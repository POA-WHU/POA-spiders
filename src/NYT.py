from json import loads
from base64 import b64encode

from bs4 import BeautifulSoup

from src.base import *
from src.db_info import *

# 构建映射url->article
_url2atc = dict()


class NYTURLManager(BaseURLManager):
    def parse(self, page_cnt) -> list:
        payload = {
            "operationName": "SearchRootQuery",
            "variables": {
                "first": 10,
                "sort": "best",
                "text": "China",
                "filterQuery": "",
                "sectionFacetFilterQuery": "",
                "typeFacetFilterQuery": "",
                "sectionFacetActive": False,
                "typeFacetActive": False,
                "cursor": b64encode(f'arrayconnection:{9 + 10 * page_cnt}'.encode()).decode()
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "b117ee74b90b0c02b406304e5051121e9c3e23833eb98a8738320c15dc1e98a6"
                }
            }
        }
        response = post_html('https://samizdat-graphql.nytimes.com/graphql/v2', payload,
                             {
                                 'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                                 'nyt-token': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs+/oUCTBmD/cLdmcecrnBMHiU/pxQCn2DDyaPKUOXxi4p0uUSZQzsuq1pJ1m5z1i0YGPd1U1OeGHAChWtqoxC7bFMCXcwnE1oyui9G1uobgpm1GdhtwkR7ta7akVTcsF8zxiXx7DNXIPd2nIJFH83rmkZueKrC4JVaNzjvD+Z03piLn5bHWU6+w+rA+kyJtGgZNTXKyPh6EC6o5N+rknNMG5+CdTq35p8f99WjFawSvYgP9V64kgckbTbtdJ6YhVP58TnuYgr12urtwnIqWP9KSJ1e5vmgf3tunMqWNm6+AnsqNj8mCLdCuc5cEB74CwUeQcP2HQQmbCddBy2y0mEwIDAQAB',
                                 'sec-ch-ua-mobile': '?0',
                                 'nyt-app-type': 'project-vi',
                                 'content-type': 'application/json',
                                 'nyt-app-version': '0.0.5',
                                 'origin': 'https://www.nytimes.com',
                                 'referer': 'https://www.nytimes.com/',
                             }
                             )
        j_res = loads(response.decode())
        edges = j_res['data']['search']['hits']['edges']
        urls = []
        for i in edges:
            node = i['node']['node']
            if 'article' not in node['uri']:
                continue

            try:
                authors = node['bylines'][0]['renderedRepresentation'][3:]
            except KeyError or IndexError:
                authors = None
            try:
                pic_url = node['promotionalMedia']['crops'][0]['renditions'][0]['url']
            except KeyError or IndexError:
                pic_url = None

            act = Article(
                publisher='NYT',
                url=node['url'],
                title=node['creativeWorkHeadline']['default'],
                date=node['firstPublished'][:10],
                authors=authors,
                content=None,  # 这一项交给NYTSpider填
                abstract=node['creativeWorkSummary'],
                location=None,
                section=node['section']['displayName'],
                category=None,
                pic_url=pic_url,
                type='article'
            )
            _url2atc[node['url']] = act
            urls.append(node['url'])

        return urls


class NYTSpider(BaseSpider):
    def parse(self, url) -> Article:
        html = get_html(url, {
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': None,
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': 1,
        })

        soup = BeautifulSoup(html, features="html.parser")
        text = soup.find('main').find('div').find('article').find('section').text
        atc = _url2atc[url]
        atc.content = text
        del _url2atc[url]
        return atc


if __name__ == '__main__':
    NYTSpider(
        server=SERVER,
        database=DATABASE,
        url_manager=NYTURLManager(),
    ).run()
