#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: urls.py
@time: 2018/09/11
"""
from django.conf.urls import url

from carts import views

urlpatterns = [
    url(r'^cart/$', views.CartView.as_view()),
    url(r'^cart/selection/$', views.CancelSelectedView.as_view())
]