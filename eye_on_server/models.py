from django.db import models


# Create your models here.
class SeverInfo(models.Model):
    ip = models.CharField(max_length=30, blank=True, null=True)
    time = models.DateTimeField()
    # 获取CPU个数和使用率
    cpu_count = models.CharField(max_length=5, blank=True, null=True)
    cpu_percent = models.CharField(max_length=30, blank=True, null=True)
    # 获取内存使用情况
    memory_total = models.CharField(max_length=30, blank=True, null=True)
    memory_ava = models.CharField(max_length=30, blank=True, null=True)
    mem_used = models.CharField(max_length=30, blank=True, null=True)
    memory_per = models.CharField(max_length=30, blank=True, null=True)
    # 获取磁盘使用情况
    disk_total = models.CharField(max_length=30, blank=True, null=True)
    disk_used = models.CharField(max_length=30, blank=True, null=True)
    disk_percent = models.CharField(max_length=30, blank=True, null=True)
    # 获取网络使用情况
    net_sent = models.CharField(max_length=30, blank=True, null=True)
    net_rec = models.CharField(max_length=30, blank=True, null=True)
    # 客户端状态
    status = models.CharField(max_length=10, blank=True, null=True)
