# 封装任务函数
from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun.sms import CCP
# celery_tasks是独立与项目的功能,所以其中的依赖项也可以单独拿来使用

# 发送短信模板ID
SMS_CODE_TEMP_ID = 1

# 获取日志器
import logging
logger = logging.getLogger('django')  # 因为在打印日志使用了django中的日志器,所以要为celery使用django配置文件进行设置


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code, expires):
    # 任务函数代码
    try:
        res = CCP().send_template_sms(mobile, [sms_code, expires], SMS_CODE_TEMP_ID)
    except Exception as e:
        logger.error('发送短信异常:[mobile: %s]-[sms_code: %s]' % (mobile, sms_code))
        # return Response({'message': '发送短信异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)  因为服务器此时的作用就是发送一个任务,然后就继续自己的执行,这个函数的执行是通过worker完成的,所以此时就不需要返回响应给服务器了
    else:
        if res != 0:
            logger.error('发送短信失败:[mobile: %s]-[sms_code: %s]' % (mobile, sms_code))
        else:
            logger.error('发送短信成功:[mobile: %s]-[sms_code: %s]' % (mobile, sms_code))