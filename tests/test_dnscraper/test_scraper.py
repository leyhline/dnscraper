import os
import sys
import unittest

#Add module to PYTHONPATH for testing
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import dnscraper.scraper as scraper


FST_PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dn_b49_1.html")
SND_PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dn_b49_2.html")
LST_PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dn_b49_4.html")
USERLIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "dn_users.html")


class TestScraper(unittest.TestCase):
    def test_first_page_of_board(self):
        board = scraper.Board("/lifestyle/digital-world/pc-internet-smartphone_b49/")
        with open(FST_PAGE, "rb") as fd:
            next_page_url, threads = board.parse(fd.read())
        self.assertEqual(next_page_url, "/lifestyle/digital-world/pc-internet-smartphone_b49/seite-2/")
        self.assertEqual(len(threads), 30)
        titles, urls, polls = zip(*threads)
        self.assertEqual(titles[-1], "Win 7 Kennwort ändern?")
        self.assertEqual(sum(polls), 1)
        self.assertTrue(polls[-2])
        for url in urls:
            self.assertTrue(url.startswith("/lifestyle/digital-world/pc-internet-smartphone/"))

    def test_second_page_of_board(self):
        board = scraper.Board("/lifestyle/digital-world/pc-internet-smartphone_b49/")
        with open(SND_PAGE, "rb") as fd:
            next_page_url, threads = board.parse(fd.read())
        self.assertEqual(next_page_url, "/lifestyle/digital-world/pc-internet-smartphone_b49/seite-3/")
        self.assertEqual(len(threads), 30)
        titles, urls, polls = zip(*threads)
        self.assertEqual(sum(polls), 0)
        self.assertEqual(titles[15], "Internationale Telefonate")
        for url in urls:
            self.assertTrue(url.startswith("/lifestyle/digital-world/pc-internet-smartphone/"))

    def test_last_page_of_board(self):
        board = scraper.Board("/lifestyle/digital-world/pc-internet-smartphone_b49/")
        with open(LST_PAGE, "rb") as fd:
            next_page_url, threads = board.parse(fd.read())
        self.assertEqual(next_page_url, None)
        self.assertEqual(len(threads), 7)
        titles, urls, polls = zip(*threads)
        self.assertEqual(sum(polls), 0)
        for url in urls:
            self.assertTrue(url.startswith("/lifestyle/digital-world/pc-internet-smartphone/"))

    def test_parse_id(self):
        board = scraper.Board("/lifestyle/digital-world/pc-internet-smartphone_b49/")
        self.assertEqual(board.idx, 49)

    def test_userscraping(self):
        userlist = scraper.UserList()
        with open(USERLIST, "rb") as fd:
            next_page_url, users = userlist.parse(fd.read())
        self.assertEqual(next_page_url, "/memberslist.php?order=DESC&sortby=userposts&letter=&sid=&page=2")
        self.assertEqual(len(users), 30)
        voice = users[0]
        self.assertEqual(voice[0], "Voice")
        self.assertEqual(voice[1], "/mitglieder/voice_u1/")


if __name__ == '__main__':
    unittest.main()
