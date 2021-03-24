from json import loads

from bs4 import BeautifulSoup

from src.base import *
from src.db_info import *

# 构建映射url->article
_url2atc = dict()

class POLITICOURLManager(BaseURLManager):

    def __init__(self, start_page=1, end_page=-1):
        super().__init__(start_page, end_page)

    def parse(self, page_cnt) -> list:
        # 构造目录页url
        dir_url = f'https://www.politico.com/search/{page_cnt-1}?s=newest&q=China'
        # 获取目录页html
        html = get_html(dir_url).decode()
        soup = BeautifulSoup(html, features="html.parser")
        res = soup.find('ul', attrs={'class':'story-frag-list layout-linear'}).find_all('li')
        urls = []
        for i in res:
            i = i.find('article')
            pic_url = i.find('figure').find('div').find('a')['href']
            i = i.find('div',attrs={'class':'summary'})
            tit = i.find('h3').find('a')
            url = tit['href']
            title = tit.text
            tmp = url.split('/')
            type = tmp[3]
            date = tmp[-4]+'-'+tmp[-3]+'-'+tmp[-2]
            try:
                abstract = i.find('div', attrs={'class': 'tease'}).find('p').text
            except:
                abstract = None
            act = Article(
                publisher='POLITICO',
                url=url,
                title=title,
                date=date,
                authors=None, # 这一项交给POLITICOSpider填
                content=None,  # 这一项交给POLITICOSpider填
                abstract=abstract,
                location=None,
                section=None,
                category='Politics', # POLITICO全部关于Politics
                pic_url=pic_url,
                type=type
            )
            _url2atc[url] = act
            urls.append(url)

        return urls


class POLITICOSpider(BaseSpider):
    def __init__(self, server: str, database: str, url_manager: BaseURLManager, maximum=-1):
        super().__init__(server, database, url_manager, maximum)

    def parse(self, url) -> Article:
        html = get_html(url)
        # 构造解析器
        soup = BeautifulSoup(html, features="html.parser")
        atc = _url2atc[url]
        # 获取内容
        raw_text = soup.find_all('div', attrs={'class':'story-text'})
        text = ''
        for i in raw_text:
            raw_text2 = i.find_all('p', recursive=False)
            for j in raw_text2:
                text += f'{j.text}\n'
        atc.content = text
        try:
            authors = []
            if atc.type=='news':
                authorslist = soup.find('span',attrs={'class':'vcard'}).find_all('a')
                for author in authorslist:
                    authors.append(author.text)
            elif atc.type=='newsletters':
                authorslist = soup.find('p',attrs={'class':'byline'}).find_all('a')
                for author in authorslist:
                    authors.append(author.text)
            authors = str(authors)
        except:
            authors = None
        atc.authors = authors
        del _url2atc[url]
        return atc


if __name__ == '__main__':
    um = POLITICOURLManager()
    spider = POLITICOSpider(
        server=SERVER,
        database=DATABASE,
        url_manager=um,
    )

    spider.run()
