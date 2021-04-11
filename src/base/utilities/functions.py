"""
工具库
"""

from random import choice
from json import load, dumps
from urllib.request import getproxies
import pikepdf

from requests import Session
from pdfminer.high_level import extract_text

from config import user_agents_path, temp_pdf_path
from base.utilities.logger import Logger

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def pdf2text(pdf_url: str) -> str:
    """提取PDF文件中的字符串

    Args:
        pdf_url (str): PDF文件的下载地址

    Returns:
        str: 提取出的字符串
    """
    Logger(pdf2text.__name__).debug(f'new pdf url: {pdf_url}')
    with open(temp_pdf_path, 'wb') as f:
        f.write(get_html(pdf_url))
    pikepdf.open(temp_pdf_path, allow_overwriting_input=True).save(temp_pdf_path)
    with open(temp_pdf_path, 'rb') as f:
        text = extract_text(f)
    return text


def get_html(url: str, headers_args: dict = None) -> bytes:
    """
    解析url获得html
    :param url: 待解析URL字符串
    :return: url对应的二进制html
    :param headers_args: 请求头附加参数
    """
    # 初次使用，配置session
    if not hasattr(get_html, 'session'):
        # with open('base\\utilities\\user_agents.json', 'r') as f:
        with open(user_agents_path, 'r') as f:
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


def post_html(url: str, data, headers_args: dict = None, is_json = True) -> bytes:
    """
    发送post请求并接收response
    :param url: request的url字符串
    :param data: request的body文件
    :param headers_args: 请求头附加参数
    :param is_json: request的body文件是json格式
    :return:
    """
    # 初次使用，配置session
    if not hasattr(post_html, 'session'):
        with open(user_agents_path, 'r') as f:
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
    if is_json is True:
        html = get_html.session.post(url, proxies=proxies, data=dumps(data)).content
    else:
        html = get_html.session.post(url, proxies=proxies, data=data).content
    return html
