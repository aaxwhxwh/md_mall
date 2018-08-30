#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: tasks.py
@time: 2018/08/30
"""
from .yuntongxun.sms import CCP
from . import constants
from celery_tasks.main import app


@app.task(name="send_sms_code")
def send_sms_code(mobile, sms_code):
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)

    pass