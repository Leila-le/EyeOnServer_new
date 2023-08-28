from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from myadmin.models import User


# ==============后台管理员操作====================
def index(request):
    return render(request, "myadmin/user/index.html")


def login(request):
    '''加载登录页面'''
    return render(request, "myadmin/index/login.html")


def dologin(request):
    """执行登录"""
    try:
        # 根据登录账号获取用户信息
        user = User.objects.get(username=request.POST['username'])
        # 校验当前用户状态是否是管理员
        if user.status == 6:
            # 获取密码并md5
            import hashlib
            md5 = hashlib.md5()
            n = user.password_salt
            s = request.POST['pass'] + str(n)
            md5.update(s.encode('utf-8'))
            # 校验密码是否正确
            if user.password_hash == md5.hexdigest():
                # 将当前登录成功用户信息以adminuser这个key放入到session中
                request.session['adminuser'] = user.toDict()
                return redirect(reverse('myadmin_index'))
            else:
                context = {"info": "登录密码错误！"}
        else:
            context = {"info": "此用户非后台管理账号！"}
    except Exception as err:
        print(err)
        context = {"info": "登录账号不存在！"}
    return render(request, "myadmin/index/login.html", context)


def logout(request):
    '''执行退出'''
    del request.session['adminuser']
    return redirect(reverse('myadmin_login'))
