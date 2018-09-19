#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: utils.py
@time: 2018/09/11
"""
import pickle
import base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    """
    当用户登陆后，对cookie内的购物车信息同步至redis数据库
    :param request: 本次登陆成功后的请求对象
    :param user: 登陆用户信息，用来获取redis内购物车
    :param response: 本次请求的响应对象
    :return: response 相应对象
    """
    # 获取cookie中购物车
    cookie_cart = request.COOKIES.get('cart')
    # 判断是否为空，为空则返回响应对象
    if not cookie_cart:
        return response
    print(123)
    cookie_cart = pickle.loads(base64.b64decode(cookie_cart.encode()))
    print(cookie_cart)

    redis = get_redis_connection('cart')
    pl = redis.pipeline()
    for sku_id, sku_dict in cookie_cart.items():
        pl.hset("cart_%s" % user.id, int(sku_id), int(sku_dict["count"]))
        if sku_dict["selected"]:
            pl.sadd("cart_selected_%s" % user.id, sku_id)
        else:
            pl.srem("cart_selected_%s" % user.id, sku_id)
    pl.execute()

    response.delete_cookie("cart")

    return response
