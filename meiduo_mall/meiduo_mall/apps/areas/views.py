from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from areas.models import Area
from areas.serializer import AreaSerializer

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