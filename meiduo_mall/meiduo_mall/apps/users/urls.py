#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: urls.py
@time: 2018/09/01
"""
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from users import views

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5, 20})/count/$', views.UsernameCountView.as_view()),
    url(r'users/$', views.CreateUser.as_view()),
    url(r'authorizations/$', obtain_jwt_token),
]