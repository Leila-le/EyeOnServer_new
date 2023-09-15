import datetime
import logging

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from eye_on_server.tools.chart import Chart
import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse

from eye_on_server.models import SeverInfo, User

from django.db.models import Max

from eye_on_server.tools.send_dingtalk import send_alert_to_dingtalk


# Create your views here.
# 将收到的json数据存入数据库中
@csrf_exempt
def data_to_model(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        logging.debug("type-datas: %s", type(data))

        received_time = datetime.datetime.now()
        formatted_datetime = received_time.strftime("%Y-%m-%d %H:%M:%S")
        logging.debug('received_time', formatted_datetime)

        name = data['name']
        license_ = data['license_name']

        alerts = {'name:': name, 'license_name:': license_}
        alerts_data = {'name:': name, 'license_name:': license_}
        send_alert = False

        # 处理cpu数据
        for key, value in data['cpu'].items():
            setattr(alerts, key, value)

        # 处理磁盘数据
        for key, value in data['disk'].items():
            setattr(alerts, key, value)

        # 处理内存数据
        for key, value in data['memory'].items():
            setattr(alerts, key, value)

        if alerts['cpu_percent'] > 70:
            alerts_data['cpu_percent'] = alerts['cpu_percent']
            send_alert = True
        if alerts['memory_percent'] > 80:
            alerts_data['memory_percent'] = alerts['memory_percent']
            send_alert = True
        if alerts['disk_percent'] > 80:
            alerts_data['disk_percent'] = alerts['disk_percent']
            send_alert = True

        alerts['time'] = formatted_datetime
        alerts_data['time'] = alerts['time']
        if send_alert:
            send_alert_to_dingtalk("资源使用预警:\n", alerts_data)

        SeverInfo.objects.create(**alerts)

        return HttpResponse("ok")


# 用于将数据表中的数据转为json格式,传至对应的html页面中的table中
@login_required
def data_to_json(request):
    data = []
    unique_licenses = SeverInfo.objects.values_list('license_name', flat=True).distinct()
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)
    paginator = Paginator(unique_licenses, limit)

    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)

    count = 0
    for unique_license in page_data:
        server_info_list = SeverInfo.objects.filter(license_name=unique_license).values('name').annotate(
            max_time=Max('time'))
        for server_info in server_info_list:
            latest_record = SeverInfo.objects.filter(license_name=unique_license, name=server_info['name'],
                                                     time=server_info['max_time']).first()
            if latest_record:
                overview_data = {
                    'name': latest_record.name,
                    'license_name': latest_record.license_name,
                    'memory': latest_record.memory_percent,
                    'cpu': latest_record.cpu_percent,
                    'disk': latest_record.disk_percent,
                    'joinTime': latest_record.time
                }
                data.append(overview_data)
                count += 1

    merged_data = {
        'code': 0,
        'msg': '',
        'count': count,
        'data': data
    }
    return JsonResponse(merged_data)


@login_required
def sever_list(request):
    return render(request, 'web/ServerList.html')


# 用于获取数据库中唯一的license_name\name列表
def get_unique_license():
    unique_license = SeverInfo.objects.values_list('license_name', flat=True).distinct()
    unique_name = SeverInfo.objects.values_list('name', flat=True).distinct()
    unique_license_list = list(unique_license)
    unique_license_json = json.dumps(unique_license_list)
    return unique_license, unique_license_json, unique_name


# def get_draw_line(unique_license, unique_name):用于画折线图
def get_draw_line(unique_license_names, unique_names):
    data_lines = []
    disk_percent_list = []
    for unique_license_name in unique_license_names:
        for unique_name in unique_names:
            server_info_list = SeverInfo.objects.filter(license_name=unique_license_name, name=unique_name).order_by(
                'time')
            if server_info_list.exists():
                disk_percent = server_info_list.values('disk_percent').last()
                x_time = [info.time for info in server_info_list]
                y_cpu = [info.cpu_percent for info in server_info_list]
                y_memory = [info.memory_percent for info in server_info_list]
                chart = Chart()
                value_disk = disk_percent.get("disk_percent") if disk_percent else None
                data_line = chart.lines_chart(f'{unique_license_name}_{unique_name}',
                                              f'CPU_Usage_{unique_license_name}_{unique_name}',
                                              x_time, y_cpu, y_memory, value_disk)
                data_lines.append(data_line)
                disk_percent_list.append(value_disk)
    reversed_list = disk_percent_list[::-1]
    return data_lines, reversed_list


