import random

from django.conf.locale import pl
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall.libs.yuntongxun.sms import CCP
from verifications import constants

# Create your views here.

# 获取日志器
import logging
logger = logging.getLogger('django')


# GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(APIView):
    def get(self, request, mobile):
        """
        获取短信验证码:
        1.给mobile手机号发送短信验证码(因为不正确格式的手机号不能指定到这个url)
            1.1 随机生成一个6位数字
            1.2 在redis中保存短信验证码内容,以'mobile'为key,以短信验证码内容为value
            1.3 使用云通讯发送短信
        2.返回应答,发送成功
        """

        # 1.1 随机生成一个6位数字
        sms_code = '06%s' % random.randint(0, 999999)
        logger.info('短信验证码为: %s' % sms_code)

        # 1.2 在redis中保存短信验证码内容, 以'mobile'为key, 以短信验证码内容为value
        redis_conn = get_redis_connection('verify_codes')
        # 判断60s之内是否给mobile手机发送过短信
        send_flag = redis_conn.get('send_flag_' % mobile)  # 超过时间自动删除返回none

        if send_flag:
            return Response({'message': '发送信息过于频繁'}, status=status.HTTP_400_BAD_REQUEST)

        # redis_conn.set('<key>', '<value>', '<expires>')
        # redis_conn.setex('<key>', '<expires>', '<value>')  两者没有区别,就是参数的顺序不同

        # 因为这里运行了两次setex,即访问了两次redis,造成了性能浪费,所以我们可以使用管道
        pl = redis_conn.pipeline()

        # 向redis管道中添加命令
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRE, sms_code)

        # 设置给'mobile'发送短信息验证码标记
        pl.setex('send_flag_' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 一次性执行管道中所有命令
        pl.exectue()

        # 1.3 使用云通讯发送短信
        expires = constants.SMS_CODE_REDIS_EXPIRE // 60 # 获取过期时间(分钟)

        # try:
        #     res = CCP().send_template_sms(mobile, [sms_code, expires], constants.SMS_CODE_TEMP_ID)
        # except Exception as e:
        #     logger.error(e)
        #     return Response({'message': '发送短信异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # if res != 0:
        #     return Response({'message': '发送短信失败'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # 因为云通讯如果要发送验证码需要指定特定的手机号码

        # 2.返回应答,发送成功
        return Response({'message': 'ok'})
