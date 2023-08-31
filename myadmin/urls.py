from django.urls import path

from myadmin.views import index
from myadmin.views import user

urlpatterns = [
    # 后台首页
    path('', index.index, name="myadmin_index"),
    path('database/', user.database_show, name='database_show'),
    # 员工账号信息管理
    path('get_data', user.get_data, name="get_data"),  # 用户信息
    path('user', user.index, name="myadmin_user_index"),  # 浏览信息
    path('user/add', user.add, name="myadmin_user_add"),  # 加载添加表单
    path('user/insert', user.insert, name="myadmin_user_insert"),  # 执行信息添加
    path('user/del', user.delete, name="myadmin_user_del"),  # 删除信息
    path('user/edit', user.edit, name="myadmin_user_edit"),  # 准备信息编辑
    path('user/update', user.update, name="myadmin_user_update"),  # 执行信息编辑
    # 重置员工密码
    # path('user/resetpass/<int:uid>', user.resetpass, name="myadmin_user_resetpass"),
    # path('user/doresetpass/<int:uid>', user.doresetpass, name="myadmin_user_doresetpass"),

    # 后台管理员路由
    path('login', index.login, name="myadmin_login"),
    path('dologin', index.dologin, name="myadmin_dologin"),
    path('logout', index.logout, name="myadmin_logout"),
    # path('verify', index.verify, name="myadmin_verify"), #验证码
]
