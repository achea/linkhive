#!/usr/bin/env python

import lh_reddit
import ConfigParser
import os.path, sys
#import lh_hackernews.py

""" how I would like to use this program
new reddituser1("gambit89")
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

if __name__=="__main__":
	config = ConfigParser.RawConfigParser()
	reddit_mysql_section = "reddit_mysql"
	reddit_user_section = "reddit_user"			
	# only allow one user
	# so one table in db for the user, no shared table
	if (not os.path.isfile("config.cfg")):		# has to be written by user
		# create one
		config.add_section(reddit_mysql_section)
		config.set(reddit_mysql_section,"db","lh_reddit")
		config.set(reddit_mysql_section,"passwd","")
		config.set(reddit_mysql_section,"user","")
		config.set(reddit_mysql_section,"host","localhost")

		config.add_section(reddit_user_section)
		config.set(reddit_user_section,"passwd","")
		config.set(reddit_user_section,"user","")

		# TODO add hacker news section too

		with open("config.cfg", "w") as f:
			config.write(f)

		print "Please fill out the config.cfg file, then run the program again"
		sys.exit(1)
	else:
		# check that at least have specified user and passwd
		config.read("config.cfg")
		if ((not config.has_section(reddit_mysql_section) or not config.has_option(reddit_mysql_section,"passwd") or config.get(reddit_mysql_section,"passwd") == "") or (not config.has_section(reddit_user_section) or not config.has_option(reddit_user_section,"user") or config.get(reddit_user_section,"user") == "")):
			print "Fill out config.cfg"
			sys.exit(1)

	# assume here that the config file is filled out (it has already been read)
	# not sure if I need to create a dictionary here...
	reddit_mysql = { "host" : config.get(reddit_mysql_section,"host"),
					"user" : config.get(reddit_mysql_section,"user"),
					"passwd" : config.get(reddit_mysql_section,"passwd"),
					"db" : config.get(reddit_mysql_section,"db") }
	reddit_user = { "user" : config.get(reddit_user_section,"user"),
					"passwd" : config.get(reddit_user_section, "passwd") }
	user1 = lh_reddit.RedditUser(reddit_user["user"],reddit_user["passwd"])
	user1.initdb(reddit_mysql["host"],reddit_mysql["user"],reddit_mysql["passwd"],reddit_mysql["db"])
	#print user1.getUserName(), user1.userName

