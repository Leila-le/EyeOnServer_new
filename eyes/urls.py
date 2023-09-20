"""
URL configuration for eyes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import PasswordChangeView
from django.urls import path
from eye_on_server import views
from eye_on_server.views import MyLoginView

urlpatterns = [
    path('myadmin/', admin.site.urls),
    path('data/', views.data_to_model, name='data'),  # 将数据存入数据库中,并将超过阈值的内容传至钉钉

    path('web/', views.draw_lines, name='ServerChart'),  # 用于展示cpu\内存使用折线图以及磁盘当前使用率
    path('table_data', views.data_to_json, name='table_data'),  # 用于实现ServerList中的数据转为json便于展示
    path('web/ServerList/', views.sever_list, name='ServerList'),  # 各系统当前最新资源使用数据
    path('web/system/', views.systems, name='system'),  # 系统详细信息展示
    path('web/search/', views.search, name='search'),  # 搜索

    path('change-password/', PasswordChangeView.as_view(), name='password_change'),
    path('accounts/login/', MyLoginView.as_view(), name='login'),
    path('logout', views.logout_view, name="logout"),
]
