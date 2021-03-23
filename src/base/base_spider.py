"""
BaseSpider定义文件
"""

from abc import ABC, abstractmethod
from typing import Union

from .base_url_manager import BaseURLManager
from .utilities import *


class BaseSpider(ABC):
    """
    从URLManager处获取url并解析，将内容存储到本地
    """

    def __init__(self, server: str, database: str, url_manager: BaseURLManager, maximum=-1):
        """
        :param server: mysql服务器
        :param database: 数据库名称
        :param url_manager: URL管理器
        :param maximum: 爬取的最大文章数，默认为无穷
        """
        self._logger = get_logger(self.__class__.__name__)
        self.maximum = maximum
        self._url_manage = url_manager
        self.dl = DataLoader(server, database)

    def run(self):
        self._logger.debug('Started running')
        # 开启url管理器
        self._url_manage.run()
        cnt = 0
        # 循环爬取
        while True:

            # 达到最大爬取数时退出
            if cnt == self.maximum:
                self._logger.debug('Counted to maximum')
                break
            # 当url管理器为空时，分情况讨论
            elif self._url_manage.is_empty:
                # url管理器还在工作，等待其填充url
                if self._url_manage.is_working:
                    while self._url_manage.is_empty:
                        pass
                # 没有在工作，说明已没有内容可供爬取，退出
                else:
                    self._logger.debug(f'No resources are available')
                    break

            url = self._url_manage.new_url()
            self._logger.debug(f'New url: {url}')
            try:
                atc = self.parse(url)
            except Exception as e:
                self._logger.error(e)
                continue
            # 将结果写入数据库
            if atc is not None:
                self.dl.insert(atc)
                cnt += 1

        self._logger.debug('Done')

    @abstractmethod
    def parse(self, url) -> Union[Article, None]:
        """
        :param url: 文档url
        :return: Article
        """
        pass

