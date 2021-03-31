from json import loads

from bs4 import BeautifulSoup

from base import *


# 构建映射url->article
_url2atc = dict()
month = dict({'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6,
              'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12})

class WilsonURLManager(BaseURLManager):

    def __init__(self, start_page=1, end_page=-1):
        super().__init__(start_page, end_page)

    def parse(self, page_cnt) -> list:
        # 构造目录页url
        dir_url = f'https://www.wilsoncenter.org/search?_page={page_cnt}&keywords=china&_limit=10&types=article,blog_post'
        # 获取目录页html
        html = get_html(dir_url).decode()
        soup = BeautifulSoup(html, features="html.parser")
        res = soup.find('div',attrs={'class':'faceted-search-results'}).find_all('a',attrs={'class':'teaser'},recursive=False)
        urls = []
        for i in res:
            type = i['data-type']
            url = 'https://www.wilsoncenter.org' + i['href']
            try:
                pic_url = i.find('div', attrs={'class':'teaser-image'}).find('img')['src']
            except:
                pic_url = None
            i = i.find('div', attrs={'class':'teaser-content'})
            try:
                category = i.find('div',attrs={'class':'teaser-top-meta'}).find('div',attrs={'class':'teaser-topic'}).text
            except:
                category = None
            title = i.find('div',attrs={'class':'teaser-title'}).find('span').text
            try:
                authors = i.find('span',attrs={'class':'teaser-byline-text-author'}).text
            except:
                authors = None
            try:
                tmp = i.find('span',attrs={'class':'teaser-byline-text-date'}).text.split(' ')
                date = tmp[-1]+'-'+str(month[tmp[0]])+'-'+tmp[1].replace(',','')
            except:
                date = None
            act = Article(
                publisher='Wilson',
                url=url,
                title=title,
                date=date,
                authors=authors,
                content=None,  # 这一项交给POLITICOSpider填
                abstract=None,
                location=None,
                section=None,
                category=category,
                pic_url=pic_url,
                type=type
            )
            _url2atc[url] = act
            urls.append(url)

        return urls


class WilsonSpider(BaseSpider):
    def __init__(self, url_manager: BaseURLManager, maximum=-1):
        super().__init__(url_manager, maximum)

    def parse(self, url) -> Article:
        html = get_html(url)
        # 构造解析器
        soup = BeautifulSoup(html, features="html.parser")
        atc = _url2atc[url]
        # 获取内容
        raw_text = soup.find('div', attrs={'class':'text-block wysiwyg-content'}).find_all('p')
        text = ''
        for i in raw_text:
            text += f'{i.text}\n'
        atc.content = text
        del _url2atc[url]
        return atc


if __name__ == '__main__':
    um = WilsonURLManager()
    spider = WilsonSpider(
        url_manager=um,
    )

    spider.run()
