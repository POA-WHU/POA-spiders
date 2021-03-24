"""
BaseURLManager定义文件
"""

from threading import Thread
from abc import ABC, abstractmethod

from .utilities import Logger


class BaseURLManager(ABC):
    """
    从目录页获取文章URL，为Spider提供待爬取的URL
    """

    def __init__(self, start_page=1, end_page=-1):
        """
        初始化
        注意：每个目录页包含多个url
        :param start_page:开始目录页码
        :param end_page:结束目录页码, 默认为无穷
        """
        self._logger = Logger(self.__class__.__name__)
        self.start_page = start_page
        self.end_page = end_page
        # url队列
        self.queue = list()
        # 工作状态
        self.is_working = False

    @property
    def is_empty(self) -> bool:
        """
        :return: URL队列是否为空
        """
        return len(self.queue) == 0

    def new_url(self):
        """
        :return: 队首url
        """
        if self.is_empty:
            self._logger.warning('Get url from an empty queue.')
            return None
        else:
            return self.queue.pop(0)

    def run(self):
        """
        新开线程爬取可用url，不影响主线程运行
        :return:
        """
        self.is_working = True
        self._logger.debug('Started running')
        Thread(target=self._gather_urls, daemon=True).start()

    def _gather_urls(self):
        """
        私有方法，不可被外部调用
        :return:
        """
        # 记录当前正在爬取的目录页
        page_cnt = self.start_page
        while page_cnt != self.end_page:
            self._logger.debug(f'Parsing page {page_cnt}')
            page_cnt += 1
            # 解析目录页，获取文档url

            try:
                urls = self.parse(page_cnt)
            except Exception as e:
                self._logger.error(e)
                continue
            # 返回空列表，说明已到达无效目录页，退出循环
            if len(urls) == 0:
                break
            # 将文档url存入队列
            for i in urls:
                self.queue.append(i)
        self.is_working = False
        self._logger.debug('Done')

    @abstractmethod
    def parse(self, page_cnt) -> list:
        """
                :param page_cnt: 页码
                :return: 文档url列表
                """
        pass
