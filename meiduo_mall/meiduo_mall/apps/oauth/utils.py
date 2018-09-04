#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: utils.py
@time: 2018/09/02
"""
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadData
from django.conf import settings


def generate_save_user_token(openId):
    serializer = Serializer(settings.SECRET_KEY, 300)
    data = {"openid": openId}
    token = serializer.dumps(data)

    return token


def check_user_token(access_token):
    """使用itsdangerous验证并提取openid"""
    serializer = Serializer(settings.SECRET_KEY, 300)
    try:
        data = serializer.loads(access_token)
    except BadData:
        return None
    else:
        return data['openid']
