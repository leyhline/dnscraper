"""
dnscraper
~~~~~~~~~~~~~~~~~

Scraping the content from digitalnippon.de for archiving purposes.

:copyright: (c) 2017 Thomas Leyh
:licence: GPLv3, see LICENSE
"""


import os
from logging.config import fileConfig
if os.path.exists("logging_config.ini"):
    fileConfig("logging_config.ini")
