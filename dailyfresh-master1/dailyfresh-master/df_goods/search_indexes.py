# -*-coding:utf-8-*-

from haystack import indexes
from df_goods.models import Goods


# 指定对于某个类的某些数据建立索引
class GoodsIndex(indexes.SearchIndex, indexes.Indexable):
    # text是索引字段
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Goods

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
