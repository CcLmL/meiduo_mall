from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from areas.models import Area
from areas.serializer import AreaSerializer, SubAreaSerializer


# Create your views here.


# GET /areas/
# class AreasView(GenericAPIView):
class AreasView(ListAPIView):
    serializer_class = AreaSerializer
    queryset = Area.objects.filter(parent=None)

    # def get(self, request):
    #     """
    #     获取所有省级地区的信息
    #     1. 查询所有省级地区
    #     2. 将省级地区的信息序列化返回
    #     """
    #     # 1. 查询所有省级地区
    #     areas = self.get_queryset()
    #
    #     # 2. 将省级地区的信息序列化返回
    #     serializer = self.get_serializer(areas, many=True)
    #
    #     return Response(serializer.data)


# GET /areas/(?p<pk>\d+)/
# class SubAreasView(GenericAPIView):
class SubAreasView(RetrieveAPIView):
    serializer_class = SubAreaSerializer
    queryset = Area.objects.all()

    # def get(self, request, pk):
    #     """
    #     获取指定地区的信息
    #     1. 根据pk获取的指定的地区信息
    #     2. 将地区序列化并返回(注:将地址关联的下级地区进行嵌套序列化)
    #     """
    #     # 1. 根据pk获取的指定的地区信息
    #     # area = Area.objects.get(pk=pk)
    #     area = self.get_object()  # 这个方法默认就是通过主键查出对象
    #
    #     # 2. 将地区序列化并返回(注:将地址关联的下级地区进行嵌套序列化)
    #     serializer = self.get_serializer(area)
    #
    #     return Response(serializer.data)