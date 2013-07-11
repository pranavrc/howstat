#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html as lh
from lxml.html.clean import Cleaner
from lxml.etree import tostring
from urllib import urlencode
import re

class Mapper:
    country_codes = {
        'afghanistan' : 40,
        'australia' : 2,
        'bangladesh' : 25,
        'bermuda' : 12,
        'england' : 1,
        'hong kong' : 19,
        'india' : 6,
        'ireland' : 29,
        'netherlands' : 15,
        'new zealand' : 5,
        'pakistan' : 7,
        'scotland' : 30,
        'south africa' : 3,
        'sri lanka' : 8,
        'west indies' : 4,
        'zimbabwe' : 9
    }

    venues = {
        'home' : 1,
        'away' : 2,
        'neutral' : 3
    }

    formats = {
        'tests' : 1,
        'odis' : 2,
        't20is' : 3,
        'all' : 11
    }

    mappings = {
        'class' : formats,
        'opposition' : country_codes,
        'host' : country_codes,
        'home_or_away' : venues,
        'year' : ''
    }

    player_name = ""
    class_allround = False

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
            param = cmds[k.lower()]

            if param == 'class':
                class_found = True

            if param == 'year':
                request_map[param] = v.lower()
            else:
                request_map[param] = self.mappings[param][v.lower()]

        if not class_found:
            request_map['class'] = 11

        if len(request_map) == 1:
            self.class_allround = True

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

    def prettify(self, allround):
        self.stat_list = self.make_list()
        list_length = len(self.stat_list)

        if allround:
            splice_length = list_length / 2
            header = self.splice_list(list_length, splice_length)
            tr = '|Overall|' + '|'.join(x for x in self.stat_list[splice_length:]) + '|'
        else:
            splice_length = list_length / 3
            header = self.splice_list(list_length, splice_length)
            tr1 = '|Unfiltered|' + '|'.join(x for x in \
                                 self.stat_list[splice_length:list_length-splice_length]) + '|'
            tr2 = '|Filtered|' + '|'.join(x for x in \
                                 self.stat_list[list_length-splice_length:list_length]) + '|'
            tr = tr1 + '\n' + tr2

        return header + tr

    def splice_list(self, list_length, splice_length):
        td = '||' + '|'.join(x for x in self.stat_list[0:splice_length]) + '|'
        delim = '|:' + '|:'.join('' for x in range(splice_length)) + '|:|:|'
        return td + '\n' + delim + '\n'

if __name__ == "__main__":
    #foo = str(raw_input())
    #bar = PlayerFinder(foo)
    #print bar
    a = Mapper()
    b = a.map_string(str(raw_input()))
    c = PlayerFinder(a.player_name)
    d = Prettifier(c.zero_in().replace("class=11;", "") + b)
    print d.prettify(a.class_allround)
