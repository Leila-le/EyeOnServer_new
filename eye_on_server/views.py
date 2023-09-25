import datetime
import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt
from eye_on_server.tools.chart import Chart
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse
from eye_on_server.models import SeverInfo, User
from django.db.models import Max

from eye_on_server.tools.send_dingtalk import process_message, schedule_send_alert_am9

logger = logging.getLogger(__name__)

bulletin = False

current_day = 0

reversed_name = []
reversed_license_name = []
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
        print('loadavg', alerts['loadavg'])
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
        get_warning(alerts)
        schedule_send_alert_am9()

        return HttpResponse("ok")


def get_warning(alerts):
    # infos = SeverInfo.objects.all()
    # for alerts in infos:
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

    return unique_license, unique_name


def get_draw_line(unique_license_names, unique_names):
    """
    生成图表数据和磁盘百分比列表。
    :param unique_license_names:(list) 唯一的许可证名称列表。
    :param unique_names:(list) 唯一的服务器名称列表。
    :return: tuple: 包含图表数据列表和反转后的磁盘百分比列表的元组。
    """
    data_lines = []
    disk_percent_list = []
    name_list = []
    license_name_list = []
    global reversed_name,reversed_license_name
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
                name_list.append(unique_name)
                license_name_list.append(unique_license_name)
    # 反转磁盘百分比列表
    reversed_list = disk_percent_list[::-1]
    reversed_name = name_list[::-1]
    reversed_license_name = license_name_list[::-1]
    return data_lines, reversed_list


@login_required
def draw_lines(request):
    """
    Requires:用户已登录。
    生成并渲染服务器图表。
    :param request:
    :return:  HttpResponse: 渲染后的HTML响应。
    """
    unique_license_names, unique_names = get_unique_license()
    # 获取模型对象列表并陈列
    data_lines, reversed_list = get_draw_line(unique_license_names, unique_names)
    return render(request, "eye_on_server/web/ServerChart.html",
                  {"data_lines": data_lines,
                   "disk_percent": reversed_list})


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
        _, search_name = get_unique_license()
        result = SeverInfo.objects.filter(license_name=search_value).exists()
        if result:
            data_lines, reversed_list = get_draw_line(search_list, search_name)
            return render(request, "eye_on_server/web/search.html",
                          {"data_lines": data_lines, "disk_percent": reversed_list})


@login_required
# @csrf_exempt
def day_data(request):
    """
    展示今、昨当天数据表
    :param request:
    :return:
    """
    if request.method == 'GET':
        day = request.GET.get('date')
        value = request.GET.get('value')
        data_index = request.GET.get('dataIndex')
        print("dataIndex", data_index)

        license_name = reversed_license_name[int(data_index)]

        name = reversed_name[int(data_index)]
        print('license_name: {},name: {}'.format(license_name, name))
        print("day", day)
        if value == 'all-day':
            draw_lines()
        if value == 'yesterday':
            return JsonResponse({"message": "暂无昨日信息!"})
        else:
            # data_lines = []
            # disk_percent_list = []
            disk_percent = 0
            data_day = SeverInfo.objects.filter(time__date=day, license_name=license_name, name=name)
            if data_day.values('disk_percent') is not None:
                disk_percent = data_day.values('disk_percent').last()
            # 提取时间、CPU使用率和内存百分比
            x_time = [info.localized_time.strftime('%Y-%m-%d %H:%M:%S') for info in data_day]
            y_cpu = [info.percent for info in data_day]
            y_memory = [info.memory_percent for info in data_day]
            # 创建图表对象
            chart = Chart()
            # 生成图表数据
            data_line = chart.lines_chart(f'{license_name}_{name}',
                                          f'CPU_Usage_{license_name}_{name}',
                                          x_time, y_cpu, y_memory)
            # 添加图标数据和磁盘百分比到相应列表
            # data_lines.append(data_line)
            # return render(request, "eye_on_server/web/ServerChart.html",
            #               {"data_line": data_line, "disk_percent": disk_percent})
            return JsonResponse({"data_line": data_line, "disk_percent": disk_percent})

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
