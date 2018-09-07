#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: fdfs_storage.py
@time: 2018/09/07
"""
from django.core.files.storage import Storage
from django.conf import settings
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client


@deconstructible
class FastDFSStorage(Storage):
    """自定义文件存储系统"""
    def __init__(self, base_url=None, client_conf=None):

        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url

        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

    def open(self, name, mode='rb'):
        pass

    def save(self, name, content, max_length=None):
        client = Fdfs_client(self.client_conf)

        ret = client.upload_by_buffer(content.read())
        if ret.get("Status") != "Upload successed.":
            raise Exception("upload file failed")

        file_name = ret.get("Remote file_id")
        return file_name

    def url(self, name):
        return self.base_url + name

    def exists(self, name):
        return False
