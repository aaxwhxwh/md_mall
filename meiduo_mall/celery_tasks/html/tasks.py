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
from goods.utils import get_categories


@app.task(name="generate_static_list_html")
def generate_static_list_html():
    """生成商品列表静态化页面"""

    categories = get_categories()

    context = {
        "categories": categories
    }

    template = loader.get_template('list.html')

    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILE_DIR, 'list.html')
    with open(file_path, 'w') as f:
        f.write(html_text)
