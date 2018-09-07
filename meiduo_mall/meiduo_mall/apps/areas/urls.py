#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: urls.py
@time: 2018/09/05
"""
from rest_framework.routers import DefaultRouter, SimpleRouter
from . import views

urlpatterns = []

router = DefaultRouter()

router.register(r'areas', views.AreasViewSet, 'area')

urlpatterns += router.urls
