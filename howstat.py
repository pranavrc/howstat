#!/usr/bin/env python

import praw
from utils import Mapper, PlayerFinder, Prettifier
from time import sleep

def fetch_stats(request):
    init = Mapper()

    try:
        mapped = init.map_string(request)
    except:
        return "Speak the language of my people, please!"

    try:
        player_url = PlayerFinder(init.player_name)
    except:
        return "Sorry, the service seems to be unavailable right now."

    try:
        base_url = player_url.zero_in().replace("class=11;", "")
    except:
        return "I couldn't find that, sorry."

    try:
        if base_url[-1] == ";":
            base_url += mapped
            prettifier = Prettifier(base_url)
        else:
            return base_url
    except:
        return base_url

    try:
        final = prettifier.prettify(init.class_allround)
    except:
        return request + ":\n\n" + "Ouch, nothing to see here, I think."

    elaborate = "Detailed Stats [here.](%s)" % base_url

    return request + ':\n\n' + final + '\n\n' + elaborate

def dealt_with(comment):
    try:
        for reply in comment.replies:
            if str(reply.author) == 'howstat':
                return True
    except:
        pass

    return False

if __name__ == "__main__":
    r = praw.Reddit(user_agent = "Howstat v 1.0 by /u/pranavrc"
                                 "http://github.com/pranavrc/howstat/")
    r.login('username', 'password')
    subreddit = r.get_subreddit('howstat')
    footer = "\n^(/u/howstat - Resident /r/Cricket  Statbot. Uses) " + \
            "[^Statsguru](http://stats.espncricinfo.com/ci/engine/stats/index.html)^. " + \
            "^(Check out the) [^code](http://github.com/pranavrc/howstat/) " + \
            "^(and the) [^HowTo!](http://redd.it/1i7lh3)"
    pending_comments = []

    while True:
        latest_comments = [cmt for cmt in subreddit.get_comments()]

        for comment in latest_comments + pending_comments:
            if "howstat" or "Howstat" in comment.body and not dealt_with(comment) \
               and str(comment.author) != "howstat":
                response = ""
                pending_comments.append(comment)
                request_limit = 1

                for each_line in comment.body.split('\n'):
                    if each_line.strip()[0:7] in ['howstat', 'Howstat']:
                        request = each_line.replace('howstat', '').strip('., ')
                        response += fetch_stats(request) + '\n\n_____\n\n'
                        request_limit += 1

                    if request_limit > 3:
                        if response:
                            response += '\n\nOnly three requests per Comment, sorry.' + \
                                    '\n\n_____\n\n'
                        break

                if response:
                    response += footer
                    try:
                        #comment.upvote()
                        comment.reply(response)
                        pending_comments.remove(comment)
                    except:
                        continue

        #sleep(60)
