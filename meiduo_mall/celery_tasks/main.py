#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: main.py
@time: 2018/08/30
"""
from celery import Celery
import os

app = Celery("hello")

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = "meiduo_mall.settings.dev"

# 加载配置
app.config_from_object("celery_tasks.config")

# 声明获取异步任务的队列[目录中必须有一个tasks.py]
app.autodiscover_tasks(['celery_tasks.sms'])
