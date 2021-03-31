from json import loads

from bs4 import BeautifulSoup

from base import *

# 构建映射url->article
_url2atc = dict()


class NPRURLManager(BaseURLManager):

    def __init__(self, start_page=1, end_page=-1):
        super().__init__(start_page, end_page)

    def parse(self, page_cnt) -> list:
        # 构造目录页json
        time_stamp = 1560643200 #起始时间戳
        dir_json ={"requests":
                [
                     {"indexName": "nprorg",
                      "params": f"query=China&maxValuesPerFacet=10&page={page_cnt-1}&analytics=true&analyticsTags=%5B%22npr.org%2Fsearch%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&clickAnalytics=true&filters=&facets=%5B%22hasAudio%22%2C%22lastModifiedDate%22%2C%22shows%22%5D&tagFilters=&numericFilters=%5B%22lastModifiedDate%3C%3D{time_stamp}%22%5D"},
                     {"indexName": "nprorg",
                      "params": f"query=China&maxValuesPerFacet=10&page={page_cnt-1}&analytics=false&analyticsTags=%5B%22npr.org%2Fsearch%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&clickAnalytics=false&filters=&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=lastModifiedDate"},
                     {"indexName": "station",
                      "params": f"query=China&hitsPerPage=3&maxValuesPerFacet=10&page={page_cnt-1}&analytics=true&analyticsTags=%5B%22npr.org%2Fsearch%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&clickAnalytics=true&filters=&facets=%5B%22hasAudio%22%2C%22lastModifiedDate%22%2C%22shows%22%5D&tagFilters=&numericFilters=%5B%22lastModifiedDate%3C%3D{time_stamp}%22%5D"},
                     {"indexName": "station",
                      "params": f"query=China&hitsPerPage=1&maxValuesPerFacet=10&page={page_cnt-1}&analytics=false&analyticsTags=%5B%22npr.org%2Fsearch%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&clickAnalytics=false&filters=&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=lastModifiedDate"}]
        }
        # 构造目录页url
        dir_url = 'https://o2dg6462xl-dsn.algolia.net/1/indexes/*/queries?x-algolia-application-id=O2DG6462XL&x-algolia-api-key=40f2ee3bc56fa66dd5551ca1496ff941'
        # 获取目录页html
        html = post_html(dir_url, dir_json).decode()
        res = loads(html)['results'][0]['hits']
        urls = []
        for i in res:
            url = 'https://www.npr.org' + i['url']

            try:
                pic_url = i['image']['url']
            except KeyError:
                pic_url = None

            try:
                abstract = i['bodyText']
            except Exception as e:
                self._logger.error(e)
                abstract = None
            act = Article(
                publisher='NPR',
                url='https://www.npr.org' + i['url'],
                title=i['title'],
                date=i['displayDate']['dateTime'],
                author=None, # 这一项交给NPRSpider填
                content=None,  # 这一项交给NPRSpider填
                abstract=abstract,
                location=None,
                section=str(i['tags']) if 'tags' in i else None,
                category=str(i['topics']) if 'topics' in i else None,
                pic_url=pic_url,
                type=i['type'] if 'topics' in i else None,
            )
            _url2atc[url] = act

            urls.append(url)

        return urls


class NPRSpider(BaseSpider):
    def __init__(self, url_manager: BaseURLManager, maximum=-1):
        super().__init__(url_manager, maximum)

    def parse(self, url) -> Article:
        html = get_html(url)
        # 构造解析器
        soup = BeautifulSoup(html, features="html.parser")
        # 获取内容
        raw_text = soup.find('div', attrs={'id': 'storytext'}).find_all('p', recursive=False)
        author = soup.find('p', attrs={'class': 'byline__name byline__name--block'})
        if author:
            author = author.text.strip()
        text = ''
        for i in raw_text:
            text += f'{i.text}\n'
        atc = _url2atc[url]
        atc.content = text
        atc.author = author
        del _url2atc[url]
        return atc


if __name__ == '__main__':
    um = NPRURLManager()
    spider = NPRSpider(
        url_manager=um,
    )

    spider.run()
