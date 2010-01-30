#!/usr/bin/env python

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
		story_errors = temp_count
		story_count = count - temp_count		# total - errors
		# does python have do .. while ?
		while ((len(story_table)-2) % 3) == 0 and count > 0:		# while exists a "More" link
			#print "in loop"
			time.sleep(5)
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
			# though we have count, it is the theoretical saved
			# story_count stores the actual saved
			story_count += count - temp_count
			story_errors += temp_count

		print "Saved " + str(story_count) + " with " + str(story_errors) + " 'errors'."


	def __save_links(self,story_table,count):
		"""Save links to database.  Returns count of possible 'errors'

		Assume error checking is already done
		And that there will be no errors here"""
		
		assert self.table_name is not None

		c = self.db.cursor()
		c.execute("SET sql_mode='STRICT_ALL_TABLES'")	# generate an error when can't insert
		story_errors = 0

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
			if not status:
				story_errors += 1

		return story_errors

	def __format_mysql(self,story):
		"""Given a story dictionary, return query"""

		# title and link need quotes escaping
		story2 = story
		story2['title'] = story['title'].replace('"', '\\"').replace("'", "\\'")
		story2['link'] = story['link'].replace('"', '\\"').replace("'", "\\'")

		query = (self.query1_template % self.table_name) + self.query2_template
		return [query, story2]
