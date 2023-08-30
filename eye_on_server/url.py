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
from django.urls import path

# from eye_on_server.views.views import CustomLoginView
from eye_on_server.views import chart, data_process
from eye_on_server.views.views import search, systems, server, draw_lines, home

urlpatterns = [
    # 后台管理员路由
    path('data/', data_process.data_to_model, name='data'),
    path('base/', home, name='base'),
    path('basic_line_charts/', chart.Line, name='line'),

    # path('ServerChart/', views.draw_lines, name='ServerChart'),
    #
    # path('ServerList/', views.server, name='ServerList'),

    path('admin/ServerChart/', draw_lines, name='ServerChart'),

    path('admin/ServerList/', server, name='ServerList'),
    path('system/', systems, name='system'),

    path('admin/search/', search, name='search')
]
