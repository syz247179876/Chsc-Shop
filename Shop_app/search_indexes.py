# -*- coding: utf-8 -*- 
# @Time : 2020/6/2 15:38 
# @Author : 司云中 
# @File : search_indexes.py 
# @Software: PyCharm
from Shop_app.models.commodity_models import Commodity
from haystack import indexes


class CommodityIndex(indexes.SearchIndex, indexes.Indexable):
    """
    定义关于Note的haystack搜索引擎
    """
    # document 表示该字段主要用于关键字查询的主要字段
    # use_Template表示该字段将从模板中指明
    text = indexes.CharField(document=True, use_template=True)
    # model_attr表明能让搜索引擎识别的额外字段，用来检索参照数据表中的字段值
    commodity_name = indexes.CharField(model_attr='commodity_name')
    shopper = indexes.CharField(model_attr='shopper')

    def get_model(self):
        # 返回建立索引的模型类
        return Commodity

    def index_queryset(self, using=None):
        # 返回建立索引的数据查询集
        return self.get_model().commodity_.all()
