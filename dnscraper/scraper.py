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
from typing import Tuple, Optional, List
from urllib.parse import urljoin
import logging

import requests
import lxml.html as lhtml


# Type definitions
NETLOC = "http://www.digitalnippon.de/"


def make_request(url: str, retries: int=3) -> bytes:
    retry = 0
    while True:
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.HTTPError:
            if retry < retries:
                raise
            else:
                retry += 1
                continue
        return r.content


class Board:
    idx = None
    title = None
    path = None
    threads = []

    def __init__(self, path: str):
        self.path = path
        match = re.match(r""".+/.+_b([0-9]+)""", path)
        self.idx = int(match.group(1))

    def scrape_threads(self):
        content = make_request(urljoin(NETLOC, self.path))
        root = lhtml.document_fromstring(content)
        title = root.cssselect("head > title")[0].text
        match = re.match(r"""(.+) \(Seite [0-9]+\)""", title)
        if not match:
            match = re.match(r"""(.+) \| Digital Nippon""", title)
        self.title = match.group(1)
        next_page_url, threads = self.parse(content)
        while next_page_url:
            content = make_request(urljoin(NETLOC, next_page_url))
            next_page_url, more_threads = self.parse(content)
            threads.extend(more_threads)
        self.threads = threads

    def parse(self, page_content: bytes) -> Tuple[Optional[str], List[Tuple[str, str, bool]]]:
        threads = self._parse_threads(page_content)
        # Make sure there are no sticky threads from other boards parsed.
        board_path = re.match(r"""(.+)_b[0-9]+""", self.path).group(1)
        threads = list(filter(lambda x: x[1].find(board_path) >= 0, threads))
        root = lhtml.document_fromstring(page_content)
        pagelink = root.cssselect("span.smallfont.pagelink > b > a")
        try:
            next_page_url = next(elem.attrib["href"] for elem in pagelink if elem.text.startswith("nächste"))
        except StopIteration:
            next_page_url = None
        return next_page_url, threads

    @staticmethod
    def _parse_threads(page_content: bytes) -> List[Tuple[str, str, bool]]:
        root = lhtml.document_fromstring(page_content)
        threadbits = root.cssselect("tr.threadbit > td.tablea > span.normalfont")
        polls = []
        for threadbit in threadbits:
            if len(threadbit.cssselect("a.threadtitle")) != 1:
                continue
            prefix = threadbit.cssselect("span.prefix > b")
            if len(prefix) != 1:
                polls.append(False)
            elif prefix[0].text.startswith("Umfrage"):
                polls.append(True)
            else:
                polls.append(False)
        threads = ((elem.text, elem.attrib["href"]) for elem in root.cssselect("a.threadtitle"))
        thread_titles, thread_urls = zip(*threads)
        thread_tuples = list(zip(thread_titles, thread_urls, polls))
        assert len(thread_tuples) == len(polls)
        assert len(thread_tuples) == len(thread_titles)
        return thread_tuples



