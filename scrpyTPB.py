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
        total = 1
        ok = 1
        ratio = 1
        site = 0
        site_num = 0
        while True:
            mirror = self.db.getMirrors(limit=1, offset=site_num)
            if not mirror:
                break
            site_num = site_num + 1
            host = mirror[0].get('url')
            url = host + path
            torrentList = []
            # print(url)
            try:
                torrentList = self.scrpyer.scrpyTorrentList(url)
            except Exception:
                continue
            if not torrentList:
                continue

            self.db.postMirror(host, ts=True)
            site = site + 1
            res = self.db.postTorrents(torrentList)
            logging.info("{}-{}".format(url, res))
            total = total + res['total']
            ok = ok + res['ok']
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
            res = self.scrpyTPBInMirrors(path=path)
            print(res)
            ok = ok + res.get('ok')
            if res.get('ok') < minResource:
                break

        return {'ok': ok, 'page': index + 1}

    def __init__(self):
        import argparse
        import TPBScrpyer
        import tpbDB

        parser = argparse.ArgumentParser(description='scrpye Xinhuanet')
        parser.add_argument('--path', dest='path',
                            action='store', default='./')
        args = parser.parse_args()

        self.pathPrefix = args.path
        if not self.pathPrefix[len(self.pathPrefix)-1] == '/':
            self.pathPrefix = self.pathPrefix + '/'

        self.scrpyer = TPBScrpyer.ScrpyerTPB()
        self.db = tpbDB.TPBDatabase()

        logging.basicConfig(format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    def main(self):
        """[summary]
        """

        from datetime import datetime

        # pathPrefix = '/home/ylin/host_home/RenminRibaoTest/'

        logging.info("[{ts}] Scrpy into {db}".format(
            ts=datetime.now(), db=self.pathPrefix))
        logging.info("[{ts}] All processes joined. Big brother is watching you".format(
            ts=datetime.now()))

        # torrents = self.scrpyer.scrpyTorrentList(
        #     'file:///home/ylin/tpb-get/crus.html')
        # print(torrents)
        # self.updateTPBMirror()
        res = self.scrpyTPBRecent(offset=0, pageLimit=5, minResource=0)
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
