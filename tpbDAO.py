from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime

Base = declarative_base()


class TpbTorrent(Base):
    # 表的名字:
    __tablename__ = 'tpbtorrent'

    def __init__(self):
        pass

    # 表的结构:
    id  = Column(String, primary_key=True) 
    btih = Column(String)
    user = Column(String)
    catalog = Column(String)
    ts = Column(DateTime)
    magnet = Column(String)
    title = Column(String)
    siteid = Column(String)
    size = Column(String)

    def __str__(self) -> str:
        return "title: {}, link: {}".format(
            self.title, self.link)


class TpbMirror(Base):
    # 表的名字:
    __tablename__ = 'tpbmirror'

    def __init__(self):
        pass

    # 表的结构:
    url = Column(String, primary_key=True)
    ts = Column(DateTime)

    def __str__(self) -> str:
        return "title: {}, link: {}".format(
            self.title, self.link)