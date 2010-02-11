#!/usr/bin/env python

#    This file is part of Linkhive.
#    Copyright (C) 2009-2010 Andree Chea <achea89@gmail.com>
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

import sys
import time
import MySQLdb
import urllib,urllib2,cookielib
from BeautifulSoup import BeautifulSoup

class HNUser:
	def __init__(self,userName,passwd):
		self.ALLOWEDCACHETYPES = ["update","all"]
		self.userName = userName
		self.passwd = passwd
		self.cj = None
		self.opener = None

		self.sleep_time = 5
		self.debug = True

		self.db = None
		self.table_name = None
		self.query1_template = "INSERT INTO %s "
		self.query2_template = "(domain,score,link,url,title,author_href,author,comments,id) VALUES('%(domain)s',%(score)d,'%(link)s','%(url)s','%(title)s','%(author_href)s','%(author)s',%(comments)d,%(id)d) ON DUPLICATE KEY UPDATE score=VALUES(score), comments=VALUES(comments)"

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

		self.opener.addheaders = [('User-Agent', 'linkhive/0.1')]

	def initdb(self,host='localhost',user=None,passwd=None,db_name='linkhive',table_name="hn_stories"):
		"""Open a connection to the database"""

		self.table_name = table_name

		# if successful, store the state
		self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db_name, sql_mode='STRICT_ALL_TABLES')
			# connect returns true even if unsuccessful according to manual?
			# TODO check if it connected

		c = self.db.cursor()		
		query = "CREATE TABLE IF NOT EXISTS " + table_name + """
(
	domain				VARCHAR(70) CHARACTER SET utf8,
	score				INT(11) NOT NULL,
	link				VARCHAR(2000) CHARACTER SET utf8,
	url					VARCHAR(21) CHARACTER SET utf8,
	title				VARCHAR(300) CHARACTER SET utf8,
	author_href			VARCHAR(31) CHARACTER SET utf8,
	author				VARCHAR(21) CHARACTER SET utf8,
	comments			INT(11) UNSIGNED NOT NULL,
	id					INT(11) UNSIGNED NOT NULL,
	PRIMARY KEY		(id)
);
"""
		c.execute(query)

	def cache_stories(self,cache_type):
		"""Get the saved links to save going back
		
		Stops when there is no more "More" link
		Want to specify how many pages back to go
		num_requests = 0 means no limit"""

		if not isinstance(cache_type, int):			#int must also be positive
			assert cache_type in self.ALLOWEDCACHETYPES

		if self.debug:
			sys.stderr.write('fetching %s\n' % ("/saved?id=" + self.userName))

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

		temp_count = self.__save_links(story_table,count)
		# new, updated, dupes
		story_counts = [temp_count[0],temp_count[1],temp_count[2]]

		# check for max pages
		page_count = 0
		if isinstance(cache_type, int) and cache_type >= 1:
			max_pages = cache_type - 1 	# because we already saved one
		else:
			max_pages = 999		# not really, won't get here 

		# does python have do .. while ?
		while ((len(story_table)-2) % 3) == 0 and count > 0 and page_count < max_pages:		# while exists a "More" link
			#print "in loop"
			time.sleep(self.sleep_time)
			# get the next page
			next_page = story_table.contents[len(story_table)-1].contents[1].contents[0]['href']
			#print next_page
			if self.debug:
				sys.stderr.write('fetching %s\n' % next_page)
			page = self.opener.open("http://news.ycombinator.com" + next_page).read().replace("\r\n",'')
			soup = BeautifulSoup(page)
			story_table = soup.contents[0].contents[0].nextSibling.contents[0].contents[0].contents[0].nextSibling.nextSibling.contents[0].contents[0]

			if ((len(story_table)-2) % 3) == 0:
				count = (len(story_table)-2)/3
			elif (len(story_table) % 3) == 0:
				count = len(story_table)/3

			#if count == 0:
			#	print "error"

			temp_count = self.__save_links(story_table,count)
			page_count += 1
			story_counts[0] += temp_count[0]
			story_counts[1] += temp_count[1]
			story_counts[2] += temp_count[2]

			# it is tricky to say when to stop, because HN returns voted stories according to their date, so if it's 7 days old, it'll be on e.g. page 4, rather than the top of the first page
			# so you might miss it if you stop on one page of dupes
			if story_counts[2] >= 60 and temp_count[2] == 30 and cache_type == "update":
				# if the last fetch was all dupes, and already 2 pages worth (though the previous 30 could span more than one page)
				break;

		print "Saved " + str(story_counts[0]) + " new stories with " + str(story_counts[1]) + " updated stories and " + str(story_counts[2]) + " duplicate, but not updated stories."


	def __save_links(self,story_table,count):
		"""Save links to database.  Returns count of possible 'errors'

		Assume error checking is already done
		And that there will be no errors here"""
		
		assert self.table_name is not None

		c = self.db.cursor()
		story_dupes = 0
		story_new = 0
		story_updates = 0

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
				
			# odd case 3 (dead link)
			# if the link was dead, then...
			# the domain has the title
			#	so have to adjust that the 
			# the 'dead' text can go into the link (apparently, the domain is still somewhere... too lazy to navigate the soup)
			# 	it is in the title 
			title_text = stuff1.string
			try:
				story_link = stuff1['href']
			except TypeError:
				#story_link = ""
				story_link = title_text
				# move the domain to title
				title_text = domain_text
				# TODO domain is somewhere...
				domain_text = ""

			stuff3 = story_table.contents[1 + x*3].contents[1]

			# odd case 2 (0 comments)
			if stuff3.contents[4].string == "discuss":
				num_comments = 0
			else:
				num_comments = int(stuff3.contents[4].string.split(" ")[0])


			data = { 'id':			int(stuff3.contents[4]['href'].split('=')[1]),
					'title':		title_text,
					'link': 		story_link,
					'domain': 		domain_text,
					'score': 		int(stuff3.contents[0].string.split(" ")[0]),
					'author': 		stuff3.contents[2].string,
					'author_href':	stuff3.contents[2]['href'],
					'comments':		num_comments,
					'url':			stuff3.contents[4]['href'] }

			query_stuff = self.__format_mysql(data)
			status = c.execute(query_stuff[0] % query_stuff[1])
			if status == 0:
				story_dupes += 1
			elif status == 2:
				story_updates += 1
			elif status == 1:
				story_new += 1
			else:
				print "how to die?"

		return (story_new,story_updates,story_dupes)

	def __format_mysql(self,story):
		"""Given a story dictionary, return query"""

		# title and link need quotes escaping
		story2 = story
		story2['title'] = story['title'].replace('"', '\\"').replace("'", "\\'")
		story2['link'] = story['link'].replace('"', '\\"').replace("'", "\\'")

		query = (self.query1_template % self.table_name) + self.query2_template
		return [query, story2]
