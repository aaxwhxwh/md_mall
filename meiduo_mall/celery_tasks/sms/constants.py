#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: constants.py
@time: 2018/08/30
"""
# 短信验证码过期时间
SMS_CODE_REDIS_EXPIRES = 300

# 短信发送模板
SEND_SMS_TEMPLATE_ID = 1

# 允许再次发送短信间隔时间
SMS_FLAG_REDIS_EXPIRES = 60