"""
工具库
"""

from random import choice
from json import load, dumps
from warnings import simplefilter
from urllib.request import getproxies
import logging

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests import get, Session




def get_html(url: str, headers_args: dict = None) -> bytes:
    """
    解析url获得html
    :param url: 待解析URL字符串
    :return: url对应的二进制html
    :param headers_args: 请求头附加参数
    """
    # 初次使用，配置session
    if not hasattr(get_html, 'session'):
        simplefilter('ignore', InsecureRequestWarning)
        # with open('base\\utilities\\user_agents.json', 'r') as f:
        with open('base\\utilities\\user_agents.json', 'r') as f:
            ua = choice(load(f)['user-agents'])
        headers = {'user-agent': ua}
        if headers_args is not None:
            headers.update(headers_args)
        session = Session()
        session.headers.update(headers)
        session.verify = False
        get_html.session = session
    proxies = getproxies()
    if 'https' in proxies.keys():
        proxies['https'] = proxies['https'].replace('s', '')
    html = get_html.session.get(url, proxies=proxies).content
    return html


def letters(str_: str) -> str:
    """
    过滤字符串中的其他字符，只保留字母
    :param str_: 待过滤字符串
    :return: 过滤后的字符串
    """
    return ''.join(filter(str.isalpha, str_))


def post_html(url: str, data, headers_args: dict = None) -> bytes:
    """
    发送post请求并接收response
    :param url: request的url字符串
    :param data: request的body文件
    :param headers_args: 请求头附加参数
    :return:
    """
    # 初次使用，配置session
    if not hasattr(post_html, 'session'):
        simplefilter('ignore', InsecureRequestWarning)
        with open('base\\utilities\\user_agents.json', 'r') as f:
            ua = choice(load(f)['user-agents'])
        headers = {'user-agent': ua}
        if headers_args is not None:
            headers.update(headers_args)
        session = Session()
        session.headers.update(headers)
        session.verify = False
        get_html.session = session
    proxies = getproxies()
    if 'https' in proxies.keys():
        proxies['https'] = proxies['https'].replace('s', '')
    html = get_html.session.post(url, proxies=proxies, data=dumps(data)).content
    return html
