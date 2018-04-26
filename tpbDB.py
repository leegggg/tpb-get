class TPBDatabase():
    mirrorDB = None
    torrentDB = None

    torrentTableDefSQL = """
        create table if not exists tpbtorrent (
            id text PRIMARY KEY,
            btih text,
            user text,
            catalog text,
            ts real,
            magnet text,
            title text,
            siteid text
        )
    """

    mirrorTableDefSQL = """
        create table if not exists tpbmirror (
            url text PRIMARY KEY,
            ts real
        )
    """

    def __init__(self, db="./tpb.db", mirrorDB=None, torrentDB=None):
        if not mirrorDB:
            self.mirrorDB = db
        if not torrentDB:
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
        c.execute(self.torrentTableDefSQL)
        conn.commit()
        conn.close()

    def postMirror(self, mirror, ts=False):
        from datetime import datetime
        import sqlite3

        sql = 'insert or IGNORE into tpbmirror (url, ts) VALUES (?,?)'
        if ts:
            sql = 'insert or replace into tpbmirror (url, ts) VALUES (?,?)'

        value = (mirror, datetime.now().timestamp())

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
            values.append((mirror, datetime.now().timestamp(),))

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
            id,btih,user,catalog,ts,magnet,title,siteid
            ) VALUES (?,?,?,?,?,?,?,?)
        '''

        value = (
            torrent.get('id'),
            torrent.get('btih'),
            torrent.get('user'),
            torrent.get('catalog'),
            torrent.get('ts'),
            torrent.get('magnet'),
            torrent.get('title'),
            torrent.get('siteid')
        )

        conn = sqlite3.connect(self.mirrorDB)
        c = conn.cursor()
        c.execute(sql, value)
        conn.commit()
        conn.close()

    def postTorrents(self, torrents):
        import sqlite3

        numWriten = 0
        numError = 0
        numTotal = len(torrents)

        for torrent in torrents:
            try:
                self.postTorrent(torrent)
                numWriten += 1
            except sqlite3.IntegrityError:
                numError += 1

        return {
            'total': numTotal,
            'error': numError,
            'ok': numWriten
        }
