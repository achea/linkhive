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
		self.ALLOWEDPAGES = ["liked","disliked","saved"]		# this is a waste of space
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

		# if successful, store the state
		self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name)
			# connect returns true even if unsuccessful according to manual?
			# TODO check if it connected

		c = self.db.cursor()		# local cursor?
		query = "CREATE TABLE IF NOT EXISTS " + table_name + """
(
	kind					VARCHAR(3) CHARACTER SET utf8,
	domain					VARCHAR(60) CHARACTER SET utf8,
	clicked					BOOL,
	name					VARCHAR(11) CHARACTER SET utf8,
	ups						INT(11) UNSIGNED NOT NULL,
	author					VARCHAR(21) CHARACTER SET utf8,
	url						VARCHAR(2000) CHARACTER SET utf8,
	media_embed_content		VARCHAR(500) CHARACTER SET utf8,		 
	media_embed_width		INT(11) UNSIGNED,
	media_embed_scrolling	BOOL,
	media_embed_height		INT(11) UNSIGNED,
	media_video_id			VARCHAR(20) CHARACTER SET utf8,
	media_video_type		VARCHAR(20) CHARACTER SET utf8,
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
	title			VARCHAR(300) CHARACTER SET utf8,
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

		sourceurl = "http://www.reddit.com/user/" + self.userName + "/" + page_type + "/.json"

		#yield header_template % dict(exported_url = escape_html(sourceurl))

		for link in self.get_links(sourceurl):
			if link['kind'] != 't3':
				# skip non-links. support for comments can be added later
				# if someone cares enough
				continue

			data = link['data']

			#query = self.__format_mysql_query(data)
			print data

