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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date, Enum, DateTime, Text
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from . import Gender


SCRAPE_DATE = date(2017, 9, 8)
Base = declarative_base()


class Database:
    def __init__(self, engine_url="sqlite:///:memory:", echo=False):
        self.engine = create_engine(engine_url, echo=echo)
        self._Session = sessionmaker(bind=self.engine)

    def create_all(self):
        Base.metadata.create_all(self.engine)

    def delete_all(self):
        Base.metadata.delete_all(self.engine)

    def get_session(self):
        return self._Session()


class ForumPost(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("thread.id"))
    author_id = Column(Integer, ForeignKey("author.id"))
    xml = Column(Text)
    created_at = Column(DateTime)

    def __repr__(self):
        return "<Post (created_at=%s)>" % self.created_at

    _re_author_and_date = re.compile(r"""Geschrieben von (.*) am (.*) um (.*):""")
    
    def __init__(self, element: lhtml.Element):
        self.element = element
        self.author_and_date_element = None
        
    def parse_author_and_date(self):
        self.xml = lhtml.etree.tostring(self.element)
        if self.author_and_date_element is None:
            self.author_and_date_element = self.element.find("i")
        author_and_date_string = self.author_and_date_element.text_content()
        match = self._re_author_and_date.match(author_and_date_string)
        author, date, time = match.groups()
        self.author_string = author
        date_and_time = date + " " + time
        if date_and_time.startswith("Heute"):
            date_and_time = datetime.strptime(date_and_time.split()[1], "%H:%M")
            self.created_at = datetime.combine(SCRAPE_DATE, date_and_time.time())
        elif date_and_time.startswith("Gestern"):
            date_and_time = datetime.strptime(date_and_time.split()[1], "%H:%M")
            self.created_at = datetime.combine(SCRAPE_DATE - timedelta(days=1), date_and_time.time())
        else:
            self.created_at = datetime.strptime(date_and_time, "%d.%m.%Y %H:%M")
    
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
    def content(self):
        return self.element.text_content()


class ForumThread(Base):
    __tablename__ = "thread"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    board_id = Column(Integer, ForeignKey("board.id"))

    def __repr__(self):
        return "<Thread (title=%s)>" % self.title

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
            post = ForumPost(element)
            post.parse_author_and_date()
            post.clean_author_and_date()
            self.posts.append(post)


class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    gender = Column(Enum(Gender), nullable=False, default=Gender.unspecified)
    birthday = Column(Date)
    registered_at = Column(Date)
    last_activity = Column(Date)

    def __repr__(self):
        return "<Author(name=%s, gender=%s, registered_at=%s)>" % (
            self.name, self.gender.name, self.registered_at.isoformat())

    _re_name_from_title = re.compile(r"""Profil von (.*) \|""")
    _SCRAPE_DATE = date(2017, 9, 8)
    
    def __init__(self, filename_url_or_file):
        self.path = filename_url_or_file
        self.name = None
        self.gender = Gender.unspecified
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
                self.gender = self._string_to_gender(content_lines[i+1])
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

    @staticmethod
    def _string_to_gender(string):
        if string == "männlich":
            return Gender.male
        elif string == "weiblich":
            return Gender.female
        else:
            return Gender.unspecified


class ForumBoard(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("board.id"))

    def __repr__(self):
        return "<Post (path=%s)>" % self.path
