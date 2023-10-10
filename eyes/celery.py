import os
import django
from celery import Celery
from django.conf import settings

# 设置系统环境变量，安装django，必须设置，否则在启动celery时会报错
# celery_study 是当前项目名
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eyes.settings')
django.setup()
app = Celery('eyes')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
broker_connection_retry_on_startup = True
