from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, Permission, PermissionsMixin
from django.db import models
from django.utils import timezone


# Create your models here.
class SeverInfo(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)
    license_name = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    # time = models.DateTimeField(auto_now_add=True)
    time = models.DateTimeField()
    # 获取CPU使用情况
    guest = models.CharField(max_length=30, blank=True, null=True)
    guest_nice = models.CharField(max_length=30, blank=True, null=True)
    idle = models.CharField(max_length=30, blank=True, null=True)
    iowait = models.CharField(max_length=30, blank=True, null=True)
    irq = models.CharField(max_length=30, blank=True, null=True)
    nice = models.CharField(max_length=30, blank=True, null=True)
    percent = models.CharField(max_length=30, blank=True, null=True)
    softirq = models.CharField(max_length=30, blank=True, null=True)
    steal = models.CharField(max_length=30, blank=True, null=True)
    system = models.CharField(max_length=30, blank=True, null=True)
    total_active = models.CharField(max_length=30, blank=True, null=True)
    total_idle = models.CharField(max_length=30, blank=True, null=True)
    user = models.CharField(max_length=30, blank=True, null=True)
    count = models.CharField(max_length=5, blank=True, null=True)
    # 获取内存使用情况
    free_physics = models.CharField(max_length=30, blank=True, null=True)
    free_swap = models.CharField(max_length=30, blank=True, null=True)
    processes = models.CharField(max_length=30, blank=True, null=True)
    total_physics = models.CharField(max_length=30, blank=True, null=True)
    total_swap = models.CharField(max_length=30, blank=True, null=True)
    uptime = models.CharField(max_length=30, blank=True, null=True)
    used_physics = models.CharField(max_length=30, blank=True, null=True)
    used_swap = models.CharField(max_length=30, blank=True, null=True)
    ava = models.CharField(max_length=30, blank=True, null=True)
    memory_percent = models.CharField(max_length=30, blank=True, null=True)
    swap_percent = models.CharField(max_length=30, blank=True, null=True)
    # 获取磁盘使用情况
    free = models.CharField(max_length=30, blank=True, null=True)
    mount_point = models.CharField(max_length=30, blank=True, null=True)
    total = models.CharField(max_length=30, blank=True, null=True)
    used = models.CharField(max_length=30, blank=True, null=True)
    disk_percent = models.CharField(max_length=30, blank=True, null=True)

    # @property
    # def localized_time(self):
    #     return self.time.astimezone(timezone.get_current_timezone())


class User(AbstractUser):
    nickname = models.CharField(max_length=50, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    @property
    def localized_time(self):
        return self.create_at.astimezone(timezone.get_current_timezone()), \
            self.update_at.astimezone(timezone.get_current_timezone())
