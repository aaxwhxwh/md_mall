#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: serializers.py
@time: 2018/09/08
"""
from rest_framework import serializers

from goods.models import SKU


class GoodsCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True, label="分类编号")
    name = serializers.CharField(read_only=True, label="分类名称")


class ChannelSerializer(serializers.Serializer):

    url = serializers.CharField(read_only=True, label="连接")
    category = GoodsCategorySerializer()


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']

