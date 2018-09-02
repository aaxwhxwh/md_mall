from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from meiduo_mall.utils.exceptons import logger
from users.models import Users
from users.serializers import CreateUserSerializer


class UsernameCountView(APIView):
    """验证用户名是否已注册"""

    def get(self, request, username):
        try:
            count = Users.objects.filter(username=username).count()
        except Exception as e:
            logger.error('数据库查询失败%s' % username)
            return Response({"message": "数据库查询失败"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "username": username,
            "count": count
        }
        return Response(data)


class CreateUser(CreateAPIView):
    """注册用户"""

    serializer_class = CreateUserSerializer
