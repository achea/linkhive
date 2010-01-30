#!/usr/bin/env python

import urllib, urllib2, cookielib
import MySQLdb

import sys
import json
import time
from urllib import urlencode
import urlparse
#from urlparse import urlparse, urlunparse, parse_qs

class RedditUser:
	"""Fetch/update user stories liked/disliked/saved 

	Authenticates when necessary
	userName = name of the user"""

	def __init__(self,userName,passwd=None):
		self.ALLOWEDPAGES = ["liked","disliked","hidden","saved"]		# this is a waste of space
																# is there a way to def global?
		self.ALLOWEDCACHETYPES = ["update","max"]
		self.userName=userName
		self.passwd=passwd
		self.loginOK = False
		#self.dbOK = False
		self.db = None			#none for now (I think must be instantiated in __init__)
								# not necessarily, but then what is it's default value?

		self.cj = None
		self.opener = None

		# please don't hurt reddit
		self.fetch_size = 100     # the higher the better, but reddit ignores +100
		self.sleep_time = 3       # in seconds. how long to sleep between
								 # requests. higher is better
		self.request_limit = None # how many requests to make to reddit before
								 # stopping (set to None to disable)

		self.debug = True

		self.table_name = None		# saving to mysql can't be called before initdb
		# the full query is query1 + valid columns + VALUES(valid columns) + query2
		self.query1_template = "INSERT INTO %s "
		self.query2_template = "ON DUPLICATE KEY UPDATE clicked=VALUES(clicked), ups=VALUES(ups), downs=VALUES(downs), likes=VALUES(likes), num_comments=VALUES(num_comments), hidden=VALUES(hidden), score=VALUES(score), saved=VALUES(saved)";

	def __del__(self):
		if self.db:
			self.db.close()

	#def getUserName(self):
	#	return self.userName

	def login(self):
		# TODO add cached cookies support
		self.cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		urllib2.install_opener(self.opener)
		login_data = urllib.urlencode({'user': self.userName, 'passwd': self.passwd})
		status = self.opener.open('http://www.reddit.com/api/login/username', login_data)
		#print "status code: " + str(status.code)
		# now check if login credentials ok
		# TODO add a user agent
		status.close()

		time.sleep(2)
	
	def initdb(self,host='localhost',user=None,passwd=None,db_name='linkhive',table_name="reddit_stories"):
		"""Open a connection to the database"""

		#reddit_table_name = "reddit_stories"
		self.table_name = table_name

		# if successful, store the state
		self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name)
			# connect returns true even if unsuccessful according to manual?
			# TODO check if it connected

		c = self.db.cursor()		# local cursor?
		# media_embed_content was upgraded from 500 to 2000 because of one that was ~1600...
		# media_video_id was upgraded from 20 to 500 because of one that was ~460
		query = "CREATE TABLE IF NOT EXISTS " + table_name + """
(
	kind					VARCHAR(3) CHARACTER SET utf8,
	domain					VARCHAR(60) CHARACTER SET utf8,
	clicked					BOOL,
	name					VARCHAR(11) CHARACTER SET utf8,
	ups						INT(11) UNSIGNED NOT NULL,
	author					VARCHAR(21) CHARACTER SET utf8,
	url						VARCHAR(2000) CHARACTER SET utf8,
	media_embed_content		VARCHAR(2000) CHARACTER SET utf8,		 
	media_embed_width		INT(11) UNSIGNED,
	media_embed_scrolling	BOOL,
	media_embed_height		INT(11) UNSIGNED,
	media_video_id			VARCHAR(500) CHARACTER SET utf8,
	media_type		VARCHAR(20) CHARACTER SET utf8,
	downs			INT(11) UNSIGNED NOT NULL,
	created			FLOAT UNSIGNED NOT NULL,
	created_utc		FLOAT UNSIGNED NOT NULL,
	subreddit_id	VARCHAR(11) CHARACTER SET utf8,
	subreddit		VARCHAR(21) CHARACTER SET utf8,
	selftext		MEDIUMTEXT CHARACTER SET utf8,
	selftext_html	MEDIUMTEXT CHARACTER SET utf8,
	likes			BOOL,
	num_comments	INT(11) UNSIGNED NOT NULL,
	id				VARCHAR(11) CHARACTER SET utf8,
	title			VARCHAR(400) CHARACTER SET utf8,
	hidden			BOOL,
	over_18			BOOL,
	score			INT(11) NOT NULL,
	saved			BOOL,
	thumbnail		VARCHAR(60) CHARACTER SET utf8,
	PRIMARY KEY		(id)
);
"""
		c.execute(query)

	def get_links(self,sourceurl, requests = 0):
		'''
		Given a reddit JSON URL, yield the JSON Link API objects,
		following 'after' links
		'''
		# rip apart the URL, make sure it has .json at the end, and set
		# the limit
		scheme, host, path, params, query, fragment = urlparse.urlparse(sourceurl)

		parsed_params = urlparse.parse_qs(query) if query else {}
		parsed_params['limit'] = [self.fetch_size]
		fragment = None # erase the fragment, we don't use it
		assert path.endswith('.json') or path.endswith('/')
		if path.endswith('/'):
			path = path + '.json'

		new_urltuple = (scheme, host, path, params,
				urlencode(parsed_params, doseq = True), fragment)
		composed_sourceurl = urlparse.urlunparse(new_urltuple)

		if self.debug:
			sys.stderr.write('fetching %s\n' % composed_sourceurl)

		if (self.opener is None):	# if it was as defined by __init__
			text = urllib.urlopen(composed_sourceurl).read()
		else:
			text = self.opener.open(composed_sourceurl).read()		# for login credentials
		parsed = json.loads(text)

		# there may be multiple listings, like on a comments-page, but we
		# can only export from pages with one listing
		assert parsed['kind'] == 'Listing'

		listing = parsed['data']

		for child in listing.get('children', []):
			yield child

		if (listing.get('after', None)
				and (self.request_limit is None
					or requests < self.request_limit - 1)):
			after_parsed_params = parsed_params.copy()
			after_parsed_params['after'] = [listing['after']]
			after_urltuple = (scheme, host, path, params,
					urlencode(after_parsed_params, doseq = True),
					fragment)
			after_sourceurl = urlparse.urlunparse(after_urltuple)

			time.sleep(self.sleep_time)

			# yes, this is recursive, but if you're making enough requests
			# to blow out your stack, you're probably hurting reddit
			for link in self.get_links(after_sourceurl, requests+1):
				yield link

	def cache_stories(self,page_type,cache_type):
		'''
		Given page_type, generate a reddit JSON url and save to database 
		'''

		assert page_type in self.ALLOWEDPAGES
		if not isinstance(cache_type, int):			#int must also be positive
			assert cache_type in self.ALLOWEDCACHETYPES

		c = self.db.cursor()
		c.execute("SET sql_mode='STRICT_ALL_TABLES'")	# generate an error when can't insert

		if page_type == "saved":
			sourceurl = "http://www.reddit.com/saved.json"
		else:			# liked, disliked, hidden
			sourceurl = "http://www.reddit.com/user/" + self.userName + "/" + page_type + "/.json"

		#yield header_template % dict(exported_url = escape_html(sourceurl))
		story_count = 0
		story_errors = 0

		for link in self.get_links(sourceurl):
			if link['kind'] != 't3':
				# skip non-links. support for comments can be added later
				# if someone cares enough
				continue

			data = link['data']

			query_stuff = self.__format_mysql(data)
			status = c.execute(query_stuff[0] % query_stuff[1])
			if not status:
				story_errors += 1
				# if an update happened, the status returns false??
				#	does that mean that it updated, or is it a bug and should've returned true?
				#print "Did not save '" + data['title'] + "'"
				#print dir(status)
				#print query_stuff[0] % query_stuff[1]
				#print status
				#print c.messages
			else:
				story_count += 1

		print "Saved " + str(story_count) + " with " + str(story_errors) + " errors."

	def __format_mysql(self,story):
		"""Given a story dictionary, format the appropriate SQL"""
		
		# must have called initdb first
		assert self.table_name is not None

		#line2 = line.replace("u'",'"').rstrip().replace("'",'"').replace("False","false").replace("True","true").replace("None","null")                                            
		#story = json.loads(line3)

		# strings must be encased in quotes
		# bools must NOT be encased in quotes
		# ints don't have to be

		# many cases.  if they aren't there, then mysql defaults them to null:
		#  media is defined or not
		#  is self post or not
		#  has thumbnail or not

		# make a copy
		# that means that story2 might have more than needed; it's ignored
		story2 = story
		# convert all bools to string
		#media_embed_scrolling
		story2['likes'] = self.__bool2str(story['likes'])
		story2['saved'] = self.__bool2str(story['saved'])
		story2['clicked'] = self.__bool2str(story['clicked'])
		story2['over_18'] = self.__bool2str(story['over_18'])
		story2['hidden'] = self.__bool2str(story['hidden'])
		# maybe delete some keys, like media_embed and media ... 
		# because I can't get the dictionary/portable thing for execute to work, I'll convert manually...
		# media_embed_content, selftext_html, selftext, url, title
		story2['url'] = story['url'].replace('"', '\\"').replace("'", "\\'")
		story2['title'] = story['title'].replace('"', '\\"').replace("'", "\\'")

		query_cols = "(domain,"
		query_values = "VALUES('%(domain)s',"
		if story['media_embed'] != {}:
			query_cols += "media_embed_content,media_embed_width,media_embed_scrolling,media_embed_height,"
			query_values += "'%(media_embed_content)s',%(media_embed_width)d,%(media_embed_scrolling)s,%(media_embed_height)s,"
			story2['media_embed_content'] = story['media_embed']['content'].replace('"', '\\"').replace("'", "\\'")

			story2['media_embed_width'] = story['media_embed']['width']
			story2['media_embed_scrolling'] = self.__bool2str(story['media_embed']['scrolling'])
			story2['media_embed_height'] = story['media_embed']['height']

		# it might be possible to have self post with no text, so assume that empty selftext has at least some html
		if story['selftext_html'] is not None:
			query_cols += "selftext_html,selftext,"
			query_values += "'%(selftext_html)s','%(selftext)s',"

			story2['selftext_html'] = story['selftext_html'].replace('"', '\\"').replace("'", "\\'")
			story2['selftext'] = story['selftext'].replace('"', '\\"').replace("'", "\\'")

		query_cols += "likes,saved,id,clicked,author,"
		query_values += "%(likes)s,%(saved)s,'%(id)s',%(clicked)s,'%(author)s',"

		if story['media'] is not None:		# assume it'll give None rather than {}
			# later add check for {} as well
			# assume video_id and type
			query_cols += "media_video_id,media_type,"
			query_values += "'%(media_video_id)s','%(media_type)s',"
			story2['media_video_id'] = story['media']['video_id']
			story2['media_type'] = story['media']['type']

		query_cols += "score,over_18,hidden,"
		query_values += "%(score)d,%(over_18)s,%(hidden)s,"
		
		if story['thumbnail'] != '':
			query_cols += "thumbnail,"
			query_values += "'%(thumbnail)s',"
		
		query_cols += "subreddit_id,downs,name,created,url,title,created_utc,num_comments,ups) "
		query_values += "'%(subreddit_id)s',%(downs)d,'%(name)s',%(created).2f,'%(url)s','%(title)s',%(created_utc).2f,%(num_comments)d,%(ups)d) "

		query = (self.query1_template % self.table_name) + query_cols + query_values + self.query2_template
		
		return [query , story2]

		"""{u'domain': u'youtube.com', 
u'media_embed': {u'content': u'&lt;object width="490" height="295"&gt;&lt;param name="movie" value="http://www.youtube.com/v/dpbYEfXoA2E&amp;fs=1"&gt;&lt;/param&gt;&lt;param name="wmode" value="transparent"&gt;&lt;/param&gt;&lt;param name="allowFullScreen" value="true"&gt;&lt;/param&gt;&lt;embed src="http://www.youtube.com/v/dpbYEfXoA2E&amp;fs=1" type="application/x-shockwave-flash" wmode="transparent" allowFullScreen="true" width="480" height="295"&gt;&lt;/embed&gt;&lt;/object&gt;', u'width': 480, u'scrolling': False, u'height': 295},
u'subreddit': u'trance', 
u'selftext_html': None, 
u'selftext': u'', 
u'likes': True, 
u'saved': False, 
u'id': u'au7ry', 
u'clicked': False, 
u'author': u'sassanix', 
u'media': {u'video_id': u'dpbYEfXoA2E', u'type': u'youtube.com'}, 
u'score': 3, 
u'over_18': False, 
u'hidden': False, 
u'thumbnail': u'', 
u'subreddit_id': u't5_2qi03', 
u'downs': 0, 
u'name': u't3_au7ry', 
u'created': 1264485682.0, 
u'url': u'http://www.youtube.com/watch?v=dpbYEfXoA2E', 
u'title': u'Heatbeat - Nebula (Original Mix)', 
u'created_utc': 1264485682.0, 
u'num_comments': 0, 
u'ups': 3}"""

	def __bool2str(self,val):
		"""Given a boolean, returns a cooresponding string (mysql-style)"""

		# there's got to be a more pretty way to do this
		if val:
			return "true"
		return "false"