@login_required
# def draw_lines(request):用于实现CPU和内存使用率折线图,
# 需要调用get_draw_line(unique_license, unique_name)
def draw_lines(request):
    unique_license_names, unique_license_json, unique_names = get_unique_license()
    # 获取模型对象列表并陈列
    data_lines, reversed_list = get_draw_line(unique_license_names, unique_names)

    return render(request, "web/ServerChart.html",
                  {"data_lines": data_lines, "disk_percent": reversed_list, "unique_license_json": unique_license_json})


@login_required
# def search(request):用于实现ServerChart页面中的搜索功能
def search(request):
    if request.method == 'GET':
        search_list = []
        search_value = request.GET.get('keywords', "").strip()
        # print('search_value', search_value)
        search_list.append(search_value)
        _, unique_license_json, search_name = get_unique_license()
        result = SeverInfo.objects.filter(license_name=search_value).exists()
        if result:
            data_lines, reversed_list = get_draw_line(search_list, search_name)
            return render(request, "web/search.html", {"data_lines": data_lines, "disk_percent": reversed_list,
                                                       "unique_license_json": unique_license_json})


@login_required
# def theme(request):设置主题颜色
def save_theme(request):
    theme = request.GET.get('theme', 'default')
    context = {'theme': theme}
    return render(request, 'web/base.html', context)


@login_required
# def home(request):用于生成base页面以及传输基本数据
def home(request):
    _, unique_license_json, _ = get_unique_license()
    infos = SeverInfo.objects.all().order_by('-time')
    prefer_dark_mode = request.session.get('prefer_dark_mode', False)  # 从会话中获取主题选项，默认为 False
    context = {'infos': infos, 'prefer_dark_mode': prefer_dark_mode}
    return render(request, "web/base.html", locals())


@login_required
# def systems:用于查看每个系统的详细信息
def systems(request):
    if request.method == 'GET':
        license_name = request.GET.get('license_name')
        infos = SeverInfo.objects.filter(license_name=license_name).order_by('-time')
        info = infos.first()
        context = {'info': info}
        return render(request, "web/system.html", context=context)


# 初始话登陆页面
@login_required
def index(request):
    return render(request, "myadmin/user/index.html")


# 加载登录页面
def login_(request):
    return render(request, "myadmin/index/login.html")


# 执行登录
@csrf_exempt
def do_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        logging.debug('users %s', user)
        if user is not None:
            if ~user.is_active:
                # 处理用户状态为不活动的情况
                return JsonResponse({'status': 'stop_user', 'message': '账号已被禁用!'})
            else:
                # 处理登录成功的情况
                login(request, user)
                request.session['adminuser'] = user.toDict()
                if user.is_superuser:  # 为管理员则进入管理员页面
                    return JsonResponse({'status': 'manage_user', 'message': '登录成功'})
                elif user.is_staff:  # 为普通用户则进入普通页面
                    return JsonResponse({'status': 'common_user', 'message': '登录成功'})
        else:
            # 处理用户为 None 的情况
            error_message = '账号或密码错误!'
            return JsonResponse({'message': error_message})
    return HttpResponse('Invalid request')


# 执行退出
def logout(request):
    logout(request)
    return redirect('myadmin_login')


