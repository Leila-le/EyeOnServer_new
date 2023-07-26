from django.contrib import admin
# 向应用中加入监测器内容
from .models import SeverInfo
# Register your models here.
admin.site.register(SeverInfo)