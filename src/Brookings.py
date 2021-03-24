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



class BrookinsSpider(BaseSpider):
    def parse(self, url):

        if 'brookings' not in url:
            # 外链
            return
        elif 'blog' in url:
            type_ = 'blog'
        elif 'article' in url:
            type_ = 'article'
        elif 'techstream' in url:
            type_ = 'techstream'
        else:
            return
        ezp = EzParser(get_html(url))
        title = ezp.find('title').text
        data = json.loads(ezp.find('script', {'type': 'application/ld+json'}).text)
        pic_url = data['image']['url']
        date = data['datePublished'][:10]
        authors = str([i['name'] for i in data['author']])
        try:
            abstract = ezp.find('div', {'class': 'editors-note'}).find('p').text
        except AttributeError:
            abstract = None
        content_tag = ezp.find(args={'class': 'post-body post-body-enhanced'})
        content = ''
        for i in content_tag.children:
            if i.tag != 'p':
                continue
            content += i.text
        try:
            category = ezp.find(
                args={'class': 'content-column-no-aside'}
            ).find(
                'ul'
            ).text.replace('\n', '').replace('\t', '')
        except AttributeError:
            category = None

        return Article(
            publisher='Brookings',
            url=url,
            title=title,
            date=date,
            authors=authors,
            content=content,
            abstract=abstract,
            location=None,
            section=None,
            category=category,
            pic_url=pic_url,
            type=type_
        )


if __name__ == '__main__':
    BrookinsSpider(
        server=SERVER,
        database=DATABASE,
        url_manager=BrookingsURLManager()
    ).run()
