# __author__ = itsneo1990
import logging

import requests
from collections import Iterable

logger = logging.getLogger(__name__)


class BaseComponent(object):

    def __init__(self, site_id, name, user_center_url, setting_url):
        print(self.__class__)
        self.site_id = site_id
        self.name = name

        self.user_center_url = user_center_url  # 账号中心
        self.setting_url = setting_url  # 设置

        self.title = None
        self.exists_url = ""
        self.post_sources = (("", None),)
        self.delete_sources = []

    def process(self):
        try:
            if not any((self.post_sources, self.title)):
                raise NotImplementedError("必须指定post_sources, title")

            if self.exists_url:
                if isinstance(self.exists_url, str):
                    resp = self.get_remote_data(self.exists_url)
                    code = resp.get("code", None) or resp.get("status", None)
                    if code == 200:
                        return self.error_response(f"{self.title}已存在:\n{self.exists_url}")
                elif isinstance(self.exists_url, Iterable):
                    for each in self.exists_url:
                        resp = self.get_remote_data(each)
                        code = resp.get("code", None) or resp.get("status", None)
                        if code == 200:
                            return self.error_response(f"{self.title}已存在:\n{each}")
                else:
                    return self.error_response("exists_url不合法")
            for each in self.post_sources:
                resp = self.post_remote_data(each[0], each[1])
                code = resp.get("code", None) or resp.get("status", None)
                if not code == 200:
                    return self.error_response(f"执行失败-->{self.title}\n{resp['message']}")
        except Exception:
            return self.error_response(f"执行失败-->{self.title}\n{resp['message']}")
        else:
            return self.success_response(f"执行成功-->{self.title}")

    def rollback(self):
        for each in self.delete_sources:
            requests.delete(url=each, timeout=10)

    @staticmethod
    def post_remote_data(url: str, data) -> dict:
        print(url, data)
        try:
            resp = requests.post(url=url, json=data, timeout=10, headers={"token": "dataMigration"})
            print(resp.json())
            return resp.json()
        except requests.ConnectTimeout:
            logger.error(msg=f"POST连接超时: {url}")
            raise

    @staticmethod
    def get_remote_data(url: str) -> dict:
        print(url)
        try:
            resp = requests.get(url=url, timeout=5)
            print(resp.json())
            return resp.json()
        except requests.ConnectTimeout:
            logger.error(msg=f"GET连接超时: {url}")
            raise

    @staticmethod
    def error_response(msg: str = "") -> tuple:
        logger.error(msg=msg)
        return False, msg

    @staticmethod
    def success_response(msg: str = "") -> tuple:
        logger.info(msg=msg)
        return True, msg
