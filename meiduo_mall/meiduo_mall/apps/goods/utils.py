#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: utils.py
@time: 2018/09/08
"""

from goods.models import GoodsChannel
from collections import OrderedDict


def get_categories():
    categories = OrderedDict()
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')

    # 查询结果分组保存
    for channel in channels:
        group_id = channel.group_id

        if group_id not in categories:
            categories[group_id] = {'sub_cats': [], 'channels': []}

        cat_1 = channel.category

        categories[group_id]['channels'].append({
            'id': cat_1.id,
            'name': cat_1.name,
            'url': channel.url
        })

        # 查询并添加二级以及三级商品分类
        for cat_2 in cat_1.goodscategory_set.all():
            cat_2.sub_cats = []
            # 根据二级分类查询三级分类
            for cat_3 in cat_2.goodscategory_set.all():
                cat_2.sub_cats.append(cat_3)
            categories[group_id]['sub_cats'].append(cat_2)

    return categories
