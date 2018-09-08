#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: pagination.py
@time: 2018/09/08
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):

    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 20
