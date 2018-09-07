#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: serializers.py
@time: 2018/09/05
"""

from rest_framework import serializers

from areas.models import Area


class AreaSerializer(serializers.ModelSerializer):
    """行政区划序列化器"""
    class Meta:
        model = Area
        fields = ['id', 'name']


class SubAreaSerializer(serializers.ModelSerializer):
    """地级市和区县序列化器"""
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
