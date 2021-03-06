#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: serializers.py
@time: 2018/09/01
"""
import re

from rest_framework import serializers, status
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from goods.models import SKU
from users import constants
from users.utils import generate_save_user_token
from celery_tasks.mail.tasks import send_verify_email

from users.models import Users, Address


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


class EmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = ['id', 'email']
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        # 保存邮箱地址
        instance.email = validated_data["email"]
        instance.save()

        # 生成邮箱验证链接
        verify_url = generate_save_user_token(instance)

        # 调用异步方法
        send_verify_email.delay(instance.email, verify_url)

        return instance


class UserAddressSerializer(serializers.ModelSerializer):

    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context["request"].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ['title']


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(label='确认密码', write_only=True)
    new_password = serializers.CharField(label='确认密码', write_only=True)
    new_password2 = serializers.CharField(label='确认密码', write_only=True)

    def validate(self, attrs):
        # 判断密码是否一致
        print(attrs)
        password = attrs.get('new_password')
        password2 = attrs.get('new_password2')
        if password != password2:
            raise serializers.ValidationError("两次密码输入不一致")

        return attrs

    def update(self, instance, validated_data):
        print(789)
        print(validated_data['password'])
        print(instance.check_password(validated_data['password']))
        if not instance.check_password(validated_data['password']):

            raise serializers.ValidationError("密码错误")
        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance


class AddUserBrowsingHistorySerializer(serializers.Serializer):

    sku_id = serializers.IntegerField(label="商品SKU编号", min_value=1)

    def validate_sku_id(self, value):
        try:
            sku = SKU.objects.get(pk=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("用户信息不存在")
        return value

    def create(self, validated_data):
        redis = get_redis_connection('history')
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']

        pl = redis.pipeline()
        pl.lrem('history_%s' % user_id, 0, sku_id)
        pl.lpush('history_%s' % user_id, sku_id)
        pl.ltrim('history_%s' % user_id, 0, constants.USER_BROWSING_HISTORY_COUNT_LIMIT-1)
        pl.execute()

        return validated_data
