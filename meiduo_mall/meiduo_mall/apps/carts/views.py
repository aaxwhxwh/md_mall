import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from carts import constants
from carts.serializers import CartSerializer, CartSKUSerializer, DelCartSerializer, CancelSelectedSerializer
from goods.models import SKU


class CartView(APIView):

    def perform_authentication(self, request):
        """重写父类方法，验证登陆信息"""
        pass

    def post(self, request):
        """添加商品到购物车"""
        # 调用序列化器校验数据
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 判断用户登陆状态
        try:
            user = request.user
        except Exception:
            user = None

        # 如果已登陆，将数据保存至redis
        if user and user.is_authenticated:
            # 连接数据库
            redis = get_redis_connection('cart')

            pl = redis.pipeline()

            # 保存商品sku_id及数量
            pl.hincrby("cart_%s" % user.id, sku_id, count)
            # 保存商品勾选状态
            pl.sadd("cart_selected_%s" % user.id, sku_id)
            pl.execute()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # 如果未登录，则将商品信息保存在cookie
        else:
            # 获取cookie中购物车数据
            cart = request.COOKIES.get('cart')
            if cart:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            # 添加购物信息
            sku_dict = cart.get(sku_id)
            if sku_dict:
                count += int(sku_dict["count"])
            cart[sku_id] = {
                "count": count,
                "selected": selected,
            }
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie("cart", cookie_cart, max_age=constants.CART_COOKIE_EXPIRE)
            return response

    def get(self, request):
        """获取购物车列表"""
        # 判断用户登陆状态
        try:
            user = request.user
        except Exception:
            user = None

        # 如果已登陆，从redis取回购物车信息
        if user and user.is_authenticated:
            redis = get_redis_connection('cart')
            redis_cart = redis.hgetall('cart_%s' % user.id)
            redis_cart_selected = redis.smembers('cart_selected_%s' % user.id)
            cart = {}
            for sku_id, count in redis_cart.items():

                cart[int(sku_id)] = {
                    "count": int(count),
                    "selected": sku_id in redis_cart_selected
                }

        # 未登录状态，从cookie取回购物车信息
        else:
            cart = request.COOKIES.get('cart')
            if cart:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]["count"]
            sku.selected = cart[sku.id]["selected"]

        serializer = CartSKUSerializer(instance=skus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """修改购物车"""
        # 调用序列化器校验数据
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 判断用户登陆状态
        try:
            user = request.user
        except Exception:
            user = None

        # 如果已登陆，从redis取回购物车信息
        if user and user.is_authenticated:
            # 连接数据库
            redis = get_redis_connection('cart')

            pl = redis.pipeline()
            pl.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            # 获取cookie中购物车数据
            cart = request.COOKIES.get('cart')
            if cart:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            # 添加购物信息
            cart[sku_id] = {
                "count": count,
                "selected": selected,
            }
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie("cart", cookie_cart, max_age=constants.CART_COOKIE_EXPIRE)
            return response

    def delete(self, request):
        """删除购物车"""
        serializer = DelCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')

        # 判断用户登陆状态
        try:
            user = request.user
        except Exception:
            user = None

        # 如果已登陆，从redis取回购物车信息
        if user and user.is_authenticated:
            # 连接数据库
            redis = get_redis_connection('cart')

            redis.hdel('cart_%s' % user.id, sku_id)
            redis.srem('cart_selected_%s' % user.id, sku_id)
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            cart = request.COOKIES.get('cart')
            if cart:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                if sku_id in cart:
                    del cart[sku_id]

                    cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                    response = Response(serializer.data, status=status.HTTP_201_CREATED)
                    response.set_cookie("cart", cookie_cart, max_age=constants.CART_COOKIE_EXPIRE)

            return response


class CancelSelectedView(APIView):

    def perform_authentication(self, request):
        """重写父类方法，验证登陆信息"""
        pass

    def put(self, request):
        # 调用序列化器校验数据
        serializer = CancelSelectedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data.get('selected')

        # 判断用户登陆状态
        try:
            user = request.user
        except Exception:
            user = None
        # 获取所有
        redis = get_redis_connection('cart')
        # 如果已登陆，从redis取回购物车信息
        if user and user.is_authenticated:
            if not selected:
                redis.delete('cart_selected_%s' % user.id)
            else:
                redis_cart = redis.hgetall('cart_%s' % user.id)
                for sku_id, count in redis_cart.items():
                    # 保存商品勾选状态
                    redis.sadd("cart_selected_%s" % user.id, sku_id)

            return Response({"message": "OK"})
        else:
            cart = request.COOKIES.get('cart')
            for sku in cart.values():
                if selected:
                    sku['selected'] = "True"
                else:
                    sku['selected'] = "False"

            return Response({"message": "OK"})