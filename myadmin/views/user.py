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
import json
from django.shortcuts import render

# 用于将数据表中的数据转为json格式,传至对应的html页面中的table中


def userdata_to_json(request, count):
    data = []
    users = User.objects.all()
    for user in users:
        overview_data = {}
        if user.status == 1:
            status = '正常'
        elif user.status == 2:
            status = '禁停'
        elif user.status == 6:
            status = '管理员'
        elif user.status == 9:
            status = '已删除'
        else:
            status = '未知状态'

        update_at = user.update_at
        update_at_str = update_at.isoformat()

        create_at = user.create_at
        create_at_str = create_at.isoformat()

        overview_data.update(id=user.id,
                             username=user.username,
                             nickname=user.nickname,
                             status=status,
                             create_at=create_at_str,
                             update_at=update_at_str)
        data.append(overview_data)
    merged_data = {'code': 0, 'count': count, 'data': data}
    file_path = './static/merger_users.json'
    try:
        with open(file_path, 'w') as f:
            json.dump(merged_data, f)
    except Exception as e:
        print('json文件生成失败', e)
    # return render(request, "myadmin/user/index.html")
    return HttpResponse('OK')


def index(request):
    """浏览信息"""
    # 获取、判断并封装状态status搜索条件
    umod = User.objects
    mywhere = []
    list_ = umod.filter(status__lt=9)
    max_pages = len(list_)  # 总条数
    if userdata_to_json(request, max_pages):
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
        # 获取页码总条数

        max_pages = len(list_)  # 最大页数
        print("max_pages", max_pages)
        # 封装信息加载模板输出
        context = {'maxpages': max_pages}
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
            return JsonResponse({'success': False, 'message': str(err)})  # 添加错误消息到消息队列
        # return render(request, "myadmin/info.html", context)
    return JsonResponse({'success': True, 'message': '添加成功！'})


def delete(request):
    """删除信息"""
    if request.method == 'GET':
        uid = request.GET.get('id')
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
    """加载编辑信息页面"""
    if request.method == 'GET':
        uid = request.GET.get('id')
        try:
            ob = User.objects.get(id=uid)
            context = {"user": ob}
            return render(request, "myadmin/user/edit.html", context)
        except Exception as err:
            context = {"info": "没有找到要修改的信息！"}
            return render(request, "myadmin/info.html", context)


def update(request):
    """执行编辑信息"""
    if request.method == 'GET':
        uid = request.GET.get('id')
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
