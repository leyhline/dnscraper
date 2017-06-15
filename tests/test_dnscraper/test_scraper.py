import os
import sys
import unittest

#Add module to PYTHONPATH for testing
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import dnscraper.scraper as scraper


FST_PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dn_b49_1.html")
SND_PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dn_b49_2.html")
LST_PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dn_b49_4.html")


class TestScraper(unittest.TestCase):
    def test_first_page_of_board(self):
        board = scraper.Board("/lifestyle/digital-world/pc-internet-smartphone_b49/")
        with open(FST_PAGE, "rb") as fd:
            next_page_url, threads = board.parse(fd.read())
        self.assertEqual(next_page_url, "/lifestyle/digital-world/pc-internet-smartphone_b49/seite-2/")
        self.assertEqual(len(threads), 30)
        titles, urls = zip(*threads)
        # The first url is a pinned thread from another board.
        for url in urls:
            self.assertTrue(url.startswith("/lifestyle/digital-world/pc-internet-smartphone/"))

    def test_second_page_of_board(self):
        board = scraper.Board("/lifestyle/digital-world/pc-internet-smartphone_b49/")
        with open(SND_PAGE, "rb") as fd:
            next_page_url, threads = board.parse(fd.read())
        self.assertEqual(next_page_url, "/lifestyle/digital-world/pc-internet-smartphone_b49/seite-3/")
        self.assertEqual(len(threads), 30)
        titles, urls = zip(*threads)
        # The first url is a pinned thread from another board.
        for url in urls:
            self.assertTrue(url.startswith("/lifestyle/digital-world/pc-internet-smartphone/"))

    def test_last_page_of_board(self):
        board = scraper.Board("/lifestyle/digital-world/pc-internet-smartphone_b49/")
        with open(LST_PAGE, "rb") as fd:
            next_page_url, threads = board.parse(fd.read())
        self.assertEqual(next_page_url, None)
        self.assertEqual(len(threads), 7)
        titles, urls = zip(*threads)
        # The first url is a pinned thread from another board.
        for url in urls:
            self.assertTrue(url.startswith("/lifestyle/digital-world/pc-internet-smartphone/"))


if __name__ == '__main__':
    unittest.main()
