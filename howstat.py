#!/usr/bin/env python
# Main howstat module.
# Resident /r/Cricket Stats generator.
# Pranav Ravichandran <me@onloop.net>

import praw
from utils import Mapper, PlayerFinder, Prettifier
from time import sleep

# Get the stats from the utils module helpers.
# Creates a response based on the data received.
def fetch_stats(request):
    # Create a mapper instance
    init = Mapper()

    # Create an URL mapping using the input request.
    try:
        mapped = init.map_string(request)
    except:
        return "Speak the language of my people, please!"

    # Find the player using the player name in the request.
    try:
        player_url = PlayerFinder(init.player_name)
    except:
        return "Sorry, the service seems to be unavailable right now."

    # Scrape and parse the statistics for the corresponding player.
    try:
        zeroed_in = player_url.zero_in()
        if not player_url.test_player:
            base_url = zeroed_in.replace("class=11;", "")
        else:
            base_url = zeroed_in.replace("class=1;", "")
    except:
        return "I couldn't find that, sorry."

    # Create a Prettifier instance if it's a valid stats url.
    try:
        if base_url[-1] == ";":
            base_url += mapped
            prettifier = Prettifier(base_url, player_url.test_player)
        else:
            return base_url
    except:
        return base_url

    # Format the content for a reddit comment.
    try:
        final = prettifier.prettify(init.class_allround)
    except:
        return request + ":\n\n" + "Ouch, nothing to see here, I think. " + \
                "You can check out the [records](%s)." % base_url

    # Url for complete stats.
    elaborate = "Detailed Stats [here.](%s)" % base_url

    return request + ':\n\n' + final + '\n\n' + elaborate

# Check if howstat has already replied to the comment.
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
    subreddit = r.get_subreddit('cricket')
    footer = "\n^(/u/howstat - Resident /r/Cricket  Statbot. Uses) " + \
            "[^Statsguru](http://stats.espncricinfo.com/ci/engine/stats/index.html)^. " + \
            "^(Check out the) [^code](http://github.com/pranavrc/howstat/) " + \
            "^(and the) [^HowTo!](http://redd.it/1i7lh3)"
    #pending_comments = []

    while True:
        # Get the latest comments from /r/cricket.
        latest_comments = [cmt for cmt in subreddit.get_comments()]

        for comment in latest_comments:
            if any(x in comment.body for x in ['howstat', 'Howstat']) \
               and not dealt_with(comment) \
               and str(comment.author) != "howstat":
                response = ""
                #pending_comments.append(comment)
                request_limit = 1

                for each_line in comment.body.split('\n'):
                    if each_line.strip()[0:7] in ['howstat', 'Howstat']:
                        if request_limit <= 3:
                            pass
                        else:
                            # More than 3 requests in one comment.
                            response += '\n\nOnly three requests per Comment, sorry.' + \
                                    '\n\n_____\n\n'
                            break

                        request = each_line.replace('howstat', '').\
                                replace('Howstat','').strip('., ')
                        response += fetch_stats(request) + '\n\n_____\n\n'
                        request_limit += 1

                if response:
                    response += footer
                    try:
                        #comment.upvote()
                        comment.reply(response)
                        #pending_comments.remove(comment)
                    except:
                        continue

        #sleep(60)
