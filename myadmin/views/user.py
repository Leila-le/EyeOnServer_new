from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime
import random

from myadmin.models import User

from eye_on_server.views.tableShow import data_to_json


def index(request, pIndex=1):
    """浏览信息"""
    umod = User.objects
    mywhere = []
    list_ = umod.filter(status__lt=9)

    # 获取、判断并封装关keyword键搜索
    kw = request.GET.get("keyword", None)
    if kw:
        # 查询员工账号或昵称中只要含有关键字的都可以
        list_ = list_.filter(Q(username__contains=kw) | Q(nickname__contains=kw))
        mywhere.append("keyword=" + kw)

    # 获取、判断并封装状态status搜索条件
    status = request.GET.get('status', '')
    if status != '':
        list_ = list_.filter(status=status)
        mywhere.append("status=" + status)

    # 执行分页处理
    pIndex = int(pIndex)
    page = Paginator(list_, 5)  # 以5条每页创建分页对象
    maxpages = page.num_pages  # 最大页数
    # 判断页数是否越界
    if pIndex > maxpages:
        pIndex = maxpages
    if pIndex < 1:
        pIndex = 1
    list2 = page.page(pIndex)  # 当前页数据
    plist = page.page_range  # 页码数列表

    # list2 = User.objects.all() #获取所有信息
    # 封装信息加载模板输出
    context = {"userlist": list2, 'plist': plist, 'pIndex': pIndex, 'maxpages': maxpages, 'mywhere': mywhere}
    return render(request, "myadmin/user/index.html", context)


def database_show(request):
    file_path = './static/merger.json'
    url = 'myadmin/database/databaseshow.html'
    return data_to_json(request, url, file_path)


def add(request):
    """加载添加页面"""
    return render(request, "myadmin/user/add.html")


def insert(request):
    """执行添加"""
    if request.method == 'POST':
        try:
            ob = User()
            username = request.POST['username']
            if User.objects.filter(username=username).exists():
                raise ValidationError('该账号已被注册')

            ob.username = username
            ob.nickname = request.POST['nickname']
            # 获取密码并md5
            import hashlib
            md5 = hashlib.md5()
            n = random.randint(100000, 999999)
            s = request.POST['password'] + str(n)
            md5.update(s.encode('utf-8'))
            ob.password_hash = md5.hexdigest()
            ob.password_salt = n
            ob.status = 1
            ob.create_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ob.update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ob.save()
            # context = {"info": "添加成功！"}
        except ValidationError as err:
            return JsonResponse({'success': False, 'message': str(err)})# 添加错误消息到消息队列
        # return render(request, "myadmin/info.html", context)
    return JsonResponse({'success': True, 'message': '添加成功！'})


def delete(request, uid):
    """删除信息"""
    try:
        ob = User.objects.get(id=uid)
        ob.status = 9
        ob.update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ob.save()
        context = {"info": "删除成功！"}
    except Exception as err:
        print(err)
        context = {"info": "删除失败"}

    # return JsonResponse(context)
    return render(request, "myadmin/info.html", context)


def edit(request, uid):
    '''加载编辑信息页面'''
    try:
        ob = User.objects.get(id=uid)
        context = {"user": ob}
        return render(request, "myadmin/user/edit.html", context)
    except Exception as err:
        context = {"info": "没有找到要修改的信息！"}
        return render(request, "myadmin/info.html", context)


def update(request, uid):
    '''执行编辑信息'''
    try:
        ob = User.objects.get(id=uid)
        ob.nickname = request.POST['nickname']
        ob.status = request.POST['status']
        ob.update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ob.save()
        context = {"info": "修改成功！"}
    except Exception as err:
        print(err)
        context = {"info": "修改失败"}
    return render(request, "myadmin/info.html", context)


"""
def resetpass(request,uid):
    '''加载重置会员密码信息页面'''
    try:
        ob = User.objects.get(id=uid)
        context={"user":ob}
        return render(request,"myadmin/user/resetpass.html",context)
    except Exception as err:
        context={"info":"没有找到要修改的信息！"}
        return render(request,"myadmin/info.html",context)

def doresetpass(request,uid):
    '''执行编辑信息'''
    try:
        ob = User.objects.get(id=uid)
        #获取密码并md5
        import hashlib
        md5 = hashlib.md5()
        n = random.randint(100000, 999999)
        s = request.POST['password']+str(n) 
        md5.update(s.encode('utf-8'))
        ob.password_hash = md5.hexdigest()
        ob.password_salt = n
        ob.save()
        context={"info":"密码重置成功！"}
    except Exception as err:
        print(err)
        context={"info":"密码重置失败"}
    return render(request,"myadmin/info.html",context)
"""
