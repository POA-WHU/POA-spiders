import time

from bs4 import BeautifulSoup

from base import *

# 构建映射url->article
_url2atc = dict()
month = dict({'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
              'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12})

class REUTERURLManager(BaseURLManager):

    def __init__(self, start_page=1, end_page=-1):
        super().__init__(start_page, end_page)

    def parse(self, page_cnt) -> list:
        # 构造目录页url
        # https://www.reuters.com/news/archive/china-news?view=page&page=1&pageSize=10
        dir_url = f'https://www.reuters.com/news/archive/china-news?view=page&page={page_cnt}&pageSize=10'
        # 获取目录页html
        html = get_html(dir_url)
        soup = BeautifulSoup(html, features="html.parser")
        articles = soup.find(attrs={'class':'news-headline-list'}).find_all(attrs={'class':'story'})
        urls = []
        for i in articles:
            # 子tag中的href属性
            try:
                url = 'https://www.reuters.com' + i.find('div', attrs={'story-content'}).find('a')['href']
            except:
                url = None
            
            try:
                pic_url = i.find('div', attrs={'story-photo lazy-photo'}).find('img')['org-src']
            except:
                pic_url = None
            
            try:
                title = i.find('div', attrs={'story-content'}).find('h3').text.strip()
            except:
                title = None
            
            try:
                date = i.find('div', attrs={'story-content'}).find('time').find('span').text
                if date[0].isdigit():
                    date = time.strftime("%Y-%m-%d", time.localtime()) 
                else:
                    temp = date.split()
                    date = temp[2] + '-' + str(month[temp[0]]) + '-' + temp[1]
            except:
                date = None

            try:
                abstract = i.find('div', attrs={'story-content'}).find('p').text.strip()
            except:
                abstract = None
            
            act = Article(
                    publisher='REUTER',
                    url=url,
                    title=title,
                    date=date,
                    authors=None,  # 这一项交给REUTERSpider填
                    content=None,  # 这一项交给REUTERSpider填
                    abstract=abstract,
                    location=None,  # 这一项交给REUTERSpider填
                    section=None,
                    category=None,  # 这一项交给REUTERSpider填,
                    pic_url=pic_url,
                    type='passage'
                )
            urls.append(url)
            print(url)
            _url2atc[url] = act

        return urls

class REUTERSpider(BaseSpider):
    def __init__(self, url_manager: BaseURLManager, maximum=-1):
        super().__init__(url_manager, maximum)

    def parse(self, url) -> Article:
        html = get_html(url)
        # 构造解析器
        soup = BeautifulSoup(html, features="html.parser")
        # 获取内容
        try:
            authors_text = soup.find('div', attrs={'class', 'TwoColumnsLayout-body-86gsE ArticlePage-body-container-10RhS'}).find('div', attrs={'clss', 'Attribution-attribution-Y5JpY'}).text
            authors_text = authors_text.split(';')[0].split(' ')[2:]
            authors = []
            location = ""
            name = ""
            for i in authors_text:
                if i == 'and':
                    authors.append(name.strip())
                    name = ""
                elif i == 'in':
                    authors.append(name.strip())
                    break
                #     l = authors_text.index(i)
                #     location = " ".join(authors_text[l+1:])
                #     break
                elif authors_text.index(i) == (len(authors_text) - 1):
                    name = name + i + " "
                    authors.append(name.strip())
                else:
                    name = name + i + " "
            # if location == "":
            #     location = None
        except:
            authors = None
        
        try:
            raw_text = soup.find('div', attrs={'class', 'TwoColumnsLayout-body-86gsE ArticlePage-body-container-10RhS'}).\
                            find('div', attrs={'clss', 'ArticleBodyWrapper'}).\
                            find_all('p', attrs={'class', 'Paragraph-paragraph-2Bgue ArticleBody-para-TD_9x'})
            try:
                location = raw_text[0].text.split(' ')
                loc_index = location.index('-')
                if loc_index == 1:
                    location = None
                else:
                    location = " ".join(location[:(loc_index-1)])
            except:
                location = None
            raw_text = raw_text[1:] # 去掉abstract
            text = ''
            for i in raw_text:
                text += f'{i.text}\n'
        except:
            text = None

        try:
            category = soup.find('div', attrs={'class', 'TwoColumnsLayout-hero-3H8pu'}).\
                            find('div', attrs={'clss', 'ArticleHeader-info-container-3-6YG'}).\
                            find('a').text
        except:
            category = None
        atc = _url2atc[url]
        atc.authors = str(authors)
        atc.location = location
        atc.content = text
        atc.category = category
        del _url2atc[url]
        return atc

if __name__ == '__main__':
    um = REUTERURLManager()
    spider = REUTERSpider(
        url_manager=um,
    )

    spider.run()