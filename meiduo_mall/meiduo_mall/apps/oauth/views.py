from django.shortcuts import render
from QQLoginTool.QQtool import OAuthQQ
# Create your views here.
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from rest_framework_jwt.settings import api_settings

from oauth.serializers import QQOauthSerializer
from oauth.utils import generate_save_user_token

from oauth.models import OauthUser


class QQAuthURLView(APIView):
    def get(self, request):
        # 获取登陆后转跳地址
        next = request.query_params.get('next', '/')
        # 使用qqLoginTool工具包生成转跳url
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URL,
            state=next
        )
        login_url = oauth.get_qq_url()
        return Response({"login_url": login_url})


class QQAuthUserView(GenericAPIView):
    serializer_class = QQOauthSerializer

    def get(self, request):
        # 获取code
        code = request.query_params.get('code')
        if not code:
            return Response({'message': "缺少授权码"}, status=status.HTTP_400_BAD_REQUEST)

        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URL,
            state=next
        )
        # 获取access_token
        access_token = oauth.get_access_token(code)
        # 获取openid
        openId = oauth.get_open_id(access_token)

        # 根据openId到数据库查询是否有绑定用户
        try:
            oauth_user = OauthUser.objects.get(openid=openId)
        except OauthUser.DoesNotExist:
            access_token = generate_save_user_token(openId)
            return Response({
                "access_token": access_token
            })
        else:
            # 补充生成记录登录状态的token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            user = oauth_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            user.token = token

            data = {
                "token": token,
                "user_id": user.id,
                "username": user.username
            }
            return Response(data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return Response({
            "token": token,
            "user_id": user.id,
            "username": user.username
        })
