#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: serializers.py
@time: 2018/09/01
"""
import re

from rest_framework import serializers
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings

from users.models import Users


class CreateUserSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='jwt_token', read_only=True)

    class Meta:
        model = Users
        fields = ['token', 'id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow']
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_allow(self, value):

        if value != 'true':
            raise serializers.ValidationError("请确认同意用户协议")

        return value

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式输入有误')

        count = Users.objects.filter(mobile=value).count()
        if count:
            raise serializers.ValidationError('手机号已注册')

        return value

    # 校验参数
    def validate(self, attrs):
        print(attrs)
        # 判断密码是否一致
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("两次密码输入不一致")

        # 判断短信验证码是否正确
        mobile = attrs.get('mobile')
        sms_code = attrs.get('sms_code')
        redis = get_redis_connection('verify')
        redis_sms_code = redis.get('sms_%s' % mobile)
        print(mobile)
        print(redis_sms_code)
        try:
            redis_sms_code = redis_sms_code.decode()
        except Exception as e:
            raise serializers.ValidationError('短信验证码已过期')
        if sms_code != redis_sms_code:
            raise serializers.ValidationError("验证码不正确")

        return attrs

    # 创建及更改用户信息
    def create(self, validate_data):
        del validate_data['sms_code']
        del validate_data['password2']
        del validate_data['allow']
        user = super().create(validate_data)
        user.set_password(validate_data['password'])
        user.save()

        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user
