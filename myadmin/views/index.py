from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
import hashlib
from myadmin.models import User


# ==============后台管理员操作====================
def index(request):
    return render(request, "myadmin/user/index.html")

def login_(request):
    """加载登录页面"""
    return render(request, "myadmin/index/login.html")


def dologin(request):
    """执行登录"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        user = User.objects.get(username=username)
        status = user.status
        if user is not None and status != 9:
            login(request, user)
            # 登录成功地处理逻辑
            if status == 6:
                return render(request, 'myadmin/base.html', {'adminuser': user.nickname})
            else:
                return redirect('ServerChart')
        else:
            # 登录失败的处理逻辑
            error_message = 'Invalid username or password'
            return render(request, 'myadmin/index/login.html', {'error_message': error_message})
    return render(request, 'myadmin/index/login.html')


def logout(request):
    """执行退出"""
    del request.session['adminuser']
    return redirect(reverse('myadmin_login'))
