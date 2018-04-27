import logging


class req():

    retry = 3
    proxy = None
    timeout = 5
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
    }

    def __init__(self, retry=3, proxy=None):
        self.retry = retry
        self.proxy = proxy

    def urlOpen(self, url, retry=3, proxy=None):
        import urllib.request
        import socket
        if proxy:
            proxyHandler = urllib.request.ProxyHandler(proxy)
            opener = urllib.request.build_opener(proxyHandler)
            urllib.request.install_opener(opener)

        request = urllib.request.Request(url=url, headers=self.headers)
        socket.setdefaulttimeout(self.timeout)
        error = ""
        for i in range(retry):
            try:
                pageRequest = urllib.request.urlopen(request)
                break
            except Exception as err:
                error = err
                logging.debug("Http open Error: {0}, retry {1}, url: {2}".format(
                    err, i+1, url))
        else:
            raise error
        return pageRequest

    def getContent(self, pageRequest, retry=3, minify=True):
        error = ""
        for i in range(retry):
            try:
                content = pageRequest.read().decode(
                    pageRequest.info().get_param('charset') or 'utf-8')
                break
            except Exception as err:
                error = err
                logging.debug("Http Read Error: {0}, retry {1}".format(
                    err, i+1))
        else:
            raise error

        if minify:
            content = content.replace('\n', '').replace(
                '\t', '').replace('\r', '').replace('\xa0', '')
        return content

    def getUrl(self, url, retry=3, proxy=None):
        try:
            pageRequest = self.urlOpen(url=url, retry=retry, proxy=proxy)
        except Exception as err:
            logging.debug("Http open Error: {0}, give up".format(err))
            raise

        try:
            content = self.getContent(pageRequest)
        except Exception as err:
            logging.debug("Http read Error: {0}, give up".format(err))
            raise

        return content
