import logging
import tpbDAO
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
Base = declarative_base()
from tpbDAO import TpbMirror

from tpbDAO import Base

def getMirrors(engine, limit=3, offset=0):
    Session = sessionmaker(bind=engine)
    mirrors = []
    try:
        session = Session()
        from sqlalchemy.sql import exists, or_
        results = session.query(TpbMirror.url) \
            .order_by(TpbMirror.ts.desc()) \
            .offset(offset) \
            .limit(limit).all()
        session.expunge_all()
        session.commit()
        if results:
            for res in results:
                mirrors.append(res.url)
    except:
        pass

    return mirrors


def postMirror(engine, mirrorUrl, ts=False):
    Session = sessionmaker(bind=engine)
    session = Session()
    mirror = tpbDAO.TpbMirror()
    mirror.url = mirrorUrl
    mirror.ts = datetime.now()
    try:
        if ts:
            session.merge(mirror)
        else:
            session.add(mirror)
        session.commit()
    except:
        logging.warning("Skip mirror {} - {}".format(mirror.url,mirror.ts))



def postMirrors(engine, mirrorList, ts=False):
    Session = sessionmaker(bind=engine)
    session = Session()

    for mirrorUrl in mirrorList:
        mirror = tpbDAO.TpbMirror()
        mirror.url = mirrorUrl
        mirror.ts = datetime.now()
        try:
            if ts:
                session.merge(mirror)
            else:
                session.add(mirror)
            session.commit()
        except:
            logging.warning("Skip mirror {} - {}".format(mirror.url, mirror.ts))
    pass


def postTorrents(engine, torrents):
    Session = sessionmaker(bind=engine)
    session = Session()

    numWriten = 0
    for torrentDict in torrents:
        torrent = tpbDAO.TpbTorrent()
        torrent.id = torrentDict.get('id')
        torrent.btih = torrentDict.get('btih')
        torrent.user = torrentDict.get('user')
        torrent.catalog = torrentDict.get('catalog')
        torrent.ts = torrentDict.get('ts')
        torrent.magnet = torrentDict.get('magnet')
        torrent.title = torrentDict.get('title')
        torrent.siteid = torrentDict.get('siteid')
        torrent.size = torrentDict.get('size')

        try:
            session.add(torrent)
            session.commit()
            numWriten += 1
        except:
            logging.debug("Skip torrent {} ".format(torrent.title))

    numTotal = len(torrents)

    return {
        'total': numTotal,
        'ok': numWriten
    }


