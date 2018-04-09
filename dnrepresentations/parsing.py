"""
dnscraper
Copyright (C) 2018 Thomas Leyh <thomas.leyh@mailbox.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import datetime, date, timedelta
import re
import lxml.html as lhtml


SCRAPE_DATE = date(2017, 9, 8)


class ForumPost:
    _re_author_and_date = re.compile(r"""Geschrieben von (.*) am (.*) um (.*):""")
    
    def __init__(self, element: lhtml.Element):
        self.element = element
        self.author_and_date_element = None
        
    def parse_author_and_date(self):
        if self.author_and_date_element is None:
            self.author_and_date_element = self.element.find("i")
        author_and_date_string = self.author_and_date_element.text_content()
        match = self._re_author_and_date.match(author_and_date_string)
        self.author, date, time = match.groups()
        date_and_time = date + " " + time
        if date_and_time.startswith("Heute"):
            date_and_time = datetime.strptime(date_and_time.split()[1], "%H:%M")
            self.datetime = datetime.combine(SCRAPE_DATE, date_and_time.time())
        elif date_and_time.startswith("Gestern"):
            date_and_time = datetime.strptime(date_and_time.split()[1], "%H:%M")
            self.datetime = datetime.combine(SCRAPE_DATE - timedelta(days=1), date_and_time.time())
        else:
            self.datetime = datetime.strptime(date_and_time, "%d.%m.%Y %H:%M")
    
    def clean_author_and_date(self):
        if self.author_and_date_element is None:
            self.author_and_date_element = self.element.find("i")
        self.element.remove(self.author_and_date_element)

    def clean_quotes(self):
        self._remove_class("quote")
        self._remove_class("quotecontent")
        
    def _remove_class(self, class_name: str):
        class_elements = self.element.find_class(class_name)
        for element in class_elements:
            element.getparent().remove(element)

    @property
    def xml(self):
        return lhtml.etree.tostring(self.element)
    
    @property
    def content(self):
        return self.element.text_content()
    

def construct_cleaned_post(element: lhtml.Element) -> ForumPost:
    """Automatically construct, parse and clean a ForumPost."""
    post = ForumPost(element)
    post.parse_author_and_date()
    post.clean_author_and_date()
    post.clean_quotes()
    return post


class ForumThread:
    _re_title = re.compile(r"""(.*) - Komplett \|""")
    
    def __init__(self, filename_url_or_file):
        self.path = filename_url_or_file
        self.posts = []
        self.title = ""
        
    def parse(self):
        etree = lhtml.parse(self.path)
        root = etree.getroot()
        title = root.head.find("title")
        match = self._re_title.match(title.text)
        self.title = match.group(1)
        post_elements = root.cssselect("html > body > div.normalfont")
        for element in post_elements:
            post = construct_cleaned_post(element)
            self.posts.append(post)


class Author:
    _re_name_from_title = re.compile(r"""Profil von (.*) \|""")
    _SCRAPE_DATE = date(2017, 9, 8)
    
    def __init__(self, filename_url_or_file):
        self.path = filename_url_or_file
        self.name = None
        self.gender = None
        self.birthday = None
        self.last_activity = None
        self.registered_at = None

    def parse(self):
        etree = lhtml.parse(self.path)
        root = etree.getroot()
        self._parse_name_from_title(root)
        self._parse_other_information(root)
        
    def _parse_name_from_title(self, html_root):
        title = html_root.head.find("title")
        match = self._re_name_from_title.match(title.text)
        self.name = match.group(1)
        
    def _parse_other_information(self, html_root):
        content = html_root.body.text_content()
        content_lines = [line.strip() for line in content.splitlines() if line.strip()]
        for i, line in enumerate(content_lines):
            if line == "Geschlecht:":
                self.gender = content_lines[i+1]
            elif line == "Registriert am:":
                registered_at = content_lines[i+1]
                registered_at = datetime.strptime(registered_at, "%d.%m.%Y")
                self.registered_at = registered_at.date()
            elif line == "Geburtstag:":
                birthday = content_lines[i+1]
                try:
                    birthday = datetime.strptime(birthday, "%d.%m.%Y")
                except ValueError:
                    birthday = datetime.strptime(birthday, "%d.%m.")
                self.birthday = birthday.date()
            elif line == "Letzte Aktivität:":
                last_activity = content_lines[i+1]
                if last_activity.startswith("Gestern"):
                    self.last_activity = SCRAPE_DATE - timedelta(days=1)
                elif last_activity.startswith("Heute"):
                    self.last_activity = SCRAPE_DATE
                elif last_activity.startswith("-"):
                    self.last_activity = None
                else:
                    last_activity = last_activity.split()[0]
                    last_activity = datetime.strptime(last_activity, "%d.%m.%Y")
                    self.last_activity = last_activity.date()
