# -*- coding: utf-8 -*-
""" 
@version: v1.0 
@author: andy 
@license: Apache Licence  
@contact: 93226042@qq.com 
@site:  
@software: PyCharm 
@file: myrouter.py 
@time: 2018/11/29 16:11 
"""
import random

#对网站的数据库作读写分离（Read/Write Splitting）可以提高性能
class Router:
    def db_for_read(self, model, **hints):
        """
        读取时随机选择一个数据库
        """
        return random.choice(['slave1', 'slave2'])

    def db_for_write(self, model, **hints):
        """
        写入时选择主库
        """
        return 'default'

    def allow_relation(self, obj1,obj2, **hints):
        """
        允许关联查询
        """
        return True