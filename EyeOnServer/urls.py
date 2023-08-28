"""
URL configuration for EyeOnServer project.

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
from django.urls import path, include
# from eye_on_server.views import views, chart, data_process
from eye_on_server.views.views import CustomLoginView

urlpatterns = [
    # 后台管理员路由
    # path('login', views.login, name="myadmin_login"),
    # path('dologin', views.dologin, name="myadmin_dologin"),
    # path('logout', views.logout, name="myadmin_logout"),
    # path('verify', views.verify, name="myadmin_verify"), #验证码
    # path('admin/login/', CustomLoginView.as_view(), name='admin_login'),
    # path('admin/', admin.site.urls),

    # path('data/', data_process.data_to_model, name='data'),
    # path('base/', views.home, name='base'),
    # path('basic_line_charts/', chart.Line, name='line'),

    # path('ServerChart/', views.draw_lines, name='ServerChart'),
    #
    # path('ServerList/', views.server, name='ServerList'),

    # path('admin/ServerChart/', views.draw_lines, name='ServerChart'),
    #
    # path('admin/ServerList/', views.server, name='ServerList'),
    # path('system/', views.systems, name='system'),
    #
    # path('admin/search/', views.search, name='search')

    path('', include('eye_on_server.url')),
    path('myadmin/', include("myadmin.urls")),
]