class ScrpyerTPB():
    """[summary]
    """
    # pylint: disable-msg=C0103
    import bs4

    proxyListUrl = 'https://raw.githubusercontent.com/proxybay/proxybay.github.io/master/index.html'
    # proxy = {'http': 'squid.hursley.ibm.com:3128'}
    proxy = None
    req = None

    def __init__(self):
        import req
        self.req = req.req(proxy=self.proxy)

    def scrpyTPBMirrorList(self, url=None):
        import bs4

        if not url:
            url = self.proxyListUrl

        try:
            content = self.req.getUrl(url)
        except:
            raise

        dom = bs4.BeautifulSoup(content, "html.parser")
        sites = []
        for siteTD in dom.select('.site > a'):
            site = siteTD.get('href')
            sites.append(site)
            sites.append("{:s}{:s}".format(site, "/?load="))

        return sites

    def parseHref(self, href, res={}):
        import re

        hrefRegexpMatch = re.compile(
            '/browse/(?P<catalog>[0-9]+[1-9])$').search(href)
        if hrefRegexpMatch:
            res['catalog'] = hrefRegexpMatch.group('catalog')

        hrefRegexpMatch = re.compile(
            '/user/(?P<user>.+)/$').search(href)
        if hrefRegexpMatch:
            res['user'] = hrefRegexpMatch.group('user')

        hrefRegexpMatch = re.compile(
            '/torrent/(?P<siteid>[0-9]+)/(?P<title>.+)$').search(href)
        if hrefRegexpMatch:
            res['siteid'] = hrefRegexpMatch.group('siteid')
            res['title'] = hrefRegexpMatch.group('title')
            if not res.get('id'):
                res['id'] = hrefRegexpMatch.group('siteid')

        hrefRegexpMatch = re.compile(
            '^magnet:.+$').search(href)
        if hrefRegexpMatch:
            magnet = hrefRegexpMatch.group(0)
            res['magnet'] = magnet
            btihRegexpMatch = re.compile(
                'btih:(?P<btih>[0-9a-fA-F]{40})').search(magnet)
            if btihRegexpMatch:
                res['btih'] = btihRegexpMatch.group('btih')
                res['id'] = btihRegexpMatch.group('btih')

        return res

    def parseTs(self, uploadStr):
        from datetime import datetime
        import re
        import math
        from datetime import timedelta

        ts = datetime.now()
        ts0 = ts

        # Uploaded 59 mins ago,
        regexpMatch = re.compile(
            r'(?P<mins>[0-9]{1,2}).+mins{0,1}.+ago').search(uploadStr)
        if regexpMatch:
            offset = datetime.now().timestamp() - datetime.utcnow().timestamp()
            mins = int(regexpMatch.group('mins'))
            ts = ts - timedelta(seconds=(60*mins+offset))

        # Uploaded Today 08:51,
        regexpMatch = re.compile(
            r'Today.*(?P<hour>[0-9]{2}):(?P<mint>[0-9]{2})').search(uploadStr)
        if regexpMatch:
            hour = int(regexpMatch.group('hour'))
            mint = int(regexpMatch.group('mint'))
            ts = ts.replace(hour=hour, minute=mint)

        # Uploaded Y-day 00:05,
        regexpMatch = re.compile(
            r'Y-day.*(?P<hour>[0-9]{2}):(?P<mint>[0-9]{2})').search(uploadStr)
        if regexpMatch:
            hour = int(regexpMatch.group('hour'))
            mint = int(regexpMatch.group('mint'))
            ts = ts.replace(hour=hour, minute=mint)
            ts = ts - timedelta(1, 0, 0)

        # Uploaded 04-25 13:08,
        regexpMatch = re.compile(
            r'(?P<month>[0-9]{2})-(?P<day>[0-9]{2}).*(?P<hour>[0-9]{2}):(?P<mint>[0-9]{2})').search(uploadStr)
        if regexpMatch:
            hour = int(regexpMatch.group('hour'))
            mint = int(regexpMatch.group('mint'))
            month = int(regexpMatch.group('month'))
            day = int(regexpMatch.group('day'))
            ts = ts.replace(hour=hour, minute=mint, month=month, day=day)

        # Uploaded 11-24 2016,
        regexpMatch = re.compile(
            r'(?P<month>[0-9]{2})-(?P<day>[0-9]{2}).*(?P<year>[0-9]{4})').search(uploadStr)
        if regexpMatch:
            year = int(regexpMatch.group('year'))
            month = int(regexpMatch.group('month'))
            day = int(regexpMatch.group('day'))
            ts = ts.replace(year=year, month=month, day=day)

        # logging.debug("{},{}".format(uploadStr, ts))
        if math.fabs(ts.timestamp() - ts0.timestamp()) < 5:
            logging.warning("Interval between ts too low may be incorrent {}. Source {}".format(
                ts.timestamp(), uploadStr))

        return ts

    def parseTorrent(self, tr):
        import uuid
        from datetime import datetime
        import re
        res = {}

        for atag in tr.select('a'):
            href = atag.get('href')
            res = self.parseHref(href, res)

        if res:
            if not res.get('id'):
                res['id'] = uuid.uuid4().hex
            if not res.get('ts'):
                res['ts'] = datetime.now().timestamp()

        descDom = tr.select('.detDesc')
        if descDom:
            desc = descDom[0].text
            hrefRegexpMatch = re.compile(
                r'Uploaded(?P<upload>.*), Size (?P<size>[0-9\.]+.+?iB)').search(desc)
            if hrefRegexpMatch:
                res['size'] = hrefRegexpMatch.group('size')
                res['ts'] = self.parseTs(hrefRegexpMatch.group('upload'))
        if not res['size']:
            logging.warning("Torrent size not fount: {}".format(tr))
        return res

    def scrpyTorrentList(self, url):
        import bs4
        logging.debug("scrpyTorrentList from {}".format(url))

        try:
            content = self.req.getUrl(url)
        except:
            raise

        # 'magnet:?xt=urn:btih:17e3c9fee45ad6e0a2a4cd4bd4e3ff4cbc380e27&dn=DivineBitches--DiB-43103+Delirious+Hunter+and+DJ+Hi+HD&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.ccc.de%3A80'
        dom = bs4.BeautifulSoup(content, "html.parser")
        resList = []
        for td in dom.select('.vertTh'):
            res = self.parseTorrent(td.parent)
            if res:
                resList.append(res)

        return resList


if __name__ == '__main__':
    scrpyer = ScrpyerTPB()
    scrpyer.scrpyTorrentList('file:./tpb.html')