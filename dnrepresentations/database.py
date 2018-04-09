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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, Integer, String, Date, Enum, DateTime, Text
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from . import Gender


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


class DbAuthor(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    gender = Column(Enum(Gender), nullable=False, default=Gender.unspecified)
    birthday = Column(Date)
    registered_at = Column(Date)
    last_activity = Column(Date)
    posts = relationship("DbForumPost", back_populates="author")

    def __repr__(self):
        return "<Author(name=%s, gender=%s, registered_at=%s)>" % (
            self.name, self.gender.name, self.registered_at.isoformat())


class DbForumThread(Base):
    __tablename__ = "thread"

    id = Column(Integer, primary_key=True)
    posts = relationship("DbForumPost", backref="thread")
    title = Column(String)
    board_id = Column(Integer, ForeignKey("board.id"))

    def __repr__(self):
        return "<Thread (title=%s)>" % self.title


class DbForumPost(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey(DbForumThread.id))
    author_id = Column(Integer, ForeignKey(DbAuthor.id))
    author = relationship("DbAuthor", back_populates="posts")
    xml = Column(Text)
    created_at = Column(DateTime)

    def __repr__(self):
        return "<Post (created_at=%s)>" % self.created_at


class DbForumBoard(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True, nullable=False)
    parent = Column(Integer, ForeignKey("board.id"))
    threads = relationship("DbForumThread", backref="board")

    def __repr__(self):
        return "<Post (path=%s)>" % self.path
