from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import SeverInfo, User


class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['password'].widget.attrs['readonly'] = True


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm


# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(SeverInfo)
