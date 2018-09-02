#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: serializers.py
@time: 2018/09/02
"""
from rest_framework import serializers

from users.models import Users


class QQOauthSerializer(serializers.ModelSerializer):

    code = serializers.CharField(max_length=64, write_only=True, required=True, help_text="用户授权码")
    token = serializers.CharField(read_only=True, help_text="登陆状态验证码")

    class Meta:
        models = Users
        fields = ['username', 'code', 'token', 'id']
