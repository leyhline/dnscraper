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
from typing import Tuple, Optional, Sequence
from urllib.parse import urljoin
import logging

import requests
import lxml.html as lhtml



# Type definitions
Url = str
NETLOC = "http://www.digitalnippon.de/"


class Board:
    idx = None
    title = None
    path = None
    threads = []

    def __init__(self, path: str):
        self.path = path
        match = re.match(r""".+/.+_b([0-9]+)""", path)
        self.idx = match.group(1)

    def scrape_threads(self):
        r = requests.get(self.url)
        next_page_url, threads = self.parse(r.content)
        r.close()

    def parse(self, page_content: bytes) -> Tuple[Optional[Url], Sequence[Tuple[str, Url, int, bool]]]:
        root = lhtml.document_fromstring(page_content)
        # Make sure there are no sticky threads from other boards parsed.
        board_path = re.match(r"""(.+)_b[0-9]+""", self.path).group(1)
        threads = tuple((elem.text, elem.attrib["href"]) for elem in root.cssselect("a.threadtitle")
                        if elem.attrib["href"].find(board_path) >= 0)
        pagelink = root.cssselect("span.smallfont.pagelink > b > a")
        try:
            next_page_url = next(elem.attrib["href"] for elem in pagelink if elem.text.startswith("nächste"))
        except StopIteration:
            next_page_url = None
        return next_page_url, threads
