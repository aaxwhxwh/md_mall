#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: urls.py
@time: 2018/09/14
"""
from django.conf.urls import url

from payments import views

urlpatterns = [
    url(r'^orders/(?P<order_id>\d+)/payment/$', views.PaymentView.as_view()),
    url(r'payment/status/$', views.PaymentStatusView.as_view()),
]
