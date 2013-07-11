#!/usr/bin/env python

import praw
import utils

r = praw.Reddit(user_agent = "Howstat v 1.0 by /u/pranavrc"
                             "http://github.com/pranavrc/howstat/")
r.login('username', 'password')
subreddit = r.get_subreddit('cricket')
newDealt, oldDealt = set(), set()

while True:
    latest_comments = subreddit.get_comments()

    for comment in latest_comments:
        if "agar" in comment.body and comment.id not in oldDealt:
            newDealt.add(comment.id)
            print comment.body

    oldDealt = newDealt
