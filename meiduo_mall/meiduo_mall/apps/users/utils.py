#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: utlis.py
@time: 2018/09/02
"""
import re

from django.contrib.auth.backends import ModelBackend

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
