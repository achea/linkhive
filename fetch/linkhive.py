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
import os, sys, stat

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

def read_args(user_defaults):
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

	# use defaults if no options specified on command-line
	(options, args) = parser.parse_args(user_defaults if len(sys.argv[1:]) == 0 else sys.argv[1:])	#parse the argments (default sys.argv[1:])s

	if len(args) > 0:
		print "Extra %d option(s) ignored ... " % len(args)

	return options

if __name__=="__main__":
	configFilePath = os.path.expanduser("~") + "/.linkhive"
	configFilePath = os.path.normpath(configFilePath)
	if (not os.path.isdir(configFilePath)):
		os.mkdir(configFilePath, stat.S_IRWXU)
	configFile = configFilePath + "/linkhive.cfg"
	configFile = os.path.normpath(configFile)

	config = ConfigParser.RawConfigParser()
	lh_section = "linkhive"
	reddit_sql_section = "reddit_sql"
	reddit_user_section = "reddit_user"	
	hn_sql_section = "hn_sql"
	hn_user_section = "hn_user"			

	#if len(sys.argv) == 1:
		# no options, so check config file

	# only allow one user
	# so one table in db for the user, no shared table
	if (not os.path.isfile(configFile)):		# has to be written by user
		# create one
		config.add_section(lh_section)
		config.set(lh_section,"defaults","")

		config.add_section(reddit_sql_section)
		config.set(reddit_sql_section,"db","linkhive")
		config.set(reddit_sql_section,"passwd","")
		config.set(reddit_sql_section,"user","")
		config.set(reddit_sql_section,"host","localhost")
		config.set(reddit_sql_section,"type","")

		config.add_section(reddit_user_section)
		config.set(reddit_user_section,"passwd","")
		config.set(reddit_user_section,"user","")
		config.set(reddit_user_section,"key","")

		# hacker news section 
		config.add_section(hn_sql_section)
		config.set(hn_sql_section,"db","linkhive")
		config.set(hn_sql_section,"passwd","")
		config.set(hn_sql_section,"user","")
		config.set(hn_sql_section,"host","localhost")
		config.set(hn_sql_section,"type","")

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

	# read default string and split on spaces (to match how sys.argv splits options)
	options = read_args(user_defaults = config.get(lh_section,"defaults").split(" ") if config.has_section(lh_section) else [])

	if options.reddit:
		if config.has_option(reddit_user_section,"key") and config.get(reddit_user_section,"key") != "":
			has_reddit_key = True
		else:
			has_reddit_key = False
		# need db and type, at least
		if ((not config.has_section(reddit_sql_section) or not config.has_option(reddit_sql_section,"db") or config.get(reddit_sql_section,"db") == "" or not config.has_option(reddit_sql_section,"type") or config.get(reddit_sql_section,"type") == "") or (not config.has_section(reddit_user_section) or not config.has_option(reddit_user_section,"user") or config.get(reddit_user_section,"user") == "")):
			print "Fill out %s..." % configFile
			sys.exit(1)
		# assume here that the config file is filled out (it has already been read)
		reddit_sql = { "host" : config.get(reddit_sql_section,"host"),
						"user" : config.get(reddit_sql_section,"user"),
						"passwd" : config.get(reddit_sql_section,"passwd"),
						"db" : config.get(reddit_sql_section,"db"),
						"type" : config.get(reddit_sql_section,"type") }
		reddit_user = { "user" : config.get(reddit_user_section,"user"),
						"passwd" : config.get(reddit_user_section, "passwd") }
		if has_reddit_key:
			reddit_user["key"] =  config.get(reddit_user_section, "key")

	# same check for hacker news
	if options.hackernews:
		if ((not config.has_section(hn_sql_section) or not config.has_option(hn_sql_section,"db") or config.get(hn_sql_section,"db") == "" or not config.has_section(hn_user_section) or not config.has_option(hn_sql_section,"type") or config.get(hn_sql_section,"type") == "") or (not config.has_section(hn_user_section) or not config.has_option(hn_user_section,"user") or config.get(hn_user_section,"user") == "")):
			print "Fill out %s..." % configFile
			sys.exit(1)
		# not sure if I need to create a dictionary here...
		hn_sql = { "host" : config.get(hn_sql_section,"host"),
					"user" : config.get(hn_sql_section,"user"),
					"passwd" : config.get(hn_sql_section,"passwd"),
					"db" : config.get(hn_sql_section,"db"),
					"type" : config.get(hn_sql_section,"type") }
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
		# SQLite requires only type and db, doesn't matter what values the others hold
		user1.initdb(reddit_sql["type"], reddit_sql["host"],reddit_sql["user"],reddit_sql["passwd"],reddit_sql["db"],config_path=configFilePath)
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
		user1.initdb(hn_sql["type"], hn_sql["host"],hn_sql["user"],hn_sql["passwd"],hn_sql["db"],config_path=configFilePath)
		user1.login()
		user1.cache_stories(hackernews_fetch)
		del user1

