#!/usr/bin/env python

import sys
import time
import MySQLdb
import urllib,urllib2,cookielib
from BeautifulSoup import BeautifulSoup

class HNUser:
	def __init__(self,userName,passwd):
		self.userName = userName
		self.passwd = passwd
		self.cj = None
		self.opener = None

		self.db = None
		self.table_name = None

	def __del__(self):
		if self.db:
			self.db.close()

	def login(self):
		# get that blasted fnid... what is it for anyway?
		hackernews_home = "http://news.ycombinator.com/"
		page = urllib2.urlopen(hackernews_home)
		soup = BeautifulSoup(page.read().replace("\r\n",''))

		login_anchor = soup.contents[0].contents[0].nextSibling.contents[0].contents[0].contents[0].contents[0].contents[0].contents[0].contents[0].nextSibling.nextSibling.contents[0].contents[0]

		time.sleep(2)
		login_url = hackernews_home[:-1] + login_anchor['href']
		page = urllib2.urlopen(login_url)
		soup = BeautifulSoup(page.read().replace("\r\n",''))

		fnid = soup.find('form',action='/y').contents[0]

		self.cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		urllib2.install_opener(self.opener)
		login_data = urllib.urlencode({'fnid': fnid['value'], 'u': self.userName, 'p': self.passwd})
		self.opener.open('http://news.ycombinator.com/y', login_data)
		time.sleep(1)

	def initdb(self,host='localhost',user=None,passwd=None,db_name='linkhive',table_name="hn_stories"):
		"""Open a connection to the database"""

		self.table_name = table_name

		# if successful, store the state
		self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name)
			# connect returns true even if unsuccessful according to manual?
			# TODO check if it connected

		c = self.db.cursor()		
		query = "CREATE TABLE IF NOT EXISTS " + table_name + """
(
	domain				VARCHAR(60) CHARACTER SET utf8,
	score				INT(11) NOT NULL,
	link				VARCHAR(2000) CHARACTER SET utf8,
	href				VARCHAR(21) CHARACTER SET utf8,
	title				VARCHAR(300) CHARACTER SET utf8,
	author_href			VARCHAR(31) CHARACTER SET utf8,
	author				VARCHAR(21) CHARACTER SET utf8,
	comments			INT(11) UNSIGNED NOT NULL,
	id					INT(11) UNSIGNED NOT NULL,
	PRIMARY KEY		(id)
);
"""
		c.execute(query)

	def cache_stories(self,num_requests = 0):
		"""Get the saved links to save going back
		
		Stops when there is no more "More" link
		Want to specify how many pages back to go
		num_requests = 0 means no limit"""

		assert self.table_name is not None

		# the initial page is different from the rest
		page = self.opener.open("http://news.ycombinator.com/saved?id=" + self.userName).read()
		soup = BeautifulSoup(page)
		story_table = soup.contents[0].contents[0].nextSibling.contents[0].contents[0].contents[0].nextSibling.nextSibling.contents[0].contents[0]

		#for x in range(len(story_table.contents)):
		#	print " --- " + str(x) + " ---"
		#	print story_table.contents[x]

		#if ((len(story_table)-2) % 3) == 0:			# we know that there is still more to go

		#assert (((len(story_table)-2) %3 ) == 0) or ((len(story_table) % 3) == 0)

		if ((len(story_table)-2) % 3) == 0:
			count = (len(story_table)-2)/3
		elif (len(story_table) % 3) == 0:
			count = len(story_table)/3

		# this check is unnecessary because range(0) is nothing
		# if count == 0:
			#print "error"

		self.__save_links(story_table,count)
		# does python have do .. while ?
		while ((len(story_table)-2) % 3) == 0 and count > 0:		# while exists a "More" link
			#print "in loop"
			time.sleep(5)
			# get the next page
			next_page = story_table.contents[len(story_table)-1].contents[1].contents[0]['href']
			#print next_page
			page = self.opener.open("http://news.ycombinator.com" + next_page).read().replace("\r\n",'')
			soup = BeautifulSoup(page)
			story_table = soup.contents[0].contents[0].nextSibling.contents[0].contents[0].contents[0].nextSibling.nextSibling.contents[0].contents[0]

			if ((len(story_table)-2) % 3) == 0:
				count = (len(story_table)-2)/3
			elif (len(story_table) % 3) == 0:
				count = len(story_table)/3

			#if count == 0:
			#	print "error"

			self.__save_links(story_table,count)
			#print count

	def __save_links(self,story_table,count):
		"""Save links to database

		Assume error checking is already done
		And that there will be no errors here"""
		for x in range(count):
			stuff1 = story_table.contents[0 + x*3].contents[2].contents[0]

			# odd case 1 (no link, like a reddit self post)
			try:
				stuff2 = story_table.contents[0 + x*3].contents[2].contents[1]
				domain_text = stuff2.string.strip().lstrip('(').rstrip(')')
			except IndexError:
				# is there a way to add attributes to any object?
				# like stuff2.string = "self"
				domain_text = "self"
				
			stuff3 = story_table.contents[1 + x*3].contents[1]

			# odd case 2 (0 comments)
			if stuff3.contents[4].string == "discuss":
				num_comments = 0
			else:
				num_comments = int(stuff3.contents[4].string.split(" ")[0])

			# odd case 3 (dead link)
			try:
				story_link = stuff1['href']
			except TypeError:
				story_link = ""

			data = { 'id':			int(stuff3.contents[4]['href'].split('=')[1]),
					'title':		stuff1.string,
					'link': 		story_link,
					'domain': 		domain_text,
					'score': 		int(stuff3.contents[0].string.split(" ")[0]),
					'author': 		stuff3.contents[2].string,
					'author_href':	stuff3.contents[2]['href'],
					'comments':		num_comments,
					'href':			stuff3.contents[4]['href'] }
			print data

