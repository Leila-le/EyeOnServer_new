from django.db import models

from datetime import datetime


# 员工账号信息模型
# class User(models.Model):
#     username = models.CharField(max_length=50)  # 员工账号
#     nickname = models.CharField(max_length=50)  # 昵称
#     password_hash = models.CharField(max_length=100)  # 密码
#     password_salt = models.CharField(max_length=50)  # 密码干扰值
#     status = models.IntegerField(default=1)  # 状态:1正常/2禁用/9删除
#     create_at = models.DateTimeField(default=datetime.now)  # 创建时间
#     update_at = models.DateTimeField(default=datetime.now)  # 修改时间
#
#     def toDict(self):
#         return {'id': self.id, 'username': self.username, 'nickname': self.nickname,
#                 'password_hash': self.password_hash, 'password_salt': self.password_salt, 'status': self.status,
#                 'create_at': self.create_at.strftime('%Y-%m-%d %H:%M:%S'),
#                 'update_at': self.update_at.strftime('%Y-%m-%d %H:%M:%S')}
#
#     class Meta:
#         db_table = "user"  # 更改表名


# Create your models here.
class SeverInfo(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)
    license_name = models.CharField(max_length=30, blank=True, null=True)
    time = models.CharField(max_length=30, blank=True, null=True)
    # 获取CPU使用情况
    cpu_guest = models.CharField(max_length=30, blank=True, null=True)
    cpu_guest_nice = models.CharField(max_length=30, blank=True, null=True)
    cpu_idle = models.CharField(max_length=30, blank=True, null=True)
    cpu_iowait = models.CharField(max_length=30, blank=True, null=True)
    cpu_irq = models.CharField(max_length=30, blank=True, null=True)
    cpu_nice = models.CharField(max_length=30, blank=True, null=True)
    cpu_percent = models.CharField(max_length=30, blank=True, null=True)
    cpu_softirq = models.CharField(max_length=30, blank=True, null=True)
    cpu_steal = models.CharField(max_length=30, blank=True, null=True)
    cpu_system = models.CharField(max_length=30, blank=True, null=True)
    cpu_total_active = models.CharField(max_length=30, blank=True, null=True)
    cpu_total_idle = models.CharField(max_length=30, blank=True, null=True)
    cpu_user = models.CharField(max_length=30, blank=True, null=True)
    cpu_count = models.CharField(max_length=5, blank=True, null=True)

    # 获取内存使用情况
    memory_free_physics = models.CharField(max_length=30, blank=True, null=True)
    memory_free_swap = models.CharField(max_length=30, blank=True, null=True)
    memory_processes = models.CharField(max_length=30, blank=True, null=True)
    memory_total_physics = models.CharField(max_length=30, blank=True, null=True)
    memory_total_swap = models.CharField(max_length=30, blank=True, null=True)
    memory_uptime = models.CharField(max_length=30, blank=True, null=True)
    memory_used_physics = models.CharField(max_length=30, blank=True, null=True)
    memory_used_swap = models.CharField(max_length=30, blank=True, null=True)
    memory_ava = models.CharField(max_length=30, blank=True, null=True)
    memory_percent = models.CharField(max_length=30, blank=True, null=True)
    memory_swap_percent = models.CharField(max_length=30, blank=True, null=True)
    # 获取磁盘使用情况
    disk_free = models.CharField(max_length=30, blank=True, null=True)
    disk_mount_point = models.CharField(max_length=30, blank=True, null=True)
    disk_total = models.CharField(max_length=30, blank=True, null=True)
    disk_used = models.CharField(max_length=30, blank=True, null=True)
    disk_percent = models.CharField(max_length=30, blank=True, null=True)
    # # 获取网络使用情况
    # net_sent = models.CharField(max_length=30, blank=True, null=True)
    # net_rec = models.CharField(max_length=30, blank=True, null=True)
    # 客户端状态
    # status = models.CharField(max_length=10, blank=True, null=True)
