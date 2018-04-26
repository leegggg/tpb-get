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
                r'Uploaded.*, Size (?P<title>[0-9\.]+.+iB)').search(desc)
            if hrefRegexpMatch:
                res['size'] = hrefRegexpMatch.group('title')

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
