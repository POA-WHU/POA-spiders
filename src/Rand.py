from os import mkdir

from bs4 import BeautifulSoup

from base import *
from db_info import *

_url2atc = dict()
month = dict({'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
              'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12})

class RandURLManager(BaseURLManager):

    def __init__(self, start_page=1, end_page=-1):
        super().__init__(start_page, end_page)

    def parse(self, page_cnt) -> list:
        # 构造目录页urlz
        dir_url = f'https://www.rand.org/topics/china.html?page={page_cnt}'
        # 获取目录页html
        html = get_html(dir_url)
        # 构造解析器
        soup = BeautifulSoup(html, features="html.parser")
        # 找到teasers list organic类下所有类名为title的tag
        airticles = soup.find(attrs={'class': 'teasers list organic'}).find_all('li')
        # 如果没有找到匹配的结果，说明已经爬取完毕，退出循环
        urls = []
        for i in airticles:
            try:
                url = i.find('div', attrs={'class':'img-wrap'}).find('a')['href']
            except:
                url = None

            try:
                pic_url = i.find('div', attrs={'class':'img-wrap'}).find('img')['src']
            except:
                pic_url = None
            
            try:
                title = i.find('div', attrs={'class':'text'}).find(attrs={'class':'title'}).text
            except:
                title = None
            
            try:
                date_list = i.find('div', attrs={'class':'text'}).find(attrs={'class':'date'}).text.split(' ')
                m = str(month[date_list[0]])
                y = date_list[2]
                d = date_list[1][:-1]
                date = y + '-' + m + '-' + d
            except:
                date = None

            try:
                abstract = i.find('div', attrs={'class':'text'}).find(attrs={'class':'desc'}).text
            except:
                abstract = None

            try:
                type_ = i.find('div', attrs={'class':'text'}).find(attrs={'class':'type'}).text
            except:
                type_ = None

            act = Article(
                        publisher='Rand',
                        url=url,
                        title=title,
                        date=date,
                        authors=None,  # 这一项交给RandSpider填
                        content=None,  # 这一项交给RandSpider填
                        abstract=abstract,
                        location=None,  # 无地址
                        section=None,   # 这一项交给RandSpider填,
                        category=None,  # 这一项交给RandSpider填,
                        pic_url=pic_url,
                        type=type_
                    )
            urls.append(url)
            _url2atc[url] = act

        return urls

def Blog_parse(atc:Article, soup:BeautifulSoup):
    try:
        content_list = soup.find('div', attrs={'class':'body-text'}).find_all('p')
        content = ""
        for i in content_list:
            content += f'{i.text}\n'
    except:
        content = None
    
    try:
        topic_list = soup.find('div', attrs={'class':'blog-column-right'}).find_all('li')
        topic = []
        for i in topic_list:
            topic.append(i.text)
    except:
        topic = None
        
    atc.content = content
    atc.category = str(topic)
    return atc

def Com_parse(atc:Article, soup:BeautifulSoup):
    try:
        authors = []
        author = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('p', attrs={'class':'authors'}).find('a').text
        authors.append(author)
    except:
        author = None

    try:
        content_list = soup.find('div', attrs={'class':'body-text'}).find_all('p')
        content = ""
        for i in content_list:
            content += f'{i.text}\n'
    except:
        content = None

    try:
        topic_list = soup.find('div', attrs={'class':'blog-column-right'}).find_all('li')
        topic = []
        for i in topic_list:
            topic.append(i.text)
    except:
        topic = None
        
    atc.content = content
    atc.authors = str(authors)
    atc.category = str(topic)
    return atc

def Journal_parse(atc:Article, soup:BeautifulSoup):
    try:
        authors = []
        author_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('p', attrs={'class':'authors'}).find_all('a')
        for i in author_list:
            authors.append(i.text)
    except:
        authors = None

    try:
        content_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('div', attrs={'class':'abstract product-page-abstract'}).find_all('p')
        content = ""
        for i in content_list:
            content += f'{i.text}\n'
    except:
        content = None

    try:
        topic_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('ul', attrs={'class':'related-topics'}).find_all('a')
        topic = []
        for i in topic_list:
            topic.append(i.text)
    except:
        topic = None
        
    atc.content = content
    atc.authors = str(authors)
    atc.category = str(topic)
    return atc

def News_parse(atc:Article, soup:BeautifulSoup):
    try:
        authors = []
        author_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('div', attrs={'class':'researcher-titles'}).find_all('a')
        for i in author_list:
            authors.append(i.text)
    except:
        authors = None

    try:
        content_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('div', attrs={'class':'eight columns'}).find_all('p')
        content_list = content_list[2:]
        content = ""
        for i in content_list:
            content += f'{i.text}\n'
    except:
        content = None

    try:
        topic_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('aside', attrs={'aria-label':'Explore'}).find_all('ul')[1].find_all('li')
        topic = []
        for i in topic_list:
            topic.append(i.text)
    except:
        topic = None
        
    atc.content = content
    atc.authors = str(authors)
    atc.category = str(topic)
    return atc

def Report_parse(atc:Article, soup:BeautifulSoup):
    try:
        authors = []
        author_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                           find('p', attrs={'class':'authors'}).find_all('a')
        for i in author_list:
            authors.append(i.text)
    except:
        authors = None

    try:
        abtract_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('div', attrs={'class':'abstract product-page-abstract'}).find_all('p')
        key_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                        find('div', attrs={'class':'key-findings'}).find_all('h3')
        recommand_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                              find('div', attrs={'class':'recommendations'}).find_all('li')
        content_list = abtract_list + key_list + recommand_list
        content = ""
        for i in content_list:
            content += f'{i.text}\n'
    except:
        content = None

    try:
        topic_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('ul', attrs={'class':'related-topics'}).find_all('a')
        topic = []
        for i in topic_list:
            topic.append(i.text)
    except:
        topic = None
        
    atc.content = content
    atc.authors = str(authors)
    atc.category = str(topic)
    return atc

def Testimony_parse(atc:Article, soup:BeautifulSoup):
    try:
        authors = []
        author_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                           find('p', attrs={'class':'authors'}).find_all('a')
        for i in author_list:
            authors.append(i.text)
    except:
        authors = None

    try:
        content = 'https://www.rand.org' + soup.find('div', attrs={'class':'column-wrap one-column'}).\
                                                find('span', attrs={'class':'format-pdf'}).find('a')['href']
    except:
        content = None

    try:
        topic_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                          find('ul', attrs={'class':'related-topics'}).find_all('a')
        topic = []
        for i in topic_list:
            topic.append(i.text)
    except:
        topic = None
    
    atc.type = "pdf"
    atc.content = content
    atc.authors = str(authors)
    atc.category = str(topic)
    return atc

def Dissertation_parse(atc:Article, soup:BeautifulSoup):
    try:
        authors = []
        author_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                           find('p', attrs={'class':'authors'}).find_all('a')
        for i in author_list:
            authors.append(i.text)
    except:
        authors = None

    try:
        content_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                            find('div', attrs={'class':'abstract product-page-abstract'}).find_all('p')
        content = ""
        for i in content_list:
            content += f'{i.text}\n'
    except:
        content = None

    try:
        topic_list = soup.find('div', attrs={'class':'column-wrap one-column'}).\
                          find('ul', attrs={'class':'related-topics'}).find_all('a')
        topic = []
        for i in topic_list:
            topic.append(i.text)
    except:
        topic = None
    
    atc.content = content
    atc.authors = str(authors)
    atc.category = str(topic)
    return atc

class RandSpider(BaseSpider):

    def __init__(self, server: str, database: str, url_manager: BaseURLManager, maximum=-1):
        super().__init__(server, database, url_manager, maximum)

    def parse(self, url) -> Article:
        html = get_html(url)
        # 构造解析器
        soup = BeautifulSoup(html, features="html.parser")
        atc = _url2atc[url]

        if atc.type == 'Blog':
            atc = Blog_parse(atc, soup)
        elif atc.type == 'Commentary':
            atc = Com_parse(atc, soup)
        elif atc.type == 'Journal Article':
            atc = Journal_parse(atc, soup)
        elif atc.type == 'News Release':
            atc = News_parse(atc, soup)
        elif atc.type == 'Report': 
            atc = Report_parse(atc, soup)
        elif atc.type == 'Testimony':
            atc = Testimony_parse(atc, soup)
        elif atc.type == 'Dissertation':
            atc = Dissertation_parse(atc, soup)

        del _url2atc[url]
        return atc
    
if __name__ == '__main__':
    um = RandURLManager()
    spider = RandSpider(
        server=SERVER,
        database=DATABASE,
        url_manager=um,
    )
    spider.run()
