#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: search_indexes.py
@time: 2018/09/10
"""
from haystack import indexes

from goods.models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    # 设置请求搜索时的参数名称和格式要求
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回搜索使用的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """设置索引查询范围"""
        return self.get_model().objects.filter(is_launched=True)
