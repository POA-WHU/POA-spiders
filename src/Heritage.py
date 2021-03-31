from json import loads

from bs4 import BeautifulSoup

from base import *

# 构建映射url->article
_url2atc = dict()
month = dict({'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
              'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12})

class HRTURLManager(BaseURLManager):

    def __init__(self, start_page=1, end_page=-1):
        super().__init__(start_page, end_page)

    def parse(self, page_cnt) -> list:
        #构造目录页json
        dir_json = f"view_name=issues_content_listing_solr&view_display_id=block_1&view_args=132&view_path=%2Ftaxonomy%2Fterm%2F132&view_base_path=&view_dom_id=50aeda757c83ab28397f9ab21e0dbce7a3113896a2e6167ab0c1fe15cdf047a2&pager_element=0&taxonomy_term_tid=132&f%5B0%5D=keywords%3A388&page={page_cnt-1}&_drupal_ajax=1&ajax_page_state%5Btheme%5D=heritage_theme&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=classy%2Fnode%2Ccore%2Fdrupal.autocomplete%2Ccore%2Fhtml5shiv%2Cfacets%2Fdrupal.facets.dropdown-widget%2Cfacets%2Fdrupal.facets.general%2Cfacets%2Fdrupal.facets.views-ajax%2Cheritage_theme%2Fglobal%2Cheritage_theme%2Fissues%2Csearch_autocomplete%2Ftheme.minimal.css%2Csystem%2Fbase%2Ctheme_name%2Fheritage-impact-breaker%2Cviews%2Fviews.module%2Cviews_infinite_scroll%2Fviews-infinite-scroll"
        #构造目录页url
        dir_url = 'https://www.heritage.org/views/ajax?f%5B0%5D=keywords%3A388&_wrapper_format=drupal_ajax'

        # #Taiwan
        # dir_json = f"view_name=issues_content_listing_solr&view_display_id=block_1&view_args=132&view_path=%2Ftaxonomy%2Fterm%2F132&view_base_path=&view_dom_id=9f94b277d18e04b664128ebae9aa271cf7f9ea29fe551a8a264350fca39e90e3&pager_element=0&taxonomy_term_tid=132&f%5B0%5D=content_type%3Acommentary&f%5B1%5D=keywords%3A1640&page={page_cnt-1}&_drupal_ajax=1&ajax_page_state%5Btheme%5D=heritage_theme&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=classy%2Fnode%2Ccore%2Fdrupal.autocomplete%2Ccore%2Fhtml5shiv%2Cfacets%2Fdrupal.facets.dropdown-widget%2Cfacets%2Fdrupal.facets.general%2Cfacets%2Fdrupal.facets.views-ajax%2Cheritage_theme%2Fglobal%2Cheritage_theme%2Fissues%2Csearch_autocomplete%2Ftheme.minimal.css%2Csystem%2Fbase%2Ctheme_name%2Fheritage-impact-breaker%2Cviews%2Fviews.module%2Cviews_infinite_scroll%2Fviews-infinite-scroll"
        # dir_url = 'https://www.heritage.org/views/ajax?f%5B0%5D=content_type%3Acommentary&f%5B1%5D=keywords%3A1640&_wrapper_format=drupal_ajax'

        # 获取目录页html
        html = post_html(dir_url, dir_json, {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}, False).decode()
        dir = loads(html)[1]['data']
        soup = BeautifulSoup(dir, features="html.parser")
        res = soup.find_all('div',attrs={'class':'result-card__info-wrapper'})
        urls = []
        for i in res:
            #print(i)
            tit = i.find('a',attrs={'class':'result-card__title js-hover-target'})
            url = 'https://www.heritage.org' + tit['href']
            title = tit.text
            tmp = i.find('p', attrs={'class':'result-card__date'}).find('span').text.split(' ')
            date = tmp[-1] + '-' + str(month[tmp[0]]) + '-' + tmp[1].replace(',', '')
            try:
                authors = i.find('a',attrs={'class':'result-card__link'}).find('span').text
            except:
                authors = None
            act = Article(
                publisher='Heritage',
                url=url,
                title=title,
                date=date,
                authors=str(authors),
                content=None,  # 这一项交给HRTSpider填
                abstract=None, # 这一项交给HRTSpider填
                location=None,
                section=None,
                category=None, # Taiwan时category设为Taiwan
                pic_url=None,
                type='Commentary'
            )
            _url2atc[url] = act

            urls.append(url)

        return urls


class HRTSpider(BaseSpider):
    def __init__(self, url_manager: BaseURLManager, maximum=-1):
        super().__init__(url_manager, maximum)

    def parse(self, url) -> Article:
        html = get_html(url)
        # 构造解析器
        soup = BeautifulSoup(html, features="html.parser")
        # 获取内容
        raw_text = soup.find('div', attrs={'class': 'article__body-copy'}).find('div').find_all('p')
        text = ''
        for i in raw_text:
            text += f'{i.text}\n'
        try:
            raw_abstract = soup.find('div', attrs={'class': 'key-takeaways__wrapper'}).find_all('p')
            abstract = ''
            for i in raw_abstract:
                abstract += f'{i.text}\n'
        except:
            abstract = None

        atc = _url2atc[url]
        atc.content = text
        atc.abstract = abstract
        if atc.authors == None:
            try:
                author = soup.find('div', attrs={'class': 'author-card__mulit-author-info'}).find('a',attrs={'class': 'author-card__multi-name'}).find('span').text
            except:
                author = None
            atc.authors = author
        del _url2atc[url]
        return atc


if __name__ == '__main__':
    um = HRTURLManager()
    spider = HRTSpider(
        url_manager=um,
    )

    spider.run()
