import datetime
import logging

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from eye_on_server.tools.chart import Chart
import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse

from eye_on_server.models import SeverInfo, User

from django.db.models import Max

from eye_on_server.tools.send_dingtalk import send_alert_to_dingtalk

logger = logging.getLogger(__name__)


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

        alerts = {'name': name, 'license_name': license_}
        alerts_data = {'name:': name, 'license_name:': license_}
        send_alert = False

        # 处理cpu数据
        for key, value in data['cpu'].items():
            # setattr(alerts, key, value)
            alerts[key] = value
        alerts['percent'] = round(alerts['percent'] * 100, 2)
        logging.debug("alerts: %s", alerts)

        # 处理磁盘数据
        for key, value in data['disk'].items():
            # setattr(alerts, key, value)
            alerts[key] = value
            logging.info("alerts: %s", alerts)
        print("disk", alerts)
        disk_percent = round(alerts['used'] / alerts['total'] * 100, 2)
        alerts.update({'disk_percent': disk_percent})
        logging.debug("alerts: %s", alerts)
        # 处理内存数据
        for key, value in data['memory'].items():
            # setattr(alerts, key, value)
            alerts[key] = value
        memory_percent = round(alerts['used_physics'] / alerts['total_physics'] * 100, 2)
        swap_percent = round(alerts['used_swap'] / alerts['total_swap'] * 100, 2)
        alerts.update({'memory_percent': memory_percent})
        alerts.update({'swap_percent': swap_percent})
        logging.debug("alerts: %s", alerts)

        if alerts['percent'] > 70:
            alerts_data['CPU使用率: '] = alerts['percent']
            send_alert = True
        if alerts['memory_percent'] > 80:
            alerts_data['内存使用率: '] = alerts['memory_percent']
            send_alert = True
        if alerts['disk_percent'] > 80:
            alerts_data['磁盘使用率: '] = alerts['disk_percent']
            send_alert = True

        alerts['time'] = formatted_datetime
        alerts_data['时间: '] = alerts['time']
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
                    'cpu': latest_record.percent,
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
    return render(request, 'eye_on_server/web/ServerList.html')


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
                y_cpu = [info.percent for info in server_info_list]
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

    return render(request, "eye_on_server/web/ServerChart.html",
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
            return render(request, "eye_on_server/web/search.html",
                          {"data_lines": data_lines, "disk_percent": reversed_list,
                           "unique_license_json": unique_license_json})


@login_required
# def theme(request):设置主题颜色
def save_theme(request):
    theme = request.GET.get('theme', 'default')
    context = {'theme': theme}
    return render(request, 'eye_on_server/web/base.html', context)


@login_required
# def home(request):用于生成base页面以及传输基本数据
def home(request):
    _, unique_license_json, _ = get_unique_license()
    infos = SeverInfo.objects.all().order_by('-time')
    prefer_dark_mode = request.session.get('prefer_dark_mode', False)  # 从会话中获取主题选项，默认为 False
    context = {'infos': infos, 'prefer_dark_mode': prefer_dark_mode}
    return render(request, "eye_on_server/web/base.html", locals())


@login_required
# def systems:用于查看每个系统的详细信息
def systems(request):
    if request.method == 'GET':
        license_name = request.GET.get('license_name')
        infos = SeverInfo.objects.filter(license_name=license_name).order_by('-time')
        info = infos.first()
        context = {'info': info}
        return render(request, "eye_on_server/web/system.html", context=context)


class MyLoginView(LoginView):
    # 登陆成功后要跳转的页面URL
    def get_success_url(self):
        return '/web/'


# 执行退出
def logout_view(request):
    logout(request)
    return redirect('login')


# 添加新用户
@receiver(post_save, sender=User)
def handle_user_registration(sender, instance, created, **kwargs):
    if created:
        # 这里可以处理新注册用户的逻辑
        password = instance.password  # 获取注册页面输入的密码
        instance.set_password(password)  # 设置密码
        instance.save()  # 保存用户对象

