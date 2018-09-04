#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: tasks.py
@time: 2018/09/04
"""
from celery_tasks.main import app
from django.core.mail import send_mail
from django.conf import settings


@app.task(name="send_verify_email")
def send_verify_email(user_email, verify_url):
    """
    发送邮箱验证邮件
    :param user_email: 用户邮箱
    :param verify_url: 邮箱验证链接
    :return:
    """
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (user_email, verify_url, verify_url)
    send_mail(subject, '', settings.EMAIL_FROM, [user_email], html_message=html_message)

