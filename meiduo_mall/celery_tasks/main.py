from celery import Celery

# 设置Django运行所依赖的环境变量
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 创建Celery类的对象,celery_tasks目录与项目是无关的
celery_app = Celery('celery_tasks')  # 名字就是一个字符串,随便取

# 加载配置
celery_app.config_from_object('celery_tasks.config')

# 启动worker时自动发现任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_email'])  # 自动发现任务会自动在路径下找tasks文件(所以tasks的名字是固定的)

