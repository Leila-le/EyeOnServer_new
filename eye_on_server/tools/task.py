import logging

from celery import shared_task
from ..models import SeverInfo


@shared_task
def process_data_and_save(data):
    # 将数据存入数据库
    try:
        SeverInfo.objects.create(**data)
        print("success!")
    except Exception as e:
        print(e)
