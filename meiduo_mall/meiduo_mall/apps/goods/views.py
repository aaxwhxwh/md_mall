from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from goods.models import GoodsCategory, SKU
from goods.serializers import ChannelSerializer, GoodsCategorySerializer, SKUSerializer


class CategoryView(GenericAPIView):
    """面包屑导航"""
    queryset = GoodsCategory.objects.all()

    def get(self, request, pk=None):
        ret = {
            "cat1": '',
            "cat2": '',
            "cat3": ''
        }

        # 自动从queryset中获取数据模型对象
        category = self.get_object()

        # 判断是否为第一级category
        if not category.parent:
            # 当前为第一级
            ret['cat1'] = ChannelSerializer(category.goodschannel_set.all()[0]).data
        # 三级分类判断
        elif category.goodscategory_set.count() == 0:
            # 当前类别为三级
            ret['cat3'] = GoodsCategorySerializer(category).data
            cat2 = category.parent
            ret['cat2'] = GoodsCategorySerializer(cat2).data
            ret['cat1'] = ChannelSerializer(cat2.parent.goodschannel_set.all()[0]).data
        else:
            # 当前类别为二级
            ret['cat2'] = GoodsCategorySerializer(category).data
            ret['cat1'] = ChannelSerializer(category.parent.goodschannel_set.all()[0]).data

        return Response(ret)


class SKUListView(ListAPIView):
    """商品分页查询"""
    serializer_class = SKUSerializer

    # 增加排序，drf框架提供对列表页排序的功能
    filter_backends = [OrderingFilter]
    orderring_fields = ['create_time', 'price', 'sales']

    # 重写queryset方法，自定义查找条件
    def get_queryset(self):
        # self.kwargs 为获取路有种正则匹配传递的参数,drf框架APIView中调用
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)

