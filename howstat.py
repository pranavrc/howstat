#!/usr/bin/env python

import praw
from utils import Mapper, PlayerFinder, Prettifier
from time import sleep

def fetch_stats(request):
    init = Mapper()
    footer = "_____\n^(/u/howstat - Unofficial /r/Cricket  Statbot. Uses) " + \
            "[^Statsguru](http://stats.espncricinfo.com/ci/engine/stats/index.html)^. " + \
            "^(Check out the) [^Code!](http://github.com/pranavrc/howstat/)"

    try:
        mapped = init.map_string(request)
    except:
        return "Huh? Bad request."

    try:
        player_url = PlayerFinder(init.player_name)
    except:
        return "Sorry, the service isn't available right now."

    try:
        base_url = player_url.zero_in().replace("class=11;", "")

        if base_url[-1] == ";":
            base_url += mapped
            prettifier = Prettifier(base_url)
        else:
            return base_url
    except:
        return "Records not found."

    try:
        final = prettifier.prettify(init.class_allround)
    except:
        return "Records not found."

    return final + '\n\n' + footer


if __name__ == "__main__":
    r = praw.Reddit(user_agent = "Howstat v 1.0 by /u/pranavrc"
                                 "http://github.com/pranavrc/howstat/")
    r.login('username', 'password')
    subreddit = r.get_subreddit('howstat')
    newDealt, oldDealt = set(), set()

    while True:
        latest_comments = subreddit.get_comments()

        for comment in latest_comments:
            if "howstat" in comment.body and comment.id not in oldDealt \
               and comment.author != "howstat":
                newDealt.add(comment.id)

                try:
                    for each_line in comment.body.split('\n'):
                        if each_line.strip()[0:7] == 'howstat':
                            request = each_line.replace('howstat', '').strip()
                            response = fetch_stats(request)
                            print response
                            comment.upvote()
                            comment.reply(response)
                except IOError:
                    newDealt.remove(comment.id)

        oldDealt = newDealt
        sleep(60)
