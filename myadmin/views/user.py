from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt

from myadmin.models import User

from eye_on_server.views.tableShow import data_to_json
from django.shortcuts import render


# 用于将数据表中的数据转为json格式,传至对应的html页面中的table中
def get_data(request):  # 表格展示内容
    queryset = User.objects.filter(status__lt=9)
    status_mapping = {
        1: '正常',
        2: '禁停',
        6: '管理员',
        9: '已删除',
    }
    # 获取请求中的页码和每页数量参数
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)

    paginator = Paginator(queryset, limit)

    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)

    data = [{
        'id': item.id,
        'username': item.username,
        'nickname': item.nickname,
        'status': status_mapping.get(item.status, '未知状态'),
        'create_at': datetime.strftime(item.create_at, "%Y-%m-%d %H:%M:%S"),
        'update_at': datetime.strftime(item.update_at, "%Y-%m-%d %H:%M:%S"),

    } for item in page_data]

    return JsonResponse({
        'code': 0,
        'msg': '',
        'count': paginator.count,
        'data': data
    })


def index(request):
    """浏览信息"""
    return render(request, "myadmin/user/index.html")


def database_show(request):
    file_path = './static/merger.json'
    url = 'myadmin/database/databaseshow.html'
    return data_to_json(request, url, file_path)


def add(request):
    """加载添加页面"""
    return render(request, "myadmin/user/add.html")


def check_username(request):
    """检查用户名是否已存在"""
    print(1111)
    if request.method == 'POST':
        print(222)
        username = request.POST.get('username')
        print('username', username)
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            print("用户已存在")
            return JsonResponse(True, safe=False)  # 用户名已存在，返回 True
        else:
            print('当前用户名还未被注册,可以继续.....')
            return JsonResponse(False, safe=False)
    return JsonResponse({}, safe=False)


def insert(request):
    if request.method == 'POST':
        print(3333)
        username = request.POST.get('username')
        password = request.POST.get('password')
        nickname = request.POST.get('nickname')
        print('username: ', username)
        print('password: ', password)
        print('nickname: ', nickname)

        # 创建用户
        # User.objects.filter(username=username).exists()
        User.objects.create_user(username=username, password=password, nickname=nickname, status=1)
        return HttpResponse("User created successfully")
    else:
        return HttpResponse("Invalid request")  # 返回一个适当的响应


@csrf_exempt
def delete(request):
    """删除信息"""
    if request.method == 'POST':
        uid = request.POST.get('id')
        try:
            ob = User.objects.get(id=uid)
            ob.status = 9
            ob.update_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ob.save()
            # 返回响应给前端，确认删除成功
            response = {'message': '删除成功'}
        except Exception as err:
            print(err)
            # context = {"info": "删除失败"}
            response = {'message': '删除失败'}
        #
        # # return JsonResponse(context)
        # return render(request, "myadmin/info.html", context)
        return JsonResponse(response, status=200)


def edit(request):
    """加载编辑信息页面"""
    if request.method == 'GET':
        uid = request.GET.get('id')
        try:
            ob = User.objects.get(id=uid)
            context = {"user": ob}
            return render(request, "myadmin/user/edit.html", context)
        except Exception as err:
            context = {"info": err}
            return render(request, "myadmin/info.html", context)
    else:
        return HttpResponse("Invalid request")  # 返回一个适当的响应


@csrf_exempt
def update(request):
    """执行编辑信息"""
    if request.method == 'POST':
        uid = request.POST.get('id')
        print('uid: ', uid)
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
    else:
        return HttpResponse("Invalid request")  # 返回一个适当的响应


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
