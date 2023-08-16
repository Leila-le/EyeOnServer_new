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
from eye_on_server.views import views
from eye_on_server.views import chart
from eye_on_server.views import data_process

urlpatterns = [
    # path('', include(eye_on_server.urls)),
    path('center', admin.site.urls),
    path('data/', data_process.data_to_model, name='data'),
    path('base/', views.home, name='base'),
    path('basic_line_charts/', chart.Line, name='line'),
    path('ServerList/', views.server, name='ServerList'),
    path('ServerChart/', views.draw_lines, name='ServerChart'),
    path('chart/', views.draw_line, name='chart'),
    path('system/', views.systems, name='system'),

]
