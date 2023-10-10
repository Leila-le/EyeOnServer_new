from celery import shared_task
from ..models import SeverInfo


@shared_task
def process_data_and_save(data):
    # 处理数据
    # 将数据存入数据库
    SeverInfo.objects.create(**data)
