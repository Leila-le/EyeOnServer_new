import datetime
import logging
import time

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from eye_on_server.tools.chart import Chart
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse
from eye_on_server.models import SeverInfo, User
from django.db.models import Max, Q
from eye_on_server.tools.send_dingtalk import process_message

logger = logging.getLogger(__name__)


@csrf_exempt
def data_to_model(request):
    """
    将接收到的数据存入数据库，并检查是否超过阈值，发送钉钉消息。
    :param request: HTTP请求对象。
    :return: HttpResponse: HTTP响应对象。
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        # 提取数据中的服务器名称和许可证名称
        name = data['name']
        license_ = data['license_name']
        # 创建包含服务器名称和许可证名称的alerts字典
        alerts = {'name': name, 'license_name': license_}
        # 处理cpu数据
        for key, value in data['cpu'].items():
            alerts[key] = value
        alerts['percent'] = round(alerts['percent'] * 100, 2)
        logging.debug("alerts: %s", alerts)
        alerts['loadavg'] = alerts['total_active'] / (alerts['total_active'] + alerts['total_idle'])
        # 处理磁盘数据
        for key, value in data['disk'].items():
            alerts[key] = value
            logging.info("alerts: %s", alerts)
        disk_percent = round(alerts['used'] / alerts['total'] * 100, 2)
        alerts.update({'disk_percent': disk_percent})
        logging.debug("alerts: %s", alerts)
        # 处理内存数据
        for key, value in data['memory'].items():
            alerts[key] = value
        memory_percent = round(alerts['used_physics'] / alerts['total_physics'] * 100, 2)
        swap_percent = round(alerts['used_swap'] / alerts['total_swap'] * 100, 2)
        alerts.update({'memory_percent': memory_percent})
        alerts.update({'swap_percent': swap_percent})
        logging.debug("alerts: %s", alerts)
        # 将alerts字典存入数据库的ServerInfo模型中
        SeverInfo.objects.create(**alerts)

        received_time = datetime.datetime.now()
        formatted_datetime = received_time.strftime("%Y-%m-%d %H:%M:%S")
        # 设置阈值，用于比较
        cpu_threshold = 80
        memory_threshold = 80
        disk_threshold = 80
        # 初始化消息列表和标志变量
        messages = []
        flag = False
        # 检查CPU使用率是否超过阈值
        if alerts['percent'] > cpu_threshold:
            message = f"系统: {alerts['name']}\n许可:{alerts['license_name']}\n时间:{formatted_datetime}\n" \
                      f"CPU使用率: {alerts['percent']}%"
            messages.append(message)
            flag = True
        # 检查内存使用率是否超过阈值
        if alerts['memory_percent'] > memory_threshold:
            if flag:
                message = f"内存使用率: {alerts['memory_percent']}%"

            else:
                message = f"系统: {alerts['name']}\n许可:{alerts['license_name']}\n时间:{formatted_datetime}\n" \
                          f"内存使用率: {alerts['memory_percent']}%"
            messages.append(message)
            flag = True
        # 检查磁盘使用率是否超过阈值
        if alerts['disk_percent'] > disk_threshold:
            if flag:
                message = f"\n磁盘使用率: {alerts['disk_percent']}%"
            else:
                message = f"系统: {alerts['name']}\n许可:{alerts['license_name']}\n时间:{formatted_datetime}\n" \
                          f"磁盘使用率: {alerts['disk_percent']}%"
            messages.append(message)
        # 将当前收集到的超过阈值的内容传至send_alert_to_dingtalk进行发送钉钉消息准备
        if messages:
            process_message("".join(messages))
        return HttpResponse("ok")


def get_message():
    infos = SeverInfo.objects.all()
    unique_license_names, _, unique_names = get_unique_license()
    # 遍历唯一的许可证名称和服务器名称
    for unique_license_name in unique_license_names:
        for unique_name in unique_names:
            # 查询服务器信息
            server_info_list = SeverInfo.objects.filter(license_name=unique_license_name, name=unique_name).order_by(
                'time')
            current_time = timezone.now()  # 获取当前时间戳
            # 计算5分钟前的时间
            five_minutes_ago = current_time - datetime.timedelta(minutes=5)
            fifteen_minutes_ago = current_time - datetime.timedelta(minutes=5)
            # 执行查询，获取在5分钟前之后创建的数据库信息
            results_five = server_info_list.objects.filter(Q(created_at__gte=five_minutes_ago))
            results_fifteen = server_info_list.objects.filter(Q(created_at__gte=fifteen_minutes_ago))
            for info in server_info_list:
                base_info = f"""> 您的云服务器已运行-{info['uptime']}，
                机器负载情况为(最近1、5、15分钟)：{info['loadavg'], results_five['loadavg'], results_fifteen['loadavg']}
                        - 目前CPU使用率为：{info['percent']}%，
                        - 系统运行内存使用率为：{info['memory_percent']}%，
                        - 剩余可用运行内存为：{info['free_physics'] / (1024 * 1024 * 1024)}GiB，
                        - 系统存储内存使用率为：{info['disk_percent']}%，
                        - 剩余可用存储内存为：{info['free'] / (1024 * 1024 * 1024)}GiB
                        <br>**{'机器CPU使用率正常' if info['percent'] <= 80 else '机器CPU使用率过高，可能触发预警'}**
                        <br>**{'机器内存使用率正常' if info['memory_percent'] <= 80 else '机器CPU使用率过高，可能触发预警'}**
                        <br>**{'机器磁盘使用率正常' if info['disk_percent'] <= 80 else '机器CPU使用率过高，可能触发预警'}**
                        """


@login_required
def data_to_json(request):
    """
    将服务器信息转为JSON格式并返回给客户端
    :param request: Http请求对象
    :return: JsonResponse: 包含服务器信息的JSON响应对象
    """
    data = []
    # 获取所有唯一的许可证名称
    unique_licenses = SeverInfo.objects.values_list('license_name', flat=True).distinct()
    # 获取请求中的页码和每页限制数
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)
    # 使用分页器进行分页
    paginator = Paginator(unique_licenses, limit)

    try:
        page_data = paginator.page(page)  # 获取指定页码的数据
    except PageNotAnInteger:
        page_data = paginator.page(1)  # 如果页码超过范围,则默认返回第一页的数据
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)  # 如果页码超过范围,则返回最后一页数据

    count = 0  # 计算数据总数
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
    """
    显示服务器列表页面
    :param request: Http请求对象
    :return: HttpResponse: 包含服务器列表页面内容的HTML响应。
    """
    return render(request, 'eye_on_server/web/ServerList.html')


def get_unique_license():
    """
    获取唯一的许可证名称和服务器名称，并将其转换为JSON格式。
    :return:tuple: 包含唯一许可证名称、转换为JSON格式的唯一许可证名称和唯一服务器名称的元组。
    """
    # 从SeverInfo中获取唯一的许可名称
    unique_license = SeverInfo.objects.values_list('license_name', flat=True).distinct()
    # 从SeverInfo中获取唯一的服务器名称
    unique_name = SeverInfo.objects.values_list('name', flat=True).distinct()
    # 将唯一的许可证名称转换为列表
    unique_license_list = list(unique_license)
    # 将唯一的许可证名称转换为JSON格式
    unique_license_json = json.dumps(unique_license_list)

    return unique_license, unique_license_json, unique_name


def get_draw_line(unique_license_names, unique_names):
    """
    生成图表数据和磁盘百分比列表。
    :param unique_license_names:(list) 唯一的许可证名称列表。
    :param unique_names:(list) 唯一的服务器名称列表。
    :return: tuple: 包含图表数据列表和反转后的磁盘百分比列表的元组。
    """
    data_lines = []
    disk_percent_list = []
    # 遍历唯一的许可证名称和服务器名称
    for unique_license_name in unique_license_names:
        for unique_name in unique_names:
            # 查询服务器信息
            server_info_list = SeverInfo.objects.filter(license_name=unique_license_name, name=unique_name).order_by(
                'time')
            if server_info_list.exists():
                # 获取最后一个服务器信息的磁盘百分比
                disk_percent = server_info_list.values('disk_percent').last()
                # 提取时间、CPU使用率和内存百分比
                x_time = [info.localized_time.strftime('%Y-%m-%d %H:%M:%S') for info in server_info_list]
                y_cpu = [info.percent for info in server_info_list]
                y_memory = [info.memory_percent for info in server_info_list]
                # 获取磁盘百分比
                value_disk = disk_percent.get("disk_percent") if disk_percent else None
                # 创建图表对象
                chart = Chart()
                # 生成图表数据
                data_line = chart.lines_chart(f'{unique_license_name}_{unique_name}',
                                              f'CPU_Usage_{unique_license_name}_{unique_name}',
                                              x_time, y_cpu, y_memory)
                # 添加图标数据和磁盘百分比到相应列表
                data_lines.append(data_line)
                disk_percent_list.append(value_disk)
    # 反转磁盘百分比列表
    reversed_list = disk_percent_list[::-1]

    return data_lines, reversed_list


@login_required
def draw_lines(request):
    """
    Requires:用户已登录。
    生成并渲染服务器图表。
    :param request:
    :return:  HttpResponse: 渲染后的HTML响应。
    """
    unique_license_names, unique_license_json, unique_names = get_unique_license()
    # 获取模型对象列表并陈列
    data_lines, reversed_list = get_draw_line(unique_license_names, unique_names)
    return render(request, "eye_on_server/web/ServerChart.html",
                  {"data_lines": data_lines,
                   "disk_percent": reversed_list,
                   "unique_license_json": unique_license_json})


@login_required
def search(request):
    """
    处理搜索请求并显示搜索结果
    :param request: HTTP请求对象
    :return: HttpResponse: 包含主页内容的HTML响应
    """
    if request.method == 'GET':
        search_list = []
        search_value = request.GET.get('keywords', "").strip()
        search_list.append(search_value)
        _, unique_license_json, search_name = get_unique_license()
        result = SeverInfo.objects.filter(license_name=search_value).exists()
        if result:
            data_lines, reversed_list = get_draw_line(search_list, search_name)
            return render(request, "eye_on_server/web/search.html",
                          {"data_lines": data_lines, "disk_percent": reversed_list,
                           "unique_license_json": unique_license_json})


@login_required
# @csrf_exempt
def day_data(request):
    if request == 'GET':
        print(111)
        day = request.GET.get('date')
        if day == 1:
            draw_lines()
        if day is None:
            return JsonResponse({"message": "暂无昨日信息!"})
        else:
            data_day = SeverInfo.objects.filter(time__date=day)

            print("data_day", data_day)
            return render(request, 'eye_on_server/web/ServerChart.html')

    return HttpResponse("Invalid quest")


@login_required
def home(request):
    """
    显示客户端主页
    :param request: HTTP请求对象
    :return:HttpResponse: 包含主页内容的HTML响应
    """
    return render(request, "eye_on_server/web/base.html")


@login_required
def systems(request):
    """
    显示特定许可证名称的服务器信息。
    :param request:HTTP请求对象。
    :return:HttpResponse: 包含特定许可证名称的服务器信息的HTML响应。
    """
    if request.method == 'GET':
        license_name = request.GET.get('license_name')
        infos = SeverInfo.objects.filter(license_name=license_name).order_by('-time')
        info = infos.first()  # 获取最新的服务器信息
        context = {'info': info}
        return render(request, "eye_on_server/web/system.html", context=context)


class MyLoginView(LoginView):
    # 自定义的登陆视图类,继承Django内置的LoginView
    def get_success_url(self):
        """
        获取登录成功后要跳转的页面URL。
        :return: 登陆成功后要跳转的页面URL
        """
        return '/web/'


def logout_view(request):
    # 执行退出
    logout(request)
    return redirect('login')


@receiver(post_save, sender=User)
def handle_user_registration(sender, instance, created, **kwargs):
    """
    处理用户注册事件的信号处理函数
    :param sender:发送信号的模型类
    :param instance:与信号相关联的模型实例
    :param created:指示是否新创建的实例
    :param kwargs:其他信号参数
    :return:None
    """
    if created:
        # 处理新注册用户的逻辑
        password = instance.password  # 获取注册页面输入的密码
        instance.set_password(password)  # 设置密码
        instance.save()  # 保存用户对象
