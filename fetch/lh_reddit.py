#!/usr/bin/env python

#    This file is part of Linkhive.
#    Copyright (C) 2009-2010 Andree Chea <achea89@gmail.com>
#    Portions copyright (C) 2010 David King
#
#    Linkhive is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    Linkhive is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Linkhive.  If not, see <http://www.gnu.org/licenses/>.

import urllib, urllib2, cookielib
try:
	import MySQLdb
	import sqlite3
except ImportError:
	pass			# TODO check for MySQLdb loaded

import sys,os
import json
import time
from urllib import urlencode
import urlparse
#from urlparse import urlparse, urlunparse, parse_qs

class RedditUser:
	"""Fetch/update user stories liked/disliked/saved 

	Authenticates when necessary
	userName = name of the user"""

	def __init__(self,userName,passwd=None,key=None,quietness = 0):
		self.ALLOWEDPAGES = ["liked","disliked","hidden","saved"]		# this is a waste of space
																# is there a way to def global?
		self.ALLOWEDCACHETYPES = ["update","all"]
		self.userName=userName
		self.passwd=passwd
		self.quietness = quietness
		self.key = key		# if no key, should be None (not other empty things like 0 or "")
		self.loginOK = False
		#self.dbOK = False
		self.db = None			#none for now (I think must be instantiated in __init__)
								# not necessarily, but then what is it's default value?
		self.type = None		# sqlite or mysql

		self.cj = None
		self.opener = None

		# please don't hurt reddit
		self.fetch_size = 100     # the higher the better, but reddit ignores +100
		self.sleep_time = 3       # in seconds. how long to sleep between
								 # requests. higher is better
		self.request_limit = None # how many requests to make to reddit before
								 # stopping (set to None to disable)

		self.debug = False

		self.table_name = None		# saving to mysql can't be called before initdb
		# the full query is query1 + valid columns + VALUES(valid columns) + query2
		self.query1_template = "INSERT INTO %s "
		self.query2_template = "ON DUPLICATE KEY UPDATE clicked=VALUES(clicked), ups=VALUES(ups), downs=VALUES(downs), likes=VALUES(likes), num_comments=VALUES(num_comments), hidden=VALUES(hidden), score=VALUES(score), saved=VALUES(saved), selftext=VALUES(selftext), selftext_html=VALUES(selftext_html)";

	def __del__(self):
		if self.db:
			self.db.commit()		# maybe rollback...
			self.db.close()

	#def getUserName(self):
	#	return self.userName

	def login(self):
		"""Logs in to reddit

		Even if don't need to login since we have a key, still call this to set up the OpenerDirector"""
		if self.key is not None:
			self.opener = urllib2.build_opener()
		else:
			# TODO add cached cookies support
			self.cj = cookielib.CookieJar()
			self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
			urllib2.install_opener(self.opener)
			login_data = urllib.urlencode({'user': self.userName, 'passwd': self.passwd})
			status = self.opener.open('http://www.reddit.com/api/login/username', login_data)
			#print "status code: " + str(status.code)
			# now check if login credentials ok
			status.close()

			time.sleep(2)

		#globally add user agent
		self.opener.addheaders = [('User-Agent', 'linkhive/0.1')]
	
	def initdb(self,type='sqlite', host='localhost',user=None,passwd=None,db_name='linkhive',table_name="reddit_stories",config_path=""):
		"""Open a connection to the database"""

		#reddit_table_name = "reddit_stories"
		self.table_name = table_name
		self.type = type

		# if successful, store the state
		if type == "mysql":
			self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name, sql_mode='STRICT_ALL_TABLES', charset='utf8mb4')
			# connect returns true even if unsuccessful according to manual?
			# TODO check if it connected
		else:		# sqlite
			dbPath = config_path + "/" + db_name + ".db"
			self.db = sqlite3.connect(os.path.normpath(dbPath),timeout=10)

		c = self.db.cursor()		# local cursor?
		# media_embed_content was upgraded from 500 to 2000 because of one that was ~1600...
		# media_video_id was upgraded from 20 to 500 because of one that was ~460
		if type == "mysql":
			query = "CREATE TABLE IF NOT EXISTS " + table_name + """
(
	kind					VARCHAR(3) CHARACTER SET utf8,
	domain					VARCHAR(70) CHARACTER SET utf8,
	clicked					BOOL,
	name					VARCHAR(11) CHARACTER SET utf8,
	ups						INT(11) UNSIGNED NOT NULL,
	author					VARCHAR(21) CHARACTER SET utf8,
	url						VARCHAR(2000) CHARACTER SET utf8,
	permalink				VARCHAR(200) CHARACTER SET utf8,
	media_embed_content		TEXT CHARACTER SET utf8,		 
	media_embed_width		INT(11) UNSIGNED,
	media_embed_scrolling	BOOL,
	media_embed_height		INT(11) UNSIGNED,
	media_video_id			VARCHAR(600) CHARACTER SET utf8,
	media_type		VARCHAR(20) CHARACTER SET utf8,
	media_deep		VARCHAR(2000) CHARACTER SET utf8,
	media_oembed_provider_url		VARCHAR(200) CHARACTER SET utf8,
	media_oembed_provider_name		VARCHAR(21) CHARACTER SET utf8,
	media_oembed_type				VARCHAR(21) CHARACTER SET utf8,
	media_oembed_description		TEXT CHARACTER SET utf8mb4,
	media_oembed_title				VARCHAR(400) CHARACTER SET utf8,
	media_oembed_url				VARCHAR(2000) CHARACTER SET utf8,
	media_oembed_author_name		VARCHAR(27)	CHARACTER SET utf8,
	media_oembed_author_url			VARCHAR(100) CHARACTER SET utf8,
	media_oembed_height				INT(11) UNSIGNED,
	media_oembed_width				INT(11) UNSIGNED,
	media_oembed_cache_age			INT(11) UNSIGNED,
	media_oembed_version			VARCHAR(11) CHARACTER SET utf8,
	media_oembed_html				TEXT CHARACTER SET utf8,
	media_oembed_html5				VARCHAR(2000) CHARACTER SET utf8,
	media_oembed_thumbnail_width	INT(11) UNSIGNED,
	media_oembed_thumbnail_height	INT(11) UNSIGNED,
	media_oembed_thumbnail_url		VARCHAR(300) CHARACTER SET utf8,
	downs			INT(11) UNSIGNED NOT NULL,
	created			INT(11) UNSIGNED NOT NULL,
	created_utc		INT(11) UNSIGNED NOT NULL,
	subreddit_id	VARCHAR(11) CHARACTER SET utf8,
	subreddit		VARCHAR(31) CHARACTER SET utf8,
	selftext		MEDIUMTEXT CHARACTER SET utf8,
	selftext_html	MEDIUMTEXT CHARACTER SET utf8,
	is_self			BOOL,
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
		else:
			query = "CREATE TABLE IF NOT EXISTS " + table_name + """
