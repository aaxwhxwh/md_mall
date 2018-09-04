from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from meiduo_mall.utils.exceptons import logger
from users.models import Users
from users.serializers import CreateUserSerializer, EmailSerializer
from users.utils import get_save_user_token


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


class UserDetailView(APIView):
    """获取用户详情信息"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "mobile": user.mobile,
            "email": user.email,
            "email_active": user.email_active,
        })


class SendEmailView(UpdateAPIView):
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, *args, **kwargs):
        return self.request.user


class VerifyEmailView(APIView):
    """验证邮箱激活链接"""
    def get(self, request):
        try:
            token = request.query_params.get('token')
        except Exception:
            return Response({'message': "token失效"}, status=status.HTTP_404_NOT_FOUND)
        user_id = get_save_user_token(token)
        if not user_id:
            return Response({"message": "无效的token"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            return Response({"message": "无效的token"}, status=status.HTTP_404_NOT_FOUND)

        user.email_active = True
        user.save()

        return Response({"message": "邮箱验证成功"}, status=status.HTTP_200_OK)
