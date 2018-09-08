#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: urls.py
@time: 2018/09/08
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^categories/(?P<pk>\d+)/$', views.CategoryView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/skus', views.SKUListView.as_view()),
]