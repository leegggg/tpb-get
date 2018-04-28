import logging


class TPBDatabase():
    mirrorDB = None
    torrentDB = None

    torrentTableDefSQLs = ["""
        create table if not exists tpbtorrent (
            id text PRIMARY KEY,
            btih text,
            user text,
            catalog text,
            ts real,
            magnet text,
            title text,
            siteid text,
            size text
        );
    """, """
        drop view if exists  all_torrents;
    """, """
        CREATE VIEW all_torrents as 
            select user, catalog,size , title,ts, siteid,magnet 
                from tpbtorrent 
                order by ts DESC;
    """]

    mirrorTableDefSQL = """
        create table if not exists tpbmirror (
            url text PRIMARY KEY,
            ts real
        )
    """

    def __init__(self, db="./tpb.db", mirrorDB=None, torrentDB=None):
        self.mirrorDB = mirrorDB
        if not self.mirrorDB:
            self.mirrorDB = db

        self.torrentDB = torrentDB
        if not self.torrentDB:
            self.torrentDB = db

        self.createTables()

    def createTables(self):
        import sqlite3

        conn = sqlite3.connect(self.mirrorDB)
        c = conn.cursor()
        c.execute(self.mirrorTableDefSQL)
        conn.commit()
        conn.close()

        conn = sqlite3.connect(self.torrentDB)
        c = conn.cursor()
        for sql in self.torrentTableDefSQLs:
            c.execute(sql)
        conn.commit()
        conn.close()

    def postMirror(self, mirror, ts=False):
        from datetime import datetime
        import sqlite3

        sql = 'insert or IGNORE into tpbmirror (url, ts) VALUES (?,?)'
        if ts:
            sql = 'insert or replace into tpbmirror (url, ts) VALUES (?,?)'

        value = (mirror, datetime.utcnow().timestamp(),)
        logging.debug(value)

        conn = sqlite3.connect(self.mirrorDB)
        c = conn.cursor()
        c.execute(sql, value)
        conn.commit()
        conn.close()

    def postMirrors(self, mirrorList, ts=False):
        from datetime import datetime
        import sqlite3

        sql = 'insert or IGNORE into tpbmirror (url, ts) VALUES (?,?)'
        if ts:
            sql = 'insert or replace into tpbmirror (url, ts) VALUES (?,?)'

        values = []
        for mirror in mirrorList:
            values.append((mirror, datetime.utcnow().timestamp(),))

        conn = sqlite3.connect(self.mirrorDB)
        c = conn.cursor()
        c.executemany(sql, values)
        conn.commit()
        conn.close()

    def getMirrors(self, limit=3, offset=0):
        import sqlite3

        sql = 'SELECT url,ts FROM tpbmirror ORDER BY ts DESC LIMIT ? OFFSET ?'

        mirrors = []
        conn = sqlite3.connect(self.mirrorDB)
        c = conn.cursor()
        for row in c.execute(sql, (limit, offset,)):
            mirrors.append({'url': row[0], 'ts': row[1]})
        conn.commit()
        conn.close()

        return mirrors

    def postTorrent(self, torrent):
        import sqlite3

        sql = '''
        insert or ABORT into tpbtorrent (
            id,btih,user,catalog,ts,magnet,title,siteid,size
            ) VALUES (?,?,?,?,?,?,?,?,?)
        '''

        value = (
            torrent.get('id'),
            torrent.get('btih'),
            torrent.get('user'),
            torrent.get('catalog'),
            torrent.get('ts'),
            torrent.get('magnet'),
            torrent.get('title'),
            torrent.get('siteid'),
            torrent.get('size')
        )

        conn = sqlite3.connect(self.torrentDB)
        c = conn.cursor()
        c.execute(sql, value)
        conn.commit()
        conn.close()

    def postTorrents(self, torrents):
        import sqlite3

        sql = '''
        INSERT OR IGNORE into tpbtorrent (
            id,btih,user,catalog,ts,magnet,title,siteid,size
            ) VALUES (?,?,?,?,?,?,?,?,?)
        '''
        values = []
        for torrent in torrents:
            value = (
                torrent.get('id'),
                torrent.get('btih'),
                torrent.get('user'),
                torrent.get('catalog'),
                torrent.get('ts'),
                torrent.get('magnet'),
                torrent.get('title'),
                torrent.get('siteid'),
                torrent.get('size')
            )
            values.append(value)

        conn = sqlite3.connect(self.torrentDB)
        c = conn.cursor()
        c.executemany(sql, values)
        conn.commit()
        conn.close()

        numWriten = c.rowcount
        numTotal = len(torrents)

        return {
            'total': numTotal,
            'ok': numWriten
        }
