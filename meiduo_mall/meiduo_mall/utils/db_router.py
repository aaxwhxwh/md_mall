#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: db_router.py
@time: 2018/09/14
"""
from goods.models import SKU
from users.models import Users


class MasterSlaveDBRouter(object):

    def db_for_read(self, model, **hints):
        # if isinstance(model, SKU):
        #     return "slave_sku"
        # elif isinstance(model, Users):
        #     return "slave_user"
        return "slave"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True