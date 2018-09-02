#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: urls.py
@time: 2018/09/02
"""
from django.conf.urls import url

from oauth import views

urlpatterns = [
    url(r'oauth/qq/authorization/$', views.QQAuthURLView.as_view()),
    url(r'oauth/qq/user/$', views.QQAuthUserView.as_view()),
]