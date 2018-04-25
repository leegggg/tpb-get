class ScrpyerXinHuaNet:
    """[summary]
    """
    import bs4

    # urlHtmlBase = "file:///home/ylin/politiqueJournalNpl/"
    urlHtmlBase = "http://www.xinhuanet.com/"
    # urlHtmlBase = "file:///home/ylin/politiqueJournalNpl/xinhuaIndex.html"
    articleUrlRegexp = r'.+/(?P<catalog>.+)/(?P<yearmonth>\d{4}-\d{2})/(?P<day>\d{2})/(?P<id>c_\d{10}).htm'
    urlDateBasePatten = "{year:04d}-{month:02d}/{day:02d}/"
    urlArticlePatten = "nw.D110000renmrb_{year:04d}{month:02d}{day:02d}_{num:d}-{page:02d}.htm"
    urlPagePatten = "nbs.D110000renmrb_{page:02d}.htm"
    useProxy = True
    proxy = {'http': 'squid.hursley.ibm.com:3128'}

    def urlOpen(self, url, retry=3):
        import urllib.request
        import socket

        if self.useProxy:
            proxy = urllib.request.ProxyHandler(self.proxy)
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)

        socket.setdefaulttimeout(60)
        error = ""
        for i in range(retry):
            try:
                pageRequest = urllib.request.urlopen(url)
                break
            except Exception as err:
                error = err
                print("Http Error: {0}, retry {1}, url: {2}".format(
                    err, i+1, url))
        else:
            raise error
        return pageRequest

    def getContent(self, pageRequest, retry=3):
        error = ""
        for i in range(retry):
            try:
                content = pageRequest.read().decode(
                    pageRequest.info().get_param('charset') or 'utf-8')
                break
            except Exception as err:
                error = err
                print("Http Read Error: {0}, retry {1}".format(
                    err, i+1))
        else:
            raise error

        content = content.replace('\n', '').replace('\t', '').replace('\r', '')

        return content

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

        if url is None:
            url = self.urlHtmlBase

        try:
            pageRequest = self.urlOpen(url=url, retry=3)
        except Exception as err:
            print("Http Error: {0}, give up".format(err))
            raise

        try:
            content = self.getContent(pageRequest)
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

        url = articleUrl

        try:
            pageRequest = self.urlOpen(url)
        except Exception as err:
            print("Http Error: {0}, give up".format(err))
            raise

        try:
            content = self.getContent(pageRequest)
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


def dumpObj(pathDir, name, obj):
    import os
    import json
    result = False
    os.makedirs(name=pathDir, mode=0o755, exist_ok=True)
    filePath = "{:s}{:s}".format(pathDir, name)
    if not os.path.exists(filePath):
        file = open(file=filePath, mode='w+', encoding='utf-8')
        try:
            json.dump(obj=obj, fp=file, ensure_ascii=False,
                      indent=4, sort_keys=True)
            result = True
        except Exception as err:
            print(err)
            pass
        finally:
            file.close()
    else:
        print("File {:s} already exist skip.".format(filePath))

    return result


def scrpyPaper(pathPrefix=""):
    """[summary]
    """

    import os
    from datetime import datetime

    scrpyer = ScrpyerXinHuaNet()

    try:
        paperObj = scrpyer.scrpyIndexs()
    except Exception as err:
        print("[{0}] Scrpy Index failed. Caused by {1}".format(
            str(datetime.now()), err))
        raise err

    indexDir = "{:s}index/".format(pathPrefix)
    contentDir = "{:s}content/".format(pathPrefix)

    indexFileName = "xinhuanet_{0}.json".format(paperObj['metadata']['ts'])
    print("Writing file {:s}".format(indexFileName))
    dumpObj(indexDir, indexFileName, paperObj)

    numFileWriten = 0
    numIndex = 0
    numFileSkip = 0
    numTotalArticle = len(paperObj['articles'])
    for articleRef in paperObj['articles']:
        numIndex = numIndex + 1
        articleFileName = "{:s}.json".format(articleRef['id'])
        articleFilePath = "{:s}{:s}".format(contentDir, articleFileName)
        if os.path.exists(articleFilePath):
            print("File {:s} already exist skip.".format(articleFilePath))
            numFileSkip = numFileSkip + 1
            continue

        article = None
        try:
            article = scrpyer.scrpyArticle(articleRef['url'])
        except Exception as err:
            print("[{}] Scrpy article {} failed. Caused by {}".format(
                str(datetime.now()), articleRef['url'], err))

        if article:
            log = "[{}][{:03d}/{:03d}][{}]{}".format(
                str(datetime.now()), numIndex, numTotalArticle, articleRef['id'], articleRef['title'])
            print(log)
            if dumpObj(contentDir, articleFileName, article):
                numFileWriten = numFileWriten + 1

    return {
        'index': paperObj['metadata']['ts'],
        'total': numTotalArticle,
        'write': numFileWriten,
        'skip': numFileSkip,
        'err': numTotalArticle-numFileWriten-numFileSkip
    }


def main():
    """[summary]
    """

    from datetime import datetime
    import argparse

    parser = argparse.ArgumentParser(description='scrpye Xinhuanet')
    parser.add_argument('--path', dest='path', action='store', default='./')
    args = parser.parse_args()

    # pathPrefix = '/home/ylin/host_home/RenminRibaoTest/'
    pathPrefix = args.path

    if not pathPrefix[len(pathPrefix)-1] == '/':
        pathPrefix = pathPrefix + '/'

    print("[{ts}] Start scrpy XinhuaNet to {pathPrefix:s}.".format(
        ts=datetime.now(), pathPrefix=pathPrefix))
    print(scrpyPaper(pathPrefix=pathPrefix))
    print("[{ts}] All processes joined. Big brother is watching you".format(
        ts=datetime.now()))

    # scrpyer = ScrpyerXinHuaNet()
    # print(scrpyer.scrpyArticle(
    #     "http://www.xinhuanet.com/politics/leaders/2017-11/23/c_1122002077.htm"))

    return


if __name__ == '__main__':
    main()
