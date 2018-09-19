#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: tasks.py
@time: 2018/09/08
"""
import os

from django.conf import settings
from django.template import loader

from celery_tasks.main import app
from goods.models import SKU
from goods.utils import get_categories


@app.task(name="generate_static_list_html")
def generate_static_list_html():
    """生成商品列表静态化页面"""

    # 商品分类菜单
    categories = get_categories()

    # 渲染模板，生成静态html文件
    context = {
        'categories': categories,
    }

    template = loader.get_template('list.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILE_DIR, 'list.html')
    with open(file_path, 'w') as f:
        f.write(html_text)

    template = loader.get_template('search.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILE_DIR, 'search.html')
    with open(file_path, 'w') as f:
        f.write(html_text)


@app.task(name="generate_static_good_html")
def generate_static_good_html(sku_id):

    categories = get_categories()

    sku = SKU.objects.get(pk=sku_id)
    sku.images = sku.skuimage_set.all()

    # 获取SPU信息
    goods = sku.goods
    goods.channel = goods.category1.goodschannel_set.all()[0]

    sku_specs = sku.skuimage_set.order_by('spec_id')
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    skus = goods.sku_set.all()

    spec_sku_map = {}
    for s in skus:
        s_specs = s.skuspecification_set.order_by('spec_id')
        key = []
        for spec in s_specs:
            key.append(spec.option.id)

        spec_sku_map[tuple(key)] = s.id

    specs = goods.goodsspecification_set.order_by('id')

    if len(sku_key) < len(specs):
        return
    for index, spec in enumerate(specs):
        key = sku_key[:]
        options = spec.specificationoption_set.all()
        for option in options:
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))

        spec.options = options

    context = {
        'categories': categories,
        'goods': goods,
        'specs': specs,
        'sku': sku
    }

    template = loader.get_template('detail.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILE_DIR, 'goods/'+str(sku_id)+'.html')
    with open(file_path, 'w') as f:
        f.write(html_text)
