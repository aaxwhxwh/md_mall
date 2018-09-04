#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: serializers.py
@time: 2018/09/02
"""
from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OauthUser
from oauth.utils import check_user_token
from users.models import Users


class QQOauthSerializer(serializers.Serializer):

    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate_access_token(self, value):
        openid = check_user_token(value)
        if not openid:
            raise serializers.ValidationError({"message": "access_token无效"})
        return openid

    def validate(self, data):
        mobile = data["mobile"]
        sms_code = data["sms_code"]
        redis = get_redis_connection('verify')
        redis_sms_code = redis.get('sms_%s' % mobile)
        print(123)
        try:
            redis_sms_code = redis_sms_code.decode()
        except Exception as e:
            raise serializers.ValidationError({"message": "短信验证码已过期"})

        if sms_code != redis_sms_code:
            raise serializers.ValidationError({"message": "短信验证码错误"})

        try:
            user = Users.objects.get(mobile=mobile)
        except Users.DoseNotExist:
            data["user"] = None
        else:
            if not user.check_password(data['password']):
                raise serializers.ValidationError({"message": "用户密码错误"})
            else:
                data["user"] = user
        return data

    def create(self, validate_data):
        user = validate_data['user']
        if not user:
            Users.objects.create(
                mobile=validate_data['mobile'],
                username=validate_data['mobile'],
                password=validate_data['password']
            )
            user.set_password(validate_data['password'])
            user.save()

        OauthUser.objects.create(
            openid=validate_data['access_token'],
            user=user
        )

        return user
