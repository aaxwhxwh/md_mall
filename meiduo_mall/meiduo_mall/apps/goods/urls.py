#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: urls.py
@time: 2018/09/08
"""
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    url(r'^categories/(?P<pk>\d+)/$', views.CategoryView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/skus', views.SKUListView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUSListView.as_view())
]

router = DefaultRouter()

router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls
