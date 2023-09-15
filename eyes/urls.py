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

    path('web/', views.draw_lines, name='ServerChart'),  # 用于展示cpu\内存使用折线图以及磁盘当前使用率
    path('web/base/', views.home, name='base'),  # 基本页面
    path('web/data/', views.data_to_model, name='data'),  # 将数据存入数据库中以及发送钉钉预警信息

    path('table_data', views.data_to_json, name='table_data'),  # 用于实现ServerList中的数据转为json便于展示
    path('web/ServerList/', views.sever_list, name='ServerList'),  # 各系统当前最新资源使用数据
    path('web/system/', views.systems, name='system'),  # 系统详细信息展示
    path('web/search/', views.search, name='search'), # 搜索

    # 员工账号信息管理
    path('get_data', views.get_data, name="get_data"),  # 用户信息
    # path('user/search', user.search_user, name='user_search'),  # 搜索用户
    path('user', views.index, name="myadmin_user_index"),  # 浏览信息
    path('user/add', views.add, name="myadmin_user_add"),  # 加载添加表单
    path('user/check_username', views.check_username, name="myadmin_user_check_username"),  # 加载添加表单
    # path('user/add', user.insert, name="myadmin_user_add"),  # 加载添加用户
    path('user/insert', views.insert, name="myadmin_user_insert"),  # 执行信息添加
    path('user/del', views.delete, name="myadmin_user_del"),  # 删除信息
    path('user/edit', views.edit, name="myadmin_user_edit"),  # 准备信息编辑
    path('user/update/', views.update, name="myadmin_user_update"),  # 执行信息编辑
    # 重置员工密码
    path('user/resetpass', views.reset_pass, name="myadmin_user_resetpass"),
    path('user/resetpassword', views.reset_password, name="myadmin_user_reset_password"),

    # 后台管理员路由
    path('login', views.login_, name="myadmin_login"),
    path('dologin', views.do_login, name="myadmin_dologin"),
    path('logout', views.logout, name="myadmin_logout"),
]
