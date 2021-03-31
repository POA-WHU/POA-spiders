from json import loads

from bs4 import BeautifulSoup

from base import *

# 构建映射url->article
_url2atc = dict()


class CNNURLManager(BaseURLManager):

    def __init__(self, start_page=1, end_page=-1):
        super().__init__(start_page, end_page)

    def parse(self, page_cnt) -> list:
        # 构造目录页url
        dir_url = f'https://search.api.cnn.io/content?size=10&q=china&from={10 * (page_cnt - 1)}&page={page_cnt}'
        # 获取目录页html
        html = get_html(dir_url).decode()
        res = loads(html)['result']
        urls = []
        for i in res:
            if i['type'] == 'article':
                url = i['url']
                act = Article(
                    publisher='CNN',
                    url=i['url'],
                    title=i['headline'],
                    date=i['lastModifiedDate'][:10],
                    authors=str(i['contributors']),
                    content=None,  # 这一项交给CNNSpider填
                    abstract=i['body'],
                    location=i['location'],
                    section=i['section'],
                    category=i['mappedSection'],
                    pic_url=i['thumbnail'],
                    type='passage'
                )
                _url2atc[url] = act

                urls.append(url)

        return urls


class CNNSpider(BaseSpider):
    def __init__(self, url_manager: BaseURLManager, maximum=-1):
        super().__init__(url_manager, maximum)

    def parse(self, url) -> Article:
        html = get_html(url)
        # 构造解析器
        soup = BeautifulSoup(html, features="html.parser")
        # 获取内容
        raw_text = soup.find_all('div', attrs={'class': 'zn-body__paragraph'})
        text = ''
        for i in raw_text:
            text += f'{i.text}\n'
        atc = _url2atc[url]
        atc.content = text
        del _url2atc[url]
        return atc


if __name__ == '__main__':
    um = CNNURLManager()
    spider = CNNSpider(
        url_manager=um,
    )

    spider.run()
