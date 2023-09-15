from django.contrib import admin
from .models import SeverInfo, User


# Register your models here.
admin.site.register(User)
admin.site.register(SeverInfo)
