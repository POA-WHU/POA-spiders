from sytk import EzParser

from base import *
from db_info import *


class BrookingsURLManager(BaseURLManager):
    def parse(self, page_cnt) -> list:
        url = f'https://www.brookings.edu/topic/china/page/{page_cnt}/?ttttttttttttttttttttttttt=49732&type=events'
        html = get_html(url)
        ezp = EzParser(html)
        tags = ezp.find_all('a', {'class': 'event-content'})
        urls = []
        for i in tags:
            urls.append(i['href'])
        return urls


month_map = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}


class BrookinsSpider(BaseSpider):
    def parse(self, url) -> Article:
        ezp = EzParser(get_html(url))
        title = ezp.find('title').text
        abstract = ezp.find('meta', {'name': 'description'})['content']
        content = ezp.find('div', {'class': 'event-description post-body'}).text
        authors_tags = ezp.find_all('div', {'class': 'expert-info'})
        authors = []
        for i in authors_tags:
            authors.append(i.find(args={'class': 'name'}).text)
        authors = str(authors)
        date_year = ezp.find('div', {'class': 'date-year'}).text
        date_month = ezp.find('div', {'class': 'date-month'}).text
        date_month = month_map[date_month]
        date_number = ezp.find('div', {'class': 'date-number'}).text
        date = '-'.join([date_year, date_month, date_number])
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
                    category=None,
                    pic_url=None,
                    type='event'
                )


if __name__ == '__main__':
    BrookinsSpider(
        server=SERVER,
        database=DATABASE,
        url_manager=BrookingsURLManager()
    ).run()
