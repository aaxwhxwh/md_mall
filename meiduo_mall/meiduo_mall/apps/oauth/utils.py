#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: utils.py
@time: 2018/09/02
"""
from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings


def generate_save_user_token(openId):
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
    data = {"openid": openId}
    token = serializer.dumps(data)

    return token