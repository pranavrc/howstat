#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html as lh
from lxml.html.clean import Cleaner
from lxml.etree import tostring
from urllib import urlencode
import re

#foo = lh.parse('http://stats.espncricinfo.com/stats/engine/player/45789.html?class=11;type=allround;template=results')
#foo = foo.xpath("//tr[contains(@class, 'data1')]")

class Mapper:
    country_codes = {
        'Afghanistan' : 40,
        'Australia' : 2,
        'Bangladesh' : 25,
        'Bermuda' : 12,
        'England' : 1,
        'Hong Kong' : 19,
        'India' : 6,
        'Ireland' : 29,
        'Netherlands' : 15,
        'New Zealand' : 5,
        'Pakistan' : 7,
        'Scotland' : 30,
        'South Africa' : 3,
        'Sri Lanka' : 8,
        'West Indies' : 4,
        'Zimbabwe' : 9
    }

    venues = {
        'Home' : 1,
        'Away' : 2,
        'Neutral' : 3
    }

    formats = {
        'Tests' : 1,
        'ODIs' : 2,
        'T20Is' : 3,
        'All' : 11
    }

    mappings = {
        'class' : formats,
        'opposition' : country_codes,
        'host' : country_codes,
        'home_or_away' : venues,
        'year' : ''
    }

    player_name = ""

    def map_string(self, request):
        cmds = {
            'vs' : 'opposition',
            'in' : 'host',
            'at' : 'home_or_away',
            'format' : 'class',
            'year' : 'year'
        }

        queries = request.split(",")
        request_map = {}
        self.player_name = queries[0]
        class_found = False

        for query in queries[1:]:
            k, v = query.split(None, 1)
            param = cmds[k]

            if param == 'class':
                class_found = True

            if param == 'year':
                request_map[param] = v
            else:
                request_map[param] = self.mappings[param][v]

        if not class_found:
            request_map['class'] = 11

        request_url = urlencode(request_map).replace("&", ";")
        return request_url

class PlayerFinder:
    base_url = "http://stats.espncricinfo.com"
    def __init__(self, player_name):
        self.player_name = player_name
        self.response = ""

    def zero_in(self):
        stats_url = self.base_url + \
                "/stats/engine/stats/analysis.html?search=" + \
                self.player_name.replace(" ", "+") + ";template=analysis"
        document = lh.parse(stats_url)
        entries = document.xpath('//a[contains(text(), "Combined Test, ODI and T20I player")]')
        players = document.findall("//span[@style='white-space: nowrap']")

        if len(entries) > 1:
            self.response = []
            for player in players:
                player_text = player.text
                if player_text[0] != "(" and player_text[-1] != ")":
                    self.response.append(player_text)
            self.response = "Huh? " + " or ".join(self.response) + "?"
        elif len(entries) == 0:
            self.response = "Not found."
        else:
            self.response = self.base_url + entries[0].get('href') + ';template=results;'

        return self.response

class Prettifier:
    target_url = ""
    def __init__(self, target_url):
        self.target_url = target_url
        self.stat_list = []

    def make_list(self):
        document = lh.parse(self.target_url)
        child_element = document.xpath('.//caption[contains(text(), "Career averages")]')
        target_element = child_element[0].getparent()
        cleaner = Cleaner(page_structure = True, allow_tags = [''], remove_unknown_tags = False)
        element_text = tostring(cleaner.clean_html(target_element))
        element_list = [x.strip() for x in re.split('\n', element_text) \
                        if x.strip() not in ['Career averages', '', 'Profile', \
                                            'unfiltered', 'overall', 'filtered']][1:-1]
        return element_list

if __name__ == "__main__":
    #foo = str(raw_input())
    #bar = PlayerFinder(foo)
    #print bar
    a = Mapper()
    b = a.map_string(str(raw_input()))
    c = PlayerFinder(a.player_name)
    d = Prettifier(c.zero_in().replace("class=11;", "") + b)
    print d.make_list()