# 用于将数据表中的数据转为json格式,传至对应的html页面中的table中
def get_data(request):  # 表格展示内容
    queryset = User.objects.filter(status__lt=9)
    status_mapping = {
        1: '正常',
        2: '禁停',
        6: '管理员',
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
        'create_at': datetime.datetime.strftime(item.create_at, "%Y-%m-%d %H:%M:%S"),
        'update_at': datetime.datetime.strftime(item.update_at, "%Y-%m-%d %H:%M:%S"),

    } for item in page_data]

    return JsonResponse({
        'code': 0,
        'msg': '',
        'count': paginator.count,
        'data': data
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def index(request):
    """浏览信息"""
    return render(request, "myadmin/user/index.html")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def add(request):
    """加载添加页面"""
    return render(request, "myadmin/user/add.html")


def check_username(request):
    """检查用户名是否已存在"""
    if request.method == 'POST':
        username = request.POST.get('username')
        logging.debug('username: %s', username)
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            logging.debug("用户已存在")
            return JsonResponse(True, safe=False)  # 用户名已存在，返回 True
        else:
            logging.debug('当前用户名还未被注册,可以继续.....')
            return JsonResponse(False, safe=False)
    return JsonResponse({}, safe=False)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def insert(request):
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        # logging.debug('form: %s', form)
        username = request.POST.get('username')
        password = request.POST.get('password')
        nickname = request.POST.get('nickname')
        status = request.POST.get('status')
        logging.debug('status %s', status)
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists")
        # 创建用户
        try:
            if User.is_staff:
                User.objects.create_user(username=username, password=password, nickname=nickname, status=status,
                                             is_staff=1)
                logging.debug('成功创建普通账号')
            elif User.is_superuser:
                User.objects.create_user(username=username, password=password, nickname=nickname, status=status,
                                             is_superuser=1)
                logging.debug('成功创建管理员账号')
            return HttpResponse("User created successfully")
        except Exception as e:
            return HttpResponse(f"Failed to create user: {str(e)}")
    else:
        return HttpResponse("Invalid request")  # 返回一个适当的响应


@login_required
@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def delete(request):
    """删除信息"""
    if request.method == 'POST':
        uid = request.POST.get('id')
        try:
            User.objects.filter(id=uid).delete()
            # 返回响应给前端，确认删除成功
            response = {'message': '删除成功'}
        except Exception as err:
            logging.debug('err: %s', err)
            # context = {"info": "删除失败"}
            response = {'message': '删除失败'}
        #
        # # return JsonResponse(context)
        # return render(request, "myadmin/info.html", context)
        return JsonResponse(response, status=200)


@login_required
@user_passes_test(lambda u: u.is_superuser)
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
@login_required
@user_passes_test(lambda u: u.is_superuser)
def update(request):
    """执行编辑信息"""
    if request.method == 'POST':
        uid = request.POST.get('id')
        logging.debug('uid: %s', uid)
        try:
            ob = User.objects.get(id=uid)
            ob.nickname = request.POST['nickname']
            ob.status = request.POST['status']
            if ob.status == '6':
                ob.is_superuser = 1
            if ob.status == '1':
                ob.is_staff = 1
            ob.update_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ob.save()
            context = {"info": "修改成功！"}
        except Exception as err:
            logging.info('err %s', err)
            context = {"info": "修改失败"}
        return render(request, "myadmin/info.html", context)
    else:
        return HttpResponse("Invalid request")  # 返回一个适当的响应


@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_pass(request):
    """加载添加页面"""
    if request.method == 'GET':
        uid = request.GET.get('id')
        try:
            ob = User.objects.get(id=uid)
            context = {"user": ob}
            return render(request, "myadmin/user/resetpassword.html", context)
        except Exception as err:
            context = {"info": err}
            return render(request, "myadmin/info.html", context)
    else:
        return HttpResponse("Invalid request")  # 返回一个适当的响应


# @csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_password(request):
    """加载重置会员密码信息页面"""
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')

        new_password = make_password(new_password)

        try:
            ob = User.objects.get(username=username)
            ob.password = new_password
            ob.save()
            context = {"info": "修改成功！"}
        except Exception as err:
            logging.debug('err: %s', err)
            context = {"info": "修改失败"}
        return JsonResponse(context)
        # return render(request,'myadmin/info.html', context)
    else:
        return HttpResponse("Invalid request")  # 返回一个适当的响应
