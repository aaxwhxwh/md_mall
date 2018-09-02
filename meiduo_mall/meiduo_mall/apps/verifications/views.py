import random, logging
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from utils.exceptons import logger
from meiduo_mall.utils.exceptons import logger
from users.models import Users
from . import constants
from celery_tasks.sms.tasks import send_sms_code

# Create your views here.
er = logging.getLogger("django")


class SMSCodeView(APIView):
    """发送短信"""

    """
    1. 生成和发送短信验证码
    2. 保存短信验证码
    3. 
    """

    def get(self, request, mobile):
        # 获取redis连接对象
        redis = get_redis_connection('verify')
        sms_flag = redis.get('sms_flag_%s' % mobile)
        if sms_flag:
            return Response({"message": "发送短信太频繁"}, status=status.HTTP_400_BAD_REQUEST)

        # 生成和发送短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        try:
            send_sms_code.delay(mobile, sms_code)
        except Exception as e:
            logger.error("发送短信失败 %s: %s" % (mobile, sms_code), status=status.HTTP_502_BAD_GATEWAY)
            return Response()
        logger.debug("%s: %s" % (mobile, sms_code))

        # 保存短信验证码
        pl = redis.pipeline()       # 管道对象，可以在创建管道对象后多次执行redis读取操作后统一提交
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("sms_flag_%s" % mobile, constants.SMS_FLAG_REDIS_EXPIRES, 1)
        pl.execute()    # 管道对象需手动提交

        return Response({"message": "发送成功"})


class MobileCountView(APIView):
    """验证手机号是否已注册"""

    def get(self, request, mobile):
        try:
            count = Users.objects.filter(mobile=mobile).count()
        except Exception as e:
            logger.error("数据库查询失败:%s" % mobile)
            return Response()

        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data)