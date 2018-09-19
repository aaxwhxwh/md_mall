from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from goods.models import SKU
from orders.serializers import OrderSettlementSerializer, SaveOrderSerializer


class OrderSettlementView(APIView):
    """订单提交视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取购物车中的商品信息"""
        user = request.user
        redis = get_redis_connection('cart')
        redis_cart = redis.hgetall('cart_%s' % user.id)
        cart_selected = redis.smembers('cart_selected_%s' % user.id)

        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]

        freight = Decimal('10.00')

        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})
        return Response(serializer.data)


class OrderView(CreateAPIView):
    """新建订单"""
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer


