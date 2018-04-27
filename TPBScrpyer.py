import logging


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
        except Exception as err:
            print(err)
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
        from datetime import timedelta

        ts = datetime.utcnow()

        # Uploaded 59 mins ago,
        regexpMatch = re.compile(
            r'(?P<mins>[0-9]{1,2}).+mins.+ago').search(uploadStr)
        if regexpMatch:
            mins = int(regexpMatch.group('mins'))
            ts = ts - timedelta(0, 60*mins, 0)

        # Uploaded Today 08:51,
        regexpMatch = re.compile(
            r'Today.+(?P<hour>[0-9]{2}):(?P<mint>[0-9]{2})').search(uploadStr)
        if regexpMatch:
            hour = int(regexpMatch.group('hour'))
            mint = int(regexpMatch.group('mint'))
            ts = ts.replace(hour=hour, minute=mint)

        # Uploaded Y-day 00:05,
        regexpMatch = re.compile(
            r'Y-day.+(?P<hour>[0-9]{2}):(?P<mint>[0-9]{2})').search(uploadStr)
        if regexpMatch:
            hour = int(regexpMatch.group('hour'))
            mint = int(regexpMatch.group('mint'))
            ts = ts.replace(hour=hour, minute=mint)
            ts = ts - timedelta(1, 0, 0)

        # Uploaded 04-25 13:08,
        regexpMatch = re.compile(
            r'(?P<month>[0-9]{2})-(?P<day>[0-9]{2}).+(?P<hour>[0-9]{2}):(?P<mint>[0-9]{2})').search(uploadStr)
        if regexpMatch:
            hour = int(regexpMatch.group('hour'))
            mint = int(regexpMatch.group('mint'))
            month = int(regexpMatch.group('month'))
            day = int(regexpMatch.group('day'))
            ts = ts.replace(hour=hour, minute=mint, month=month, day=day)

        # Uploaded 11-24 2016,
        regexpMatch = re.compile(
            r'(?P<month>[0-9]{2})-(?P<day>[0-9]{2}).+(?P<year>[0-9]{4})').search(uploadStr)
        if regexpMatch:
            year = int(regexpMatch.group('year'))
            month = int(regexpMatch.group('month'))
            day = int(regexpMatch.group('day'))
            ts = ts.replace(year=year, month=month, day=day)

        # logging.debug("{},{}".format(uploadStr, ts))

        return ts.timestamp()

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
                r'Uploaded(?P<upload>.*), Size (?P<size>[0-9\.]+.+iB)').search(desc)
            if hrefRegexpMatch:
                res['size'] = hrefRegexpMatch.group('size')
                res['ts'] = self.parseTs(hrefRegexpMatch.group('upload'))

        return res

    def scrpyTorrentList(self, url):
        import bs4
        try:
            content = self.req.getUrl(url)
        except Exception as err:
            print(err)
            raise

        # 'magnet:?xt=urn:btih:17e3c9fee45ad6e0a2a4cd4bd4e3ff4cbc380e27&dn=DivineBitches--DiB-43103+Delirious+Hunter+and+DJ+Hi+HD&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.ccc.de%3A80'
        dom = bs4.BeautifulSoup(content, "html.parser")
        resList = []
        for td in dom.select('.vertTh'):
            res = self.parseTorrent(td.parent)
            if res:
                resList.append(res)

        return resList
