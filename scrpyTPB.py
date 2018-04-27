# pylint: disable-msg=C0103
import logging


class scrpyTPB():
    scrpyer = None
    db = None
    pathPrefix = ""

    def updateTPBMirror(self):
        mirrorList = self.scrpyer.scrpyTPBMirrorList()
        self.db.postMirrors(mirrorList, ts=False)

    def scrpyTPBInMirrors(self, path='/recent/0', threshold=0.3, minSite=3):
        total = 0
        ok = 0
        ratio = 1
        site = 0
        site_num = 0
        while True:
            mirror = self.db.getMirrors(limit=1, offset=site_num)
            if not mirror:
                logging.debug("No more mirrors")
                break
            site_num = site_num + 1
            host = mirror[0].get('url')
            url = host + path
            torrentList = []
            # print(url)
            try:
                torrentList = self.scrpyer.scrpyTorrentList(url)
            except Exception as err:
                logging.debug(err)
                continue

            if not torrentList:
                logging.debug("Empty torrent list form {}".format(url))
                continue

            self.db.postMirror(host, ts=True)
            site = site + 1
            res = self.db.postTorrents(torrentList)
            logging.info("{} {}".format(url, res))
            total = total + res['total']
            ok = ok + res['ok']
            if not total:
                ratio = 1
            else:
                ratio = ok / total
            if ratio < threshold and site > minSite:
                break

        return {'path': path, 'total': total, 'ok': ok, 'site': site, 'ratio': ratio}

    def scrpyTPBRecent(self, basePath='/recent/', offset=0,
                       pageLimit=10, minResource=20):
        ok = 0
        index = 0

        for index in range(pageLimit):
            path = "{:s}{:d}".format(basePath, index+offset)
            if '/user/' in basePath:
                path = "{:s}{:d}/3".format(basePath, index+offset)
            if '/browse/' in basePath:
                path = "{:s}{:d}/3".format(basePath, index+offset)
            if '/search/' in basePath:
                path = "{:s}{:d}/7//".format(basePath, index+offset)

            res = self.scrpyTPBInMirrors(path=path)
            logging.info(res)
            ok = ok + res.get('ok')
            if res.get('ok') < minResource:
                break
            # Page existe dans auchune mirror
            if res.get('site') < 1:
                break

        return {'basepath': basePath, 'ok': ok, 'page': index + 1}

    def __init__(self):
        import argparse
        import TPBScrpyer
        import tpbDB

        parser = argparse.ArgumentParser(description='scrpye TPB torrents')
        parser.add_argument('--offset', dest='offset',
                            action='store', type=int, default=0)
        parser.add_argument('--pages', dest='pages',
                            action='store', type=int, default=1)
        parser.add_argument('--min-resource', dest='minResource',
                            action='store', type=int, default=-1)
        parser.add_argument('--mirrordb', dest='mirrordb',
                            action='store', default=None)
        parser.add_argument('--torrentdb', dest='torrentdb',
                            action='store', default=None)
        parser.add_argument('--db', dest='db',
                            action='store', default='./tpb.db')
        parser.add_argument('--update-mirror', dest='updatemirror',
                            action='store_true')
        parser.add_argument('--add-mirror', dest='addmirror',
                            action='store', default=None)
        parser.add_argument('--log-level', dest='logLevel',
                            action='store', type=int, default=2)
        parser.add_argument('--path', dest='path',
                            action='store', default='/recent/')
        self.args = parser.parse_args()

        logging.basicConfig(format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', level=self.args.logLevel*10)
        logging.info("Start TPB Scrpyer by linyz")
        self.scrpyer = TPBScrpyer.ScrpyerTPB()

        mirrordb = self.args.mirrordb
        if not mirrordb:
            mirrordb = self.args.db
        logging.debug("Mirror DB: {}".format(mirrordb))

        torrentdb = self.args.torrentdb
        if not torrentdb:
            torrentdb = self.args.db
        logging.debug("Torrent DB: {}".format(torrentdb))

        self.db = tpbDB.TPBDatabase(mirrorDB=mirrordb, torrentDB=torrentdb)

    def main(self):
        """[summary]
        """

        if self.args.addmirror:
            mirror = self.args.addmirror
            logging.info("Mirror add updated from {}".format(
                mirror))
            self.db.postMirror(mirror=mirror, ts=True)
            logging.debug(self.db.getMirrors(limit=1))
            return

        if self.args.updatemirror:
            logging.info("Mirror List update from {}".format(
                self.scrpyer.proxyListUrl))
            self.updateTPBMirror()
            logging.debug(self.db.getMirrors(limit=10))
            return

        # torrents = self.scrpyer.scrpyTorrentList(
        #     'file:///home/ylin/tpb-get/crus.html')
        # print(torrents)
        logging.info(
            "Get torrents of {path} from page {offset} to page {end} tpb mirrors".format(
                path=self.args.path, offset=self.args.offset,
                end=self.args.offset+self.args.pages
            ))

        path = self.args.path
        if path and path[len(path)-1] != '/':
            path = path + '/'

        res = self.scrpyTPBRecent(
            offset=self.args.offset, pageLimit=self.args.pages,
            minResource=self.args.minResource, basePath=path)
        logging.info(res)
        # mirrorList = scrpyer.scrpyTPBMirrorList()
        # db.postMirrors(mirrorList, ts=False)
        # mirrors = db.getMirrors(limit=1, offset=100)
        # print(mirrors)
        # scrpyer.scrpyTPBMirrorList()
        # scrpyer.scrpyTurrentList('https://thepiratebay.rocks/recent/1')

        # resList = scrpyer.scrpyTorrentList('https://www.example.org/')
        # print(resList)
        return


if __name__ == '__main__':
    main = scrpyTPB()
    main.main()
    logging.info("All processes joined. Big brother is watching you")
