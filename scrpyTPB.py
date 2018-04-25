# def dumpObj(pathDir, name, obj):
#    import os
#    import json
#    result = False
#    os.makedirs(name=pathDir, mode=0o755, exist_ok=True)
#    filePath = "{:s}{:s}".format(pathDir, name)
#    if not os.path.exists(filePath):
#        file = open(file=filePath, mode='w+', encoding='utf-8')
#        try:
#            json.dump(obj=obj, fp=file, ensure_ascii=False,
#                      indent=4, sort_keys=True)
#            result = True
#        except Exception as err:
#            print(err)
#            pass
#        finally:
#            file.close()
#    else:
#        print("File {:s} already exist skip.".format(filePath))
#
#    return result
#
#
# def scrpyPaper(pathPrefix=""):
#    """[summary]
#    """
#
#    import os
#    from datetime import datetime
#
#    scrpyer = ScrpyerXinHuaNet()
#
#    try:
#        paperObj = scrpyer.scrpyIndexs()
#    except Exception as err:
#        print("[{0}] Scrpy Index failed. Caused by {1}".format(
#            str(datetime.now()), err))
#        raise err
#
#    indexDir = "{:s}index/".format(pathPrefix)
#    contentDir = "{:s}content/".format(pathPrefix)
#
#    indexFileName = "xinhuanet_{0}.json".format(paperObj['metadata']['ts'])
#    print("Writing file {:s}".format(indexFileName))
#    dumpObj(indexDir, indexFileName, paperObj)
#
#    numFileWriten = 0
#    numIndex = 0
#    numFileSkip = 0
#    numTotalArticle = len(paperObj['articles'])
#    for articleRef in paperObj['articles']:
#        numIndex = numIndex + 1
#        articleFileName = "{:s}.json".format(articleRef['id'])
#        articleFilePath = "{:s}{:s}".format(contentDir, articleFileName)
#        if os.path.exists(articleFilePath):
#            print("File {:s} already exist skip.".format(articleFilePath))
#            numFileSkip = numFileSkip + 1
#            continue
#
#        article = None
#        try:
#            article = scrpyer.scrpyArticle(articleRef['url'])
#        except Exception as err:
#            print("[{}] Scrpy article {} failed. Caused by {}".format(
#                str(datetime.now()), articleRef['url'], err))
#
#        if article:
#            log = "[{}][{:03d}/{:03d}][{}]{}".format(
#                str(datetime.now()), numIndex, numTotalArticle, articleRef['id'], articleRef['title'])
#            print(log)
#            if dumpObj(contentDir, articleFileName, article):
#                numFileWriten = numFileWriten + 1
#
#    return {
#        'index': paperObj['metadata']['ts'],
#        'total': numTotalArticle,
#        'write': numFileWriten,
#        'skip': numFileSkip,
#        'err': numTotalArticle-numFileWriten-numFileSkip
#    }


def main():
    """[summary]
    """

    from datetime import datetime
    import argparse
    import TPBScrpyer

    parser = argparse.ArgumentParser(description='scrpye Xinhuanet')
    parser.add_argument('--path', dest='path', action='store', default='./')
    args = parser.parse_args()

    # pathPrefix = '/home/ylin/host_home/RenminRibaoTest/'
    pathPrefix = args.path

    if not pathPrefix[len(pathPrefix)-1] == '/':
        pathPrefix = pathPrefix + '/'

    print("[{ts}] All processes joined. Big brother is watching you".format(
        ts=datetime.now()))

    scrpyer = TPBScrpyer.ScrpyerTPB()
    scrpyer.scrpyTPBMirrorList()
    scrpyer.scrpyTurrentList('https://thepiratebay.rocks/recent/1')

    return


if __name__ == '__main__':
    main()
