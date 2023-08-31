from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
import hashlib
from myadmin.models import User


# ==============后台管理员操作====================
def index(request):
    return render(request, "myadmin/user/index.html")


def encrypt_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    encrypted_password = md5.hexdigest()
    return encrypted_password


# def dologin(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         # 在这里可以进行表单验证、用户认证等相关逻辑处理
#         encrypted_password = encrypt_password(password)
#
#         # 验证用户名和加密后的密码
#         user = authenticate(request, username=username, password=encrypted_password)
#         if user is not None:
#             login(request, user)
#             return redirect('myadmin_index')  # 重定向到后台管理首页
#         else:
#             context = {'info': '登录失败，请检查用户名和密码'}
#             return render(request, 'myadmin/index/login.html', context)
#
#     return render(request, 'myadmin/index/login.html')

def login(request):
    """加载登录页面"""
    return render(request, "myadmin/index/login.html")


def dologin(request):
    """执行登录"""
    print(1)
    if request.method == 'POST':
        print(2)
        try:
            # 根据登录账号获取用户信息
            user = User.objects.get(username=request.POST['username'])
            # 校验当前用户状态是否是管理员
            if user.status == 6:
                print(3)
                # 获取密码并md5
                md5 = hashlib.md5()
                n = user.password_salt
                s = request.POST['password'] + str(n)
                md5.update(s.encode('utf-8'))
                # 校验密码是否正确
                if user.password_hash == md5.hexdigest():
                    # 将当前登录成功用户信息以adminuser这个key放入到session中
                    request.session['adminuser'] = user.toDict()
                    print(4)
                    return redirect(reverse('myadmin_index'))
                else:

                    context = {"info": "登录密码错误！"}
            else:
                context = {"info": "此用户非后台管理账号！"}
        except Exception as err:
            print(5555)
            print(err)
            context = {"info": err}
        return render(request, "myadmin/index/login.html", context)
    else:
        return HttpResponse("Invalid request")  # 返回一个适当的响应


def logout(request):
    """执行退出"""
    del request.session['adminuser']
    return redirect(reverse('myadmin_login'))
