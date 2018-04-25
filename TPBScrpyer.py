class ScrpyerTPB():
    """[summary]
    """
    import bs4

    # urlHtmlBase = "file:///home/ylin/politiqueJournalNpl/"
    urlHtmlBase = "http://www.xinhuanet.com/"
    # urlHtmlBase = "file:///home/ylin/politiqueJournalNpl/xinhuaIndex.html"
    proxyListUrl = 'https://raw.githubusercontent.com/proxybay/proxybay.github.io/master/index.html'
    articleUrlRegexp = r'.+/(?P<catalog>.+)/(?P<yearmonth>\d{4}-\d{2})/(?P<day>\d{2})/(?P<id>c_\d{10}).htm'
    urlDateBasePatten = "{year:04d}-{month:02d}/{day:02d}/"
    urlArticlePatten = "nw.D110000renmrb_{year:04d}{month:02d}{day:02d}_{num:d}-{page:02d}.htm"
    urlPagePatten = "nbs.D110000renmrb_{page:02d}.htm"
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
            sites.append(siteTD.get('href'))

        return sites

    def scrpyTurrentList(self, url):
        import bs4
        try:
            content = self.req.getUrl(url)
        except Exception as err:
            print(err)
            raise

        'magnet:?xt=urn:btih:17e3c9fee45ad6e0a2a4cd4bd4e3ff4cbc380e27&dn=DivineBitches--DiB-43103+Delirious+Hunter+and+DJ+Hi+HD&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.ccc.de%3A80'
        dom = bs4.BeautifulSoup(content, "html.parser")
        sites = []
        for tr in dom.select('.vertTh'):
            print(tr.parent())

        return sites

    def parseArticleRef(self, href):
        import re
        articleUrlRegexp = re.compile(self.articleUrlRegexp)
        articleUrl = href.get('href')

        if not articleUrl:
            return None
        if not href.text:
            return None

        articleUrlRegexpMatch = articleUrlRegexp.search(articleUrl)
        article = None
        if articleUrlRegexpMatch:
            date = '{:s}-{:s}'.format(articleUrlRegexpMatch.group(
                'yearmonth'), articleUrlRegexpMatch.group('day'))
            catalog = articleUrlRegexpMatch.group('catalog')
            articleId = articleUrlRegexpMatch.group('id')
            article = {
                'date': date,
                'title': href.text,
                'catalog': catalog,
                'url': articleUrl,
                'id': articleId
            }

        return article

    def scrpyIndexs(self, url=None, retry=3):
        import bs4
        from datetime import datetime
        import req

        if url is None:
            url = self.urlHtmlBase

        try:
            pageRequest = self.req.urlOpen(url=url, retry=3)
        except Exception as err:
            print("Http Error: {0}, give up".format(err))
            raise

        try:
            content = self.req.getContent(pageRequest)
        except Exception as err:
            print("Http read Error: {0}, give up".format(err))
            raise

        dom = bs4.BeautifulSoup(content, "html.parser")

        hrefs = dom.select('a')
        articles = []
        for href in hrefs:
            try:
                article = self.parseArticleRef(href)
            except:
                pass

            if article:
                articles.append(article)

        index = {
            "metadata": {
                "Site": "www.xinhuanet.com",
                "alise": ["XinHuaWang", "xinhuanet"],
                "ts": datetime.now().timestamp(),
                'url': url
            },
            "articles": articles
        }

        return index

    def scrpyArticle(self, articleUrl):
        import bs4
        import datetime
        import uuid
        import re
        import req

        url = articleUrl

        try:
            pageRequest = self.req.urlOpen(url)
        except Exception as err:
            print("Http Error: {0}, give up".format(err))
            raise

        try:
            content = self.req.getContent(pageRequest)
        except Exception as err:
            print("Http read Error: {0}, give up".format(err))
            raise

        dom = bs4.BeautifulSoup(content, "html.parser")
        article = dom.select("#p-detail")[0].get_text(separator='\n')

        title = ""
        ts = datetime.datetime.now().timestamp()
        source = ""
        pageid = str(uuid.uuid4())
        publishid = str(uuid.uuid4())
        keywords = ""
        description = ""
        bodyTitle = ""
        articleId = str(uuid.uuid4())
        timeString = ""

        try:
            articleUrlRegexp = re.compile(self.articleUrlRegexp)
            articleUrlRegexpMatch = articleUrlRegexp.search(articleUrl)
            articleId = articleUrlRegexpMatch.group('id')

            if dom.select("title"):
                title = dom.select("title")[0].text
            else:
                print("No title!!")
            if dom.select(".h-title"):
                bodyTitle = dom.select(".h-title")[0].text
            if dom.select(".h-time"):
                timeString = dom.select(".h-time")[0].text
            if dom.select("#source"):
                source = dom.select("#source")[0].text
            # 2018-04-23 07:40:59
            try:
                ts = datetime.datetime.strptime(
                    timeString.strip(), '%Y-%m-%d %H:%M:%S').timestamp()
            except:
                pass

            meta = dom.find("meta",  {"name": "pageid"})
            if meta:
                pageid = meta.get('content')
            meta = dom.find("meta",  {"name": "publishid"})
            if meta:
                publishid = meta.get('content')
            meta = dom.find("meta",  {"name": "keywords"})
            if meta:
                keywords = meta.get('content')
            meta = dom.find("meta",  {"name": "description"})
            if meta:
                description = meta.get('content')
        except Exception as err:
            print(err)
            pass

        articleObj = {
            'metadata': {
                'ts': ts,
                'time': timeString,
                'scrpy_ts': datetime.datetime.now().timestamp(),
                'url': url,
                'source': source,
                'pageid': pageid,
                'publishid': publishid,
                'keywords': keywords,
                'description': description,
                'body-title': bodyTitle,
                'id': articleId
            },
            'id': articleId,
            'title': title,
            'content': article
        }
        return articleObj
