"""
dnscraper.scraper
~~~~~~~~~~~~~~~~~

Using the boards.txt in the same directory to scan all included boards pagewise
for threads. If you have the threads' information (especially the url) you can
thereafter request the printing version of each thread where all posts are
included.

:copyright: (c) 2017 Thomas Leyh
:licence: GPLv3, see LICENSE
"""

import re
import typing
import logging

import requests
import lxml.html as lhtml


class Board:
    id = None
    title = None
    url = None
    threads = []

    def __init__(self, url: str):
        self.url = url

    def scrape_threads(self):
        r = requests.get(self.url)
        # TODO Parse method
        root = lhtml.document_fromstring(r.content)
        threads = [(elem.text, elem.attrib["href"]) for elem in root.cssselect("a.threadtitle")]
        pagelink = root.cssselect("span.smallfont.pagelink > b > a")
        next_page_url = next(elem.attrib["href"] for elem in pagelink if elem.text.startswith("nächste"))
        r.close()