(
	kind					VARCHAR(3),
	domain					VARCHAR(70),
	clicked					TINYINT(1),
	name					VARCHAR(11),
	ups						UNSIGNED INT(11) NOT NULL,
	author					VARCHAR(21),
	url						VARCHAR(2000),
	permalink				VARCHAR(200),
	media_embed_content		TEXT,		 
	media_embed_width		UNSIGNED INT(11),
	media_embed_scrolling	TINYINT(1),
	media_embed_height		UNSIGNED INT(11),
	media_video_id			VARCHAR(600),
	media_type		VARCHAR(20),
	media_deep		VARCHAR(2000),
	media_oembed_provider_url		VARCHAR(200),
	media_oembed_provider_name		VARCHAR(21),
	media_oembed_type				VARCHAR(21),
	media_oembed_description		TEXT,
	media_oembed_title				VARCHAR(400),
	media_oembed_url				VARCHAR(2000),
	media_oembed_author_name		VARCHAR(27),
	media_oembed_author_url			VARCHAR(100),
	media_oembed_height				UNSIGNED INT(11),
	media_oembed_width				UNSIGNED INT(11),
	media_oembed_cache_age			UNSIGNED INT(11),
	media_oembed_version			VARCHAR(11),
	media_oembed_html				TEXT,
	media_oembed_html5				VARCHAR(2000),
	media_oembed_thumbnail_width	UNSIGNED INT(11),
	media_oembed_thumbnail_height	UNSIGNED INT(11),
	media_oembed_thumbnail_url		VARCHAR(300),
	downs			UNSIGNED INT(11) NOT NULL,
	created			UNSIGNED INT(11) NOT NULL,
	created_utc		UNSIGNED INT(11) NOT NULL,
	subreddit_id	VARCHAR(11),
	subreddit		VARCHAR(31),
	selftext		MEDIUMTEXT,
	selftext_html	MEDIUMTEXT,
	is_self			TINYINT(1),
	likes			TINYINT(1),
	num_comments	UNSIGNED INT(11) NOT NULL,
	id				VARCHAR(11),
	title			VARCHAR(400),
	hidden			TINYINT(1),
	over_18			TINYINT(1),
	score			INT(11) NOT NULL,
	saved			TINYINT(1),
	thumbnail		VARCHAR(60),
	PRIMARY KEY		(id)
);
"""

		c.execute(query)
		self.db.commit()

	def get_links(self,sourceurl, requests = 0):
		'''
		Given a reddit JSON URL, yield the JSON Link API objects,
		following 'after' links

		See http://www.github.com/ketralnis/redditexporter for the original source
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

		debug_print = 'fetching %s\n' % composed_sourceurl
		if self.debug:
			sys.stderr.write(debug_print)
		elif self.quietness < 1:
			print debug_print,

		text = self.__get_page(composed_sourceurl)		# fetch page with timeout retries
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

	def __get_page(self, url, tries=5):
		"""
		Retries tries times before giving up.

		From reddit-comment-exporter by Peteris Krumins ( http://www.catonmat.net/ )
		"""

		for i in range(tries):
			try:
				if (self.opener is None):	# if it was as defined by __init__
					text = urllib.urlopen(url).read()
				else:
					text = self.opener.open(url).read()		# for login credentials

				return text 
			except KeyboardInterrupt:
				return
			except:
				print >>sys.stderr, "Failed getting %s, retrying." % url
				pass

	def cache_stories(self,page_type,cache_type):
		'''
		Given page_type, generate a reddit JSON url and save to database 
		'''

		assert page_type in self.ALLOWEDPAGES
		if not isinstance(cache_type, int):			#int must also be positive
			assert cache_type in self.ALLOWEDCACHETYPES

		c = self.db.cursor()

		if self.key is not None:
			key_string = "?feed=" + self.key + "&user=" + self.userName
		else:
			key_string = ""		# to make sure that there is something

		if page_type == "saved":
			sourceurl = "http://www.reddit.com/saved.json" + key_string
		else:			# liked, disliked, hidden
			sourceurl = "http://www.reddit.com/user/" + self.userName + "/" + page_type + "/.json" + key_string

		#yield header_template % dict(exported_url = escape_html(sourceurl))

		# the status numbers are I'm guessing the rows affected when query
		# going with these assumptions
		#   insert new = 1
		#   update with new values = 2
		#   try to update, but no new values = 0
		#      0 could also mean other things, like ... ?
		story_new = 0
		story_dupes = 0
		story_updates = 0

		for link in self.get_links(sourceurl):
			if link['kind'] != 't3':
				# skip non-links. support for comments can be added later
				# if someone cares enough
				continue

			data = link['data']

			query_stuff = self.__format_sql(data)
			if self.type == "mysql":
				status = c.execute(query_stuff[0], query_stuff[1])
				if status == 0:
					story_dupes += 1
					# if an update happened, the status returns false??
					#	does that mean that it updated, or is it a bug and should've returned true?
					#print "Did not save '" + data['title'] + "'"
					#print dir(status)
					#print query_stuff[0] % query_stuff[1]
					#print status
					#print c.messages
				elif status == 2:
					story_updates += 1
				elif status == 1:
					story_new += 1
				else:
					print "how to die?"
			else:
				# what does status mean???
				try:
					status = c.execute(query_stuff[0],query_stuff[1])
					story_new += 1
				except sqlite3.IntegrityError:
					# check if values differ for dupes check
					c.execute("SELECT clicked,ups,downs,likes,num_comments,hidden,score,saved,selftext,selftext_html FROM " + self.table_name + " WHERE id = :id",query_stuff[1])
					row = c.fetchone()			# assume only one 

					if (row[0] != query_stuff[1]['clicked'] or row[1] != query_stuff[1]['ups'] or row[2] != query_stuff[1]['downs'] or row[3] != query_stuff[1]['likes'] or row[4] != query_stuff[1]['num_comments'] or row[5] != query_stuff[1]['hidden'] or row[6] != query_stuff[1]['score'] or row[7] != query_stuff[1]['saved'] or row[8] != query_stuff[1]['selftext'] or row[9] != query_stuff[1]['selftext_html']):
						story_updates += 1
						query = "UPDATE " + self.table_name + " SET clicked=:clicked, ups=:ups, downs=:downs, likes=:likes, num_comments=:num_comments, hidden=:hidden, score=:score, saved=:saved, selftext=:selftext, selftext_html=:selftext_html WHERE id = :id "
						status = c.execute(query,query_stuff[1])
					else:
						story_dupes += 1


			if story_dupes >= 200 and cache_type == "update":		# if more than 2 full pages
				break;

		self.db.commit()
		if self.quietness < 2:
			print "Saved " + str(story_new) + " new stories with " + str(story_updates) + " updated stories and " + str(story_dupes) + " duplicate, but not updated stories."

	def __format_sql(self,story):
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

		query_cols = "(domain,"
		query_values = "VALUES(%(domain)s,"
		if story['media_embed'] != {}:
			query_cols += "media_embed_content,media_embed_width,media_embed_scrolling,media_embed_height,"
			query_values += "%(media_embed_content)s,%(media_embed_width)s,%(media_embed_scrolling)s,%(media_embed_height)s,"
			story2['media_embed_content'] = story['media_embed']['content']
			story2['media_embed_width'] = story['media_embed']['width']
			story2['media_embed_scrolling'] = story['media_embed']['scrolling']
			story2['media_embed_height'] = story['media_embed']['height']

		# it might be possible to have self post with no text, so assume that empty selftext has at least some html
		if story['selftext_html'] is not None:
			query_cols += "selftext_html,selftext,"
			query_values += "%(selftext_html)s,%(selftext)s,"

			# don't need to copy selftexts from story to story2 because story2 already has them

		query_cols += "is_self,likes,saved,id,clicked,author,"
		query_values += "%(is_self)s,%(likes)s,%(saved)s,%(id)s,%(clicked)s,%(author)s,"

		if story['media'] is not None:		# assume it'll give None rather than {}
			# later add check for {} as well
			if 'oembed' in story['media']:
				query_cols +="media_oembed_provider_url,media_oembed_provider_name,media_oembed_type,media_oembed_title,media_oembed_version,media_oembed_html,"
				query_values +="%(media_oembed_provider_url)s,%(media_oembed_provider_name)s,%(media_oembed_type)s,%(media_oembed_title)s,%(media_oembed_version)s,%(media_oembed_html)s,"
				story2['media_oembed_provider_url'] = story['media']['oembed']['provider_url']
				story2['media_oembed_provider_name'] = story['media']['oembed']['provider_name']
				story2['media_oembed_type'] = story['media']['oembed']['type']
				story2['media_oembed_title'] = story['media']['oembed']['title']
				story2['media_oembed_version'] = story['media']['oembed']['version']
				story2['media_oembed_html'] = story['media']['oembed']['html']

				if 'url' in story['media']['oembed']:		# blip.tv doesn't have url
					query_cols += "media_oembed_url,"
					query_values += "%(media_oembed_url)s,"
					story2['media_oembed_url'] = story['media']['oembed']['url']
				if 'cache_age' in story['media']['oembed']:
					query_cols += "media_oembed_cache_age,"
					query_values += "%(media_oembed_cache_age)s,"
					story2['media_oembed_cache_age'] = story['media']['oembed']['cache_age']
				if 'height' in story['media']['oembed']:		# scribd doesn't have height
					query_cols += "media_oembed_height,media_oembed_width,"
					query_values += "%(media_oembed_height)s,%(media_oembed_width)s,"
					story2['media_oembed_height'] = story['media']['oembed']['height']
					story2['media_oembed_width'] = story['media']['oembed']['width']
				if 'description' in story['media']['oembed']:
					query_cols += "media_oembed_description,"
					query_values += "%(media_oembed_description)s,"
					story2['media_oembed_description'] = story['media']['oembed']['description']
				if 'author_name' in story['media']['oembed']:
					# also assume author_url is provided there too
					query_cols += "media_oembed_author_name,"
					query_values += "%(media_oembed_author_name)s,"
					story2['media_oembed_author_name'] = story['media']['oembed']['author_name']
				if 'author_url' in story['media']['oembed']:
					query_cols += "media_oembed_author_url,"
					query_values += "%(media_oembed_author_url)s,"
					story2['media_oembed_author_url'] = story['media']['oembed']['author_url']
				if 'html5' in story['media']['oembed']:		# TED
					query_cols += "media_oembed_html5,"
					query_values += "%(media_oembed_html5)s,"
					story2['media_oembed_html5'] = story['media']['oembed']['html5']
				if 'thumbnail_url' in story['media']['oembed']:		# blip.tv doesn't have url
					query_cols += "media_oembed_thumbnail_width,media_oembed_thumbnail_height,media_oembed_thumbnail_url,"
					query_values += "%(media_oembed_thumbnail_width)s,%(media_oembed_thumbnail_height)s,%(media_oembed_thumbnail_url)s,"
					story2['media_oembed_thumbnail_width'] = story['media']['oembed']['thumbnail_width']
					story2['media_oembed_thumbnail_height'] = story['media']['oembed']['thumbnail_height']
					story2['media_oembed_thumbnail_url'] = story['media']['oembed']['thumbnail_url']

			query_cols += "media_type,"
			query_values += "%(media_type)s,"
			story2['media_type'] = story['media']['type']
			# oembed seems to have replaced video_id?
			if 'video_id' in story['media']:
				query_cols += "media_video_id,"
				query_values += "%(media_video_id)s,"
				story2['media_video_id'] = story['media']['video_id']
			if 'deep' in story['media']:
				# this field looks like a copy of url field
				# neat check if there is a video in the url 
				query_cols += "media_deep,"
				query_values += "%(media_deep)s,"
				story2['media_deep'] = story['media']['deep']

		query_cols += "score,over_18,hidden,"
		query_values += "%(score)s,%(over_18)s,%(hidden)s,"
		
		if story['thumbnail'] != '':
			query_cols += "thumbnail,"
			query_values += "%(thumbnail)s,"
		
		query_cols += "subreddit_id,subreddit,downs,permalink,name,created,url,title,created_utc,num_comments,ups) "
		query_values += "%(subreddit_id)s,%(subreddit)s,%(downs)s,%(permalink)s,%(name)s,%(created)s,%(url)s,%(title)s,%(created_utc)s,%(num_comments)s,%(ups)s) "

		if self.type == "mysql":
			query = (self.query1_template % self.table_name) + query_cols + query_values + self.query2_template
		else:
			# SQLite uses :blah instead of %(blah)s
			#	"(?<=%\()[\w^\)]+(?=\)s)" matches the column names
			# remove the %( and )s
			query_values = query_values.replace("%(",":").replace(")s","")
			query = (self.query1_template % self.table_name) + query_cols + query_values	# no self.query3_template

			# SQLite doesn't support boolean
			# but sql driver will convert
				# not really a conversion, since a bool in Python is an int

		return [query , story2]
