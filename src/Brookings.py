from sytk import EzParser
import json

from base import *
from db_info import *


class BrookingsURLManager(BaseURLManager):
    def parse(self, page_cnt) -> list:
        url = f'https://www.brookings.edu/topic/china/page/{page_cnt}/?ttttttttttttttttttttttttt=49732&type=all'
        html = get_html(url)
        ezp = EzParser(html)
        tags = ezp.find_all('div', {'class': 'article-info'})
        urls = []
        for i in tags:
            try:
                urls.append(i[0][0]['href'])
            except KeyError:
                pass
        return urls


# month_map = {
#     'Jan': '01',
#     'Feb': '02',
#     'Mar': '03',
#     'Apr': '04',
#     'May': '05',
#     'Jun': '06',
#     'Jul': '07',
#     'Aug': '08',
#     'Sep': '09',
#     'Oct': '10',
#     'Nov': '11',
#     'Dec': '12'
# }


def blog_handler(url) -> Article:

    ezp = EzParser(get_html(url))
    title = ezp.find('title').text
    data = json.loads(ezp.find('script', {'type': 'application/ld+json'}).text)
    pic_url = data['image']['url']
    date = data['datePublished'][:10]
    authors = str([i['name'] for i in data['author']])
    abstract = ezp.find('div', {'class': 'editors-note'}).find('p').text
    content_tag = ezp.find(args={'class': 'post-body post-body-enhanced'})
    content = ''
    for i in content_tag.children:
        if i.tag != 'p':
            continue
        content += i.text
    category = ezp.find(args={'class': 'content-column-no-aside'}).find('ul').text.replace('\n', '').replace('\t', '')
    return Article(
        publisher='Brookings',
        url=url,
        title=title,
        date=date,
        authors=authors,
        content=content,  # 这一项交给CNNSpider填
        abstract=abstract,
        location=None,
        section=None,
        category=category,
        pic_url=pic_url,
        type='event'
    )


def article_handler(url) -> Article:
    pass


def techstream_handler(url) -> Article:
    pass


class BrookinsSpider(BaseSpider):
    def parse(self, url) -> Article:

        if 'brookings' not in url:
            # 外链
            pass
        elif 'blog' in url:
            return blog_handler(url)
        elif 'article' in url:
            return article_handler(url)
        elif 'techstream' in url:
            return techstream_handler(url)
        else:
            raise Exception(f'new type found:{url}')
        # ezp = EzParser(get_html(url))
        # title = ezp.find('title').text
        # abstract = ezp.find('meta', {'name': 'description'})['content']
        # content = ezp.find(
        #     'div', {'class': 'event-description post-body'}).text
        # authors_tags = ezp.find_all('div', {'class': 'expert-info'})
        # authors = []
        # for i in authors_tags:
        #     authors.append(i.find(args={'class': 'name'}).text)
        # authors = str(authors)
        # date_year = ezp.find('div', {'class': 'date-year'}).text
        # date_month = ezp.find('div', {'class': 'date-month'}).text
        # date_month = month_map[date_month]
        # date_number = ezp.find('div', {'class': 'date-number'}).text
        # date = '-'.join([date_year, date_month, date_number])
        # return Article(
        #     publisher='Brookings',
        #     url=url,
        #     title=title,
        #     date=date,
        #     authors=authors,
        #     content=content,  # 这一项交给CNNSpider填
        #     abstract=abstract,
        #     location=None,
        #     section=None,
        #     category=None,
        #     pic_url=None,
        #     type='event'
        # )


if __name__ == '__main__':
    BrookinsSpider(
        server=SERVER,
        database=DATABASE,
        url_manager=BrookingsURLManager()
    ).run()
