#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: crons.py
@time: 2018/09/07
"""
from collections import OrderedDict
from django.conf import settings
from django.template import loader

import time
import os

from contents.models import ContentCategory
from goods.utils import get_categories


def generate_static_index_html():
    """生成静态主页html文件"""
    print('%s: generate_static_index_html' % time.ctime())

    '''
    1. 获取数据
        1.1 获取商品分类
        1.2 获取广告数据
    2. 获取模板
    
    3. 填充数据
    
    4. 页面文件存储
    '''

    # 保存商品分类信息(商品频道）

    categories = get_categories()

    # 获取广告数据
    contents = OrderedDict()
    content_categories = ContentCategory.objects.all()
    # 根据分类查询广告数据
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 填充数据
    context = {
        'categories': categories,
        'contents': contents
    }
    template = loader.get_template('index.html')
    print(template)
    html_text = template.render(context)

    # 保存页面
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILE_DIR, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
