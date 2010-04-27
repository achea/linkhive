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

import lh_reddit,lh_hackernews
import ConfigParser
from optparse import OptionParser
import os.path, sys, stat

""" how I would like to use this program
new reddituser1("username")
reddituser1.initdb(host,user,pass,db,tablename)
if reddituser1.loginok()
reddituser1.cachestories("liked/disliked/saved",update|1000|max)
	update mode is only until 100 stories duped
	    dupes is after one full page is the same, i.e. 100 stories
	max is 1000
	allow to set specific # of stories
	if fetching error
		stop and show the error
			the fix might be to edit the source, rather than to simply try again
				after edit the source, then we can try again
			eventually, we won't have any fetching errors
			some errors might be try again
				like network pingout
am I to provide a function to fetch but not save?
reddituser1.getstories"""

def read_args():
	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage, version="linkhive v0.1 by Andree Chea")
	#parser.add_option("-h", "--help"
	parser.add_option("-q", "--quiet",
				action="count", dest="quietness",
				help="decrease output verbosity (maximum qq)")
	parser.add_option("--reddit",
				action="store_true", dest="reddit", default=False,
				help="fetch stories from reddit")
	parser.add_option("--hackernews",
				action="store_true", dest="hackernews", default=False,
				help="fetch stories from Hacker News")
	parser.add_option("--reddit-fetch",
				action="store", type="string", dest="reddit_fetch", default="update",
				help="type of fetch to perform (update|all) default: update")
	parser.add_option("--hackernews-fetch",
				action="store", type="string", dest="hackernews_fetch", default="update",
				help="type of fetch to perform (update|all|xx) default: update")
	parser.add_option("--reddit-page",
				action="store", type="string", dest="reddit_page", default="liked",
				help="which reddit page to fetch (liked|saved|disliked|hidden) default: liked")

	(options, args) = parser.parse_args()	#parse the argments (default sys.argv[1:])s

	if len(args) > 0:
		print "Extra %d option(s) ignored ... " % len(args)

	return options

if __name__=="__main__":
	configFile = "linkhive.cfg"
	config = ConfigParser.RawConfigParser()
	reddit_mysql_section = "reddit_mysql"
	reddit_user_section = "reddit_user"			
	hn_mysql_section = "hn_mysql"
	hn_user_section = "hn_user"			

	#if len(sys.argv) == 1:
		# no options, so check config file

	# only allow one user
	# so one table in db for the user, no shared table
	if (not os.path.isfile(configFile)):		# has to be written by user
		# create one
		config.add_section(reddit_mysql_section)
		config.set(reddit_mysql_section,"db","linkhive")
		config.set(reddit_mysql_section,"passwd","")
		config.set(reddit_mysql_section,"user","")
		config.set(reddit_mysql_section,"host","localhost")

		config.add_section(reddit_user_section)
		config.set(reddit_user_section,"passwd","")
		config.set(reddit_user_section,"user","")
		config.set(reddit_user_section,"key","")

		# hacker news section 
		config.add_section(hn_mysql_section)
		config.set(hn_mysql_section,"db","linkhive")
		config.set(hn_mysql_section,"passwd","")
		config.set(hn_mysql_section,"user","")
		config.set(hn_mysql_section,"host","localhost")

		config.add_section(hn_user_section)
		config.set(hn_user_section,"passwd","")
		config.set(hn_user_section,"user","")

		with open(configFile, "w") as f:
			config.write(f)

		f.close()
		os.chmod(configFile, stat.S_IRUSR | stat.S_IWUSR);		# u+rw

		print "Blank %s file written" % configFile
		sys.exit(0)
	else:
		config.read(configFile)

	options = read_args()

	if options.reddit:
		if config.has_option(reddit_user_section,"key") and config.get(reddit_user_section,"key") != "":
			has_reddit_key = True
		else:
			has_reddit_key = False
		# check that at least have specified user and passwd
		# allow mysql user with no password
		if not has_reddit_key and ((not config.has_section(reddit_mysql_section) or not config.has_option(reddit_mysql_section,"user") or config.get(reddit_mysql_section,"user") == "") or (not config.has_section(reddit_user_section) or not config.has_option(reddit_user_section,"user") or config.get(reddit_user_section,"user") == "")):
			print "Fill out %s..." % configFile
			sys.exit(1)
		# assume here that the config file is filled out (it has already been read)
		reddit_mysql = { "host" : config.get(reddit_mysql_section,"host"),
						"user" : config.get(reddit_mysql_section,"user"),
						"passwd" : config.get(reddit_mysql_section,"passwd"),
						"db" : config.get(reddit_mysql_section,"db") }
		reddit_user = { "user" : config.get(reddit_user_section,"user"),
						"passwd" : config.get(reddit_user_section, "passwd") }
		if has_reddit_key:
			reddit_user["key"] =  config.get(reddit_user_section, "key")

	# same check for hacker news
	if options.hackernews:
		if ((not config.has_section(hn_mysql_section) or not config.has_option(hn_mysql_section,"user") or config.get(hn_mysql_section,"user") == "") or (not config.has_section(hn_user_section) or not config.has_option(hn_user_section,"user") or config.get(hn_user_section,"user") == "")):
			print "Fill out %s..." % configFile
			sys.exit(1)
		# not sure if I need to create a dictionary here...
		hn_mysql = { "host" : config.get(hn_mysql_section,"host"),
					"user" : config.get(hn_mysql_section,"user"),
					"passwd" : config.get(hn_mysql_section,"passwd"),
					"db" : config.get(hn_mysql_section,"db") }
		hn_user = { "user" : config.get(hn_user_section,"user"),
					"passwd" : config.get(hn_user_section, "passwd") }

	if options.reddit:
		try:
			# where is the scope of reddit_page ?
			reddit_fetch = int(options.reddit_fetch)
		except ValueError:
			if options.reddit_fetch == "all":
				reddit_fetch = 10
			else:
				# RedditUser asserts will take care of the other cases
				reddit_fetch = options.reddit_fetch

		#print options.reddit_page,reddit_fetch,dir(reddit_fetch)
		#sys.exit(0)
		if has_reddit_key:
			user1 = lh_reddit.RedditUser(reddit_user["user"],None,reddit_user["key"], quietness = options.quietness)
		else:
			user1 = lh_reddit.RedditUser(reddit_user["user"],reddit_user["passwd"], quietness = options.quietness)
		user1.initdb(reddit_mysql["host"],reddit_mysql["user"],reddit_mysql["passwd"],reddit_mysql["db"])
		user1.login()
		# options.reddit_page has values liked, saved, etc..
		# options.reddit_fetch has values update, all, xx
		# pagetype == options.reddit_page, cachetype == options.reddit_fetch
		user1.cache_stories(options.reddit_page,reddit_fetch)
		del user1

	if options.hackernews:
		try:
			hackernews_fetch = int(options.hackernews_fetch)
		except ValueError:
			if options.hackernews_fetch == "all":
				hackernews_fetch = 9999999
					# current id is ~1,300,000, and supposing each id is a story and 30 stories per page, approx ~43,000 pages.  9,999,999 pages is 'future-safe'  
			else:
				# asserts handle the rest
				hackernews_fetch = options.hackernews_fetch

		user1 = lh_hackernews.HNUser(hn_user["user"],hn_user["passwd"],quietness = options.quietness)
		user1.initdb(hn_mysql["host"],hn_mysql["user"],hn_mysql["passwd"],hn_mysql["db"])
		user1.login()
		user1.cache_stories(hackernews_fetch)
		del user1

