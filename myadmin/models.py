from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

    def authenticate(self, username, password):
        user = self.model.objects.get(username=username)
        if user.check_password(password):
            return user
        return None


class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    nickname = models.CharField(max_length=50, null=True)
    status = models.IntegerField(default=1)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'status': self.status,
            'create_at': self.create_at.strftime('%Y-%m-%d %H:%M:%S'),
            'update_at': self.update_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def has_perm(self, perm, obj=None):
        # 实现判断用户是否具有特定权限的方法
        return self.is_superuser

    def has_module_perms(self, app_label):
        # 实现判断用户是否具有特定应用权限的方法
        return self.is_superuser

    class Meta:
        db_table = "user"
