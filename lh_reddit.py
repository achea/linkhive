#!/usr/bin/env python

import urllib, urllib2, cookielib
import MySQLdb

#username = 'myuser'
#password = 'mypassword'

#cj = cookielib.CookieJar()
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#login_data = urllib.urlencode({'username' : username, 'j_password' : password})
#opener.open('http://www.example.com/login.php', login_data)
#resp = opener.open('http://www.example.com/hiddenpage.php')
#print resp

class RedditUser:
	"""Fetch/update user stories liked/disliked/saved 

	Authenticates when necessary
	userName = name of the user"""

	def __init__(self,userName=None,passwd=None):
		self.ALLOWEDPAGES = ["liked","disliked","saved"]		# this is a waste of space
																# is there a way to def global?
		self.ALLOWEDCACHETYPES = ["update","max"]
		self.userName=userName
		self.passwd=passwd
		self.loginOK = False
		#self.dbOK = False
		self.db = None			#none for now (I think must be instantiated in __init__)
								# not necessarily, but then what is it's default value?
		self.cj = cookielib.CookieJar()
	
	def __del__(self):
		if self.db:
			self.db.close()

	def getUserName(self):
		return self.userName

	def initdb(self,host='localhost',user=None,passwd=None,db_name='lh_reddit'):
		"""Open a connection to the database"""

		# if successful, store the state
		self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name)
			# connect returns true even if unsuccessful according to manual?

	def cachestories(self,page_type,cache_type):
		"""Cache stories"""

		assert page_type in self.ALLOWEDPAGES
		if not isinstance(cache_type, int):			#int must also be positive
			assert cache_type in self.ALLOWEDCACHETYPES

