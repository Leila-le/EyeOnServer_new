import logging

from celery import shared_task
from django.core.cache import cache

from ..models import SeverInfo


@shared_task
def process_data_and_save(data):
    # 将数据存入数据库
    try:
        SeverInfo.objects.create(**data)


    except Exception as e:
        logging.error(e)
