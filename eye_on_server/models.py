from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, Permission, PermissionsMixin
from django.db import models


# Create your models here.
class SeverInfo(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)
    license_name = models.CharField(max_length=30, blank=True, null=True)
    time = models.CharField(max_length=30, blank=True, null=True)
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


# class UserManager(BaseUserManager):
#
#     def create_user(self, username, password=None, **extra_fields):
#         user = self.model(username=username, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, username, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#
#         return self.create_user(username, password, **extra_fields)
#
#
# class User(AbstractBaseUser):
#     username = models.CharField(max_length=50, unique=True)
#     nickname = models.CharField(max_length=50, null=True)
#
#     create_at = models.DateTimeField(auto_now_add=True)
#     update_at = models.DateTimeField(auto_now=True)
#
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#
#     objects = UserManager()
#
#     USERNAME_FIELD = 'username'
#
#     def toDict(self):
#         return {
#             'id': self.id,
#             'username': self.username,
#             'nickname': self.nickname,
#             'create_at': self.create_at.strftime('%Y-%m-%d %H:%M:%S'),
#             'update_at': self.update_at.strftime('%Y-%m-%d %H:%M:%S')
#         }
#
#     def has_perm(self, perm, obj=None):
#         # 实现判断用户是否具有特定权限的方法
#         return self.is_superuser
#
#     def has_module_perms(self, app_label):
#         # 实现判断用户是否具有特定应用权限的方法
#         return self.is_superuser
#
#     class Meta:
#         db_table = "user"

class User(AbstractUser):
    nickname = models.CharField(max_length=50, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

