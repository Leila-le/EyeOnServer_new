from django.db import models


# Create your models here.
class SeverInfo(models.Model):
    ip = models.CharField(max_length=30)
    time = models.DateTimeField()
    # 获取CPU个数和使用率
    cpu_count = models.CharField(max_length=5)
    cpu_percent = models.CharField(max_length=30)
    # 获取内存使用情况
    memory_total = models.CharField(max_length=30)
    mem_used = models.CharField(max_length=30)
    memory_per = models.CharField(max_length=30)
    # 获取磁盘使用情况
    disk_total = models.CharField(max_length=30)
    disk_used = models.CharField(max_length=30)
    disk_percent = models.CharField(max_length=30)
    # 获取网络使用情况
    net_sent = models.CharField(max_length=30)
    net_rec = models.CharField(max_length=30)
