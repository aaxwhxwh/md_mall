#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:will
@file: serializers.py
@time: 2018/09/13
"""
import random
import time
from decimal import Decimal

from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers
from django.db import transaction

from goods.models import SKU
from meiduo_mall.utils.exceptons import logger
from orders.models import OrderInfo, OrderGoods


class CartSKUSerializer(serializers.ModelSerializer):
    """商品购物车序列化器"""
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price')


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class SaveOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderInfo
        fields = ['order_id', 'address', 'pay_method']

        read_only_fields = ['order_id']

        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True,
            }
        }

    def create(self, validated_data):
        """保存创建订单"""
        user = self.context["request"].user
        # 自定义订单ID

        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ("%09d" % user.id) + str(random.randint(0, 10000))

        # 获取当前用户
        address = validated_data['address']
        pay_method = validated_data['pay_method']

        with transaction.atomic():
            save_id = transaction.savepoint()

            try:
                # 保存订单信息
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0),
                    freight=Decimal(10),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )

                # 从redis获取购物商品详情
                redis = get_redis_connection('cart')
                redis_cart = redis.hgetall('cart_%s' % user.id)
                cart_selected = redis.smembers('cart_selected_%s' % user.id)

                cart = {}
                for sku_id in cart_selected:
                    cart[int(sku_id)] = int(redis_cart[sku_id])

                # 遍历结算商品
                for sku_id in cart:
                    while True:
                        # 判断库存量，确定是否创建订单
                        sku = SKU.objects.get(pk=sku_id)
                        sku_count = cart[sku_id]

                        # 判断库存
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        if sku_count > origin_stock:
                            transaction.savepoint_rollback(save_id)
                            raise serializers.ValidationError("商品库存不足")

                        time.sleep(5)

                        # sku.stock = origin_stock - sku_count
                        new_stock = origin_stock - sku_count
                        # sku.sales = origin_sales + sku_count
                        new_sales = origin_sales + sku_count
                        # sku.save()
                        # 乐观锁解决库存变化
                        ret = SKU.objects.filter(id=sku.id, stock=origin_stock).update(stock=new_stock, sales=new_sales)

                        if ret == 0:
                            continue

                        sku.goods.sales += sku_count
                        sku.goods.save()

                        # 商品金额
                        order.total_count += sku_count
                        order.total_amount += (sku.price * sku_count)

                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )

                        break

                order.total_amount += order.freight
                order.save()

            except serializers.ValidationError:
                raise
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                raise

            transaction.savepoint_commit(save_id)
            # 删除已结算的redis商品信息
            pl = redis.pipeline()
            pl.hdel('cart_%s' % user.id, *cart_selected)
            pl.srem('cart_selected_%s' % user.id, *cart_selected)
            pl.execute()

            return order
