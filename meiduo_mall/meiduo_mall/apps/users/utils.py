#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: utlis.py
@time: 2018/09/02
"""
import re

from django.contrib.auth.backends import ModelBackend
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings

from users import constants
from users.models import Users


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt返回前端的数据内容
    :param token: jwt生成的token对象
    :param user:当前登录用户信息
    :param request:本次请求信息
    :return:
    """

    return {
        "username": user.username,
        "user_id": user.id,
        "token": token
    }


def get_user_by_account(account):
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = Users.objects.filter(mobile=account).get()
        else:
            user = Users.objects.filter(username=account).get()
    except Users.DoseNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """

        :param request:
        :param username:用户输入的登陆账号信息
        :param password:
        :param kwargs:
        :return:
        """
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user


def generate_save_user_token(user):
    serializer = Serializer(settings.SECRET_KEY, constants.EMAIL_VERIFY_TOKEN_EXPIRE)
    data = {"user_id": user.id}
    token = serializer.dumps(data)
    token = token.decode()

    verify_url = settings.VERIFY_EMAIL_HTML + "?token=" + token

    return verify_url


def get_save_user_token(token):
    serializer = Serializer(settings.SECRET_KEY, constants.EMAIL_VERIFY_TOKEN_EXPIRE)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        return data['user_id']

