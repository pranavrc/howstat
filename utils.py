#!/usr/bin/env python
# Helper modules for howstat.
# Pranav Ravichandran <me@onloop.net>

import lxml.html as lh
from lxml.html.clean import Cleaner
from lxml.etree import tostring
from urllib import urlencode
import re

class Mapper:
    ''' Contains mappings and a helper
    to map input request to an URL. '''
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
        'all' : 11,
        'test' : 1,
        'odi' : 2,
        't20i' : 3,
        't20' : 3
    }

    mappings = {
        'class' : formats,
        'opposition' : country_codes,
        'host' : country_codes,
        'home_or_away' : venues,
        'year' : '',
        'spanmin1' : '',
        'spanmax1' : ''
    }

    player_name = ""
    class_allround = False

    def map_string(self, request):
        ''' Maps input request to an URL. '''
        cmds = {
            'vs' : 'opposition',
            'against' : 'opposition',
            'in' : 'host',
            'venue' : 'host',
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
                if '-' in v:
                    min_year, max_year = v.split('-')

                    if len(min_year.split()) > 2:
                        request_map['spanmin1'] = re.sub(' +', ' ', min_year).strip().replace(' ', '+')
                    elif len(min_year.split()) == 2:
                        request_map['spanmin1'] = '1+' + re.sub(' +', ' ', min_year).strip().replace(' ', '+')
                    else:
                        request_map['spanmin1'] = '1+Jan+' + min_year.strip().replace(' ', '+')

                    if len(max_year.split()) > 2:
                        request_map['spanmax1'] = re.sub(' +', ' ', max_year).strip().replace(' ', '+')
                    elif len(max_year.split()) == 2:
                        request_map['spanmax1'] = '28+' + re.sub(' +', ' ', max_year).strip().replace(' ', '+')
                    else:
                        request_map['spanmax1'] = '28+Dec+' + max_year.strip().replace(' ', '+')


                    request_map['spanval1'] = 'span'
                else:
                    request_map[param] = v.lower()
            else:
                request_map[param] = self.mappings[param][v.lower()]

        if not class_found:
            request_map['class'] = 11

        if len(request_map) == 1:
            self.class_allround = True

        request_url = urlencode(request_map).replace("&", ";").replace("%2B", "+")
        return request_url

class PlayerFinder:
    ''' Takes a player's name and returns his/her
    relevant stats url in Statsguru. '''
    base_url = "http://stats.espncricinfo.com"
    def __init__(self, player_name):
        self.player_name = player_name
        self.response = ""
        self.test_player = False

    def zero_in(self):
        ''' Returns the statistics URL of a player. '''
        stats_url = self.base_url + \
                "/stats/engine/stats/analysis.html?search=" + \
                self.player_name.replace(" ", "+") + ";template=analysis"
        document = lh.parse(stats_url)
        entries = document.xpath('//a[contains(text(), "Combined Test, ODI and T20I player")]')

        if not entries:
            entries = document.xpath('//a[text() = "Test matches player"]')
            if entries:
                self.test_player = True

        players = document.findall("//span[@style='white-space: nowrap']")

        if len(entries) > 1:
            self.response = []
            for player in players:
                player_text = player.text
                if player_text[0] != "(" and player_text[-1] != ")":
                    self.response.append(player_text)
            self.response = "Huh? " + " or ".join(self.response) + "?"
        elif len(entries) == 0:
            self.response = "I...couldn't find that."
        else:
            self.response = self.base_url + entries[0].get('href') + ';template=results;'

        return self.response

class Prettifier:
    ''' Helper functions to prettify scraped statistics data. '''
    target_url = ""
    def __init__(self, target_url, tests_only):
        self.target_url = target_url
        self.stat_list = []
        self.tests_only = tests_only

    def make_list(self):
        ''' Makes a list of all relevant statistics values. '''
        if self.tests_only:
            self.target_url = self.target_url.replace("class=11", "class=1")

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
        ''' Formats a statistics list into a reddit comment. '''
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
        ''' Splits a list based on different categories. '''
        td = '||' + '|'.join(x for x in self.stat_list[0:splice_length]) + '|'
        delim = '|:' + '|:'.join('' for x in range(splice_length)) + '|:|:|'
        return td + '\n' + delim + '\n'

if __name__ == "__main__":
    a = Mapper()
    b = a.map_string(str(raw_input()))
    c = PlayerFinder(a.player_name)
    f = c.zero_in()
    if not c.test_player:
        d = f.replace("class=11;", "")
    else:
        d = f.replace("class=1;", "")
    e = Prettifier(d + b, c.test_player)
    print e.prettify(a.class_allround)
