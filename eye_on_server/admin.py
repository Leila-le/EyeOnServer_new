from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from management.commands.print_urls import Command as PrintUrlsCommand
# 向应用中加入监测器内容
from .models import SeverInfo
# Register your models here.
admin.site.register(SeverInfo)
