# -*- coding: utf-8 -*-
""" 
@version: v1.0 
@author: andy 
@license: Apache Licence  
@contact: 93226042@qq.com 
@site:  
@software: PyCharm 
@file: search_indexes.py 
@time: 2018/10/14 12:15 
"""
from haystack import indexes
from .models import Product

#指定对于某个类的某些数据建立索引

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        return  self.get_model().objects.all()
