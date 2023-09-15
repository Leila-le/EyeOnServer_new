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
from django.urls import path

from eye_on_server import views

urlpatterns = [
    path('myadmin/', admin.site.urls),
    path('', views.draw_lines, name='ServerChart'),  # 用于展示cpu\内存使用折线图以及磁盘当前使用率
    path('base/', views.home, name='base'),  # 基本页面
    path('data/', views.data_to_model, name='data'),  # 将数据存入数据库中以及发送钉钉预警信息

    path('table_data', views.data_to_json, name='table_data'),  # 用于实现ServerList中的数据转为json便于展示
    path('ServerList/', views.sever_list, name='ServerList'),  # 各系统当前最新资源使用数据
    path('system/', views.systems, name='system'),  # 系统详细信息展示
    path('search/', views.search, name='search')  # 搜索
]
