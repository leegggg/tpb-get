# pylint: disable-msg=C0103
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import tpbDAO
import TPBScrpyer
from datetime import datetime

from tpbDAO import Base

class scrpyTPB():
    scrpyer = None
    db = None
    pathPrefix = ""

    def updateTPBMirror(self,engine):
        mirrorList = self.scrpyer.scrpyTPBMirrorList()
        TPBScrpyer.postMirrors(engine,mirrorList, ts=False)

    def scrpyTPBInMirrors(self, engine,path='/recent/0', threshold=0.3, minSite=3):
        total = 0
        ok = 0
        ratio = 1
        site = 0
        site_num = 0
        while True:
            mirror = TPBScrpyer.getMirrors(engine,limit=1, offset=site_num)
            if not mirror:
                logging.debug("No more mirrors")
                break
            site_num = site_num + 1
            host = mirror[0]
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

            TPBScrpyer.postMirror(engine, host, ts=True)
            site = site + 1
            res = TPBScrpyer.postTorrents(engine, torrentList)
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

    def scrpyTPBRecent(self, dbUrl, basePath='/recent/', offset=0,
                       pageLimit=10, minResource=20):
        engine = create_engine(dbUrl)
        ok = 0
        index = 0
        if basePath[len(basePath)-1] != '/':
            basePath = basePath + '/'

        for index in range(pageLimit):
            path = "{:s}{:d}".format(basePath, index+offset)
            if '/user/' in basePath:
                path = "{:s}{:d}/3".format(basePath, index+offset)
            if '/browse/' in basePath:
                path = "{:s}{:d}/3".format(basePath, index+offset)
            if '/search/' in basePath:
                path = "{:s}{:d}/7//".format(basePath, index+offset)

            res = self.scrpyTPBInMirrors(engine=engine,path=path)
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
        parser.add_argument('--process', dest='process',
                            action='store', type=int, default=8)
        parser.add_argument('--jobs', dest='jobpath',
                            action='store', default=None)
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
            self.torrentdb = 'sqlite:///./data/tpb.db'
        logging.debug("Torrent DB: {}".format(torrentdb))

        # self.db = tpbDB.TPBDatabase(mirrorDB=mirrordb, torrentDB=torrentdb)

    def main(self):
        """[summary]
        """

        engine = create_engine(self.torrentdb)
        Base.metadata.create_all(engine)

        from multiprocessing import Pool

        if self.args.addmirror:
            mirrorUrl = self.args.addmirror
            logging.info("Mirror add updated from {}".format(
                mirrorUrl))
            TPBScrpyer.postMirror(engine,mirrorUrl,ts=True)
            logging.debug(TPBScrpyer.getMirrors(engine,limit=1))
            return

        if self.args.updatemirror or not TPBScrpyer.getMirrors(engine):
            logging.info("Mirror List update from {}".format(
                self.scrpyer.proxyListUrl))
            self.updateTPBMirror(engine)
            logging.debug(TPBScrpyer.getMirrors(engine,limit=10))
            if self.args.updatemirror:
                return

        # torrents = self.scrpyer.scrpyTorrentList(
        #     'file:///home/ylin/tpb-get/crus.html')
        # print(torrents)
        logging.info(
            "Get torrents from page {offset} to page {end} from tpb mirrors with {process} processes.".format(
                path=self.args.path, offset=self.args.offset,
                end=self.args.offset+self.args.pages,
                process=self.args.process
            ))

        jobs = []
        if self.args.jobpath:
            with open(self.args.jobpath) as f:
                jobs = f.readlines()

            logging.info("Find {nbjob} jobs from {jobpath}".format(
                nbjob=len(jobs), jobpath=self.args.jobpath
            ))
        elif self.args.path:
            logging.info("Find 1 jobs from cli path: {path}".format(
                path=self.args.path
            ))
            jobs.append(self.args.path)

        # you may also want to remove whitespace characters like `\n` at the end of each line
        jobs = [x.strip() for x in jobs]
        logging.info("Paths to be scrpy : {}".format(jobs))
        pool = Pool(self.args.process)
        for job in jobs:
            pool.apply_async(func=self.scrpyTPBRecent,
                             kwds={
                                 'offset': self.args.offset,
                                 'pageLimit': self.args.pages,
                                 'minResource': self.args.minResource,
                                 'basePath': job,
                                 'dbUrl': self.torrentdb
                             }, callback=logging.info)

        pool.close()
        pool.join()

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
