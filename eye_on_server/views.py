import datetime
import logging
from collections import deque, defaultdict

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
from django.db.models import Max
from django.core.cache import cache
from eye_on_server.tools.send_dingtalk import process_message
from eye_on_server.tools.task import process_data_and_save

logger = logging.getLogger(__name__)

bulletin = False

current_day = 0
last_warning_time = 0
CACHE_SIZE = 100
data_cache = defaultdict(lambda: deque(maxlen=CACHE_SIZE))


@csrf_exempt
def data_to_model(request):
    """
    将接收到的数据存入数据库，并检查是否超过阈值，发送钉钉消息。
    :param request: HTTP请求对象。
    :return: HttpResponse: HTTP响应对象。
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 提取数据中的服务器名称和许可证名称
            name = data['name']
            license_ = data['license_name']
            if not name or not license_:
                return HttpResponse("Invalid data", status=400)

            # 创建包含服务器名称和许可证名称的alerts字典
            alerts = {'name': name, 'license_name': license_}
            alerts.update({'time': timezone.localtime(timezone.now())})
            # 处理cpu数据
            for key, value in data['cpu'].items():
                alerts[key] = value
            alerts['percent'] = round(alerts['percent'] * 100, 2)
            logging.debug("alerts: %s", alerts)
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
            if alerts['total_physics'] != 0:
                memory_percent = round(alerts['used_physics'] / alerts['total_physics'] * 100, 2)
            else:
                memory_percent = 0

            if alerts['total_swap'] != 0:
                swap_percent = round(alerts['used_swap'] / alerts['total_swap'] * 100, 2)
            else:
                swap_percent = 0
            alerts.update({'memory_percent': memory_percent})
            alerts.update({'swap_percent': swap_percent})
            # 将alerts字典存入数据库的ServerInfo模型中
            # SeverInfo.objects.create(**alerts)
            process_data_and_save.delay(alerts)  # 异步存入数据库
            get_warning_star(alerts)
            get_cache_DB(alerts)
            return HttpResponse("ok")
        except json.JSONDecodeError:
            return HttpResponse("Invalid JSON data", status=400)
    else:
        return HttpResponse("Method not allowed", status=405)


def get_cache_DB(alerts):
    data_key = str(alerts['name']) + str(alerts['license_name'])
    cache.add(data_key, alerts, 20)  # 缓存
    # 检查redis缓存中是否存在名为'unique_name'和'unique_license_names'的缓存
    unique_names = cache.get("unique_names")
    unique_license_names = cache.get("unique_license_names")
    # 没有则将相关列表转为元组进行缓存
    if unique_names is None:
        unique_names = []
    if unique_license_names is None:
        unique_license_names = []
    # 将新的name和license_name追加到相应的列表中
    unique_names.append(alerts['name'])
    unique_license_names.append(alerts['license_name'])
    # 去除重复项
    unique_names = list(set(unique_names))
    unique_license_names = list(set(unique_license_names))
    cache.add('unique_names', unique_names, 60)
    cache.add('unique_license_names', unique_license_names, 60)


def get_warning_star(alerts):
    # 设置阈值，用于比较
    cpu_threshold = 80
    memory_threshold = 80
    disk_threshold = 80
    keys = []
    if alerts['percent'] > cpu_threshold:
        key = alerts['name'] + '-' + alerts['license_name'] + '-' + 'CPU'
        keys.append(key)
        cpu_percent_max = alerts['percent']
        cached_value = cache.get(key)
        if cached_value is None:
            cache.add(key, cpu_percent_max, 10)
        elif cached_value < cpu_percent_max:
            cache.add(key, cpu_percent_max, 10)
    if alerts['memory_percent'] > memory_threshold:
        key = alerts['name'] + '-' + alerts['license_name'] + '-' + '内存'
        keys.append(key)
        memory_percent_max = alerts['memory_percent']
        cached_value = cache.get(key)
        if cached_value is None:
            cache.add(key, memory_percent_max, 10)
        elif cached_value < memory_percent_max:
            cache.add(key, memory_percent_max, 10)
    if alerts['disk_percent'] > disk_threshold:
        key = alerts['name'] + '-' + alerts['license_name'] + '-' + '磁盘'
        keys.append(key)
        disk_percent_max = alerts['disk_percent']
        cached_value = cache.get(key)
        if cached_value is None:
            cache.add(key, disk_percent_max, 10)
        elif cached_value < disk_percent_max:
            cache.add(key, disk_percent_max, 10)
    if keys is not None:
        # 执行获取警告消息的逻辑
        process_message(keys)  # 发送实时消息
    else:
        return


@login_required
def data_to_json(request):
    """
    将服务器信息转为JSON格式并返回给客户端
    :param request: Http请求对象
    :return: JsonResponse: 包含服务器信息的JSON响应对象
    """
    data = []
    # 先从缓存中获取唯一的许可名称
    unique_license = cache.get("unique_license_names")
    flag = 1
    unique_name = cache.get("unique_names")
    print("unique_name", unique_name)
    # 缓存中没有则从SeverInfo中获取唯一的许可名称
    if unique_license is None:
        flag = 0
        unique_licenses = SeverInfo.objects.values_list('license_name', flat=True).distinct()
        unique_license = unique_licenses.order_by('license_name')
    # 获取请求中的页码和每页限制数
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)
    # 使用分页器进行分页
    paginator = Paginator(unique_license, limit)

    try:
        page_data = paginator.page(page)  # 获取指定页码的数据
    except PageNotAnInteger:
        page_data = paginator.page(1)  # 如果页码超过范围,则默认返回第一页的数据
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)  # 如果页码超过范围,则返回最后一页数据

    count = 0  # 计算数据总数
    for unique_license in page_data:
        if flag:
            for name in unique_name:
                key = name + unique_license
                latest_record = cache.get(key)
                print("cache_latest_record", latest_record)
                if latest_record:
                    overview_data = {
                        'name': latest_record['name'],
                        'license_name': latest_record['license_name'],
                        'memory': latest_record['memory_percent'],
                        'cpu': latest_record['percent'],
                        'disk': latest_record['disk_percent'],
                        'joinTime': latest_record['time'].strftime('%Y-%m-%d %H:%M:%S')
                    }
                    data.append(overview_data)
                    count += 1
        else:
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
                        'joinTime': latest_record.time.strftime('%Y-%m-%d %H:%M:%S')
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


def get_draw_line(unique_license_names, **kwargs):
    """
    生成图表数据和磁盘百分比列表。
    :return: tuple: 包含图表数据列表和反转后的磁盘百分比列表的元组。
    """
    data_lines = []
    disk_percent_list = []
    # 遍历唯一的许可证名称和服务器名称
    for unique_license_name in unique_license_names:
        print('unique_license_name',unique_license_name)
        # 查询服务器信息
        if kwargs:
            start_time = kwargs.get('start_time')
            end_time = kwargs.get('end_time')
            server_info_list = SeverInfo.objects.filter(license_name=unique_license_name,
                                                        time__range=(start_time, end_time)).order_by('time')
        else:
            server_info_list = SeverInfo.objects.filter(license_name=unique_license_name).order_by('time')
        if server_info_list.exists():
            # 提取时间、CPU使用率和内存百分比
            x_time = [info.time.strftime('%Y-%m-%d %H:%M:%S') for info in server_info_list]
            y_cpu = [info.percent for info in server_info_list]
            y_memory = [info.memory_percent for info in server_info_list]
            unique_name = server_info_list.values("name").first()
            # print("x_time{},y_cpu{},y_memory{}".format(x_time,y_cpu,y_memory))
            # 创建图表对象
            chart = Chart()
            # 生成图表数据
            try:
                data_line = chart.lines_chart(f'{unique_license_name}_{unique_name}',
                                              f'CPU_Usage_{unique_license_name}_{unique_name}',
                                              x_time, y_cpu, y_memory)
                # 添加图标数据和磁盘百分比到相应列表
                data_lines.append(data_line)
                # print("dataline{}".format(data_line))
            except Exception as e:
                print(e)

            # 获取最后一个服务器信息的磁盘百分比
            disk_percent = server_info_list.values('disk_percent').last()
            # 获取磁盘百分比
            value_disk = disk_percent.get("disk_percent") if disk_percent else None
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
    # 删除七天以前的数据库记录
    delete_old_records()
    if 'str_value' in request.session:
        del request.session['str_value']
    # 从SeverInfo中获取唯一的许可名称
    unique_license_names = cache.get("unique_license_names")
    print("draw_lines:unique_license_names", unique_license_names)
    if unique_license_names is None:
        unique_license_names = SeverInfo.objects.values_list('license_name', flat=True).distinct()
        print("draw_lines:unique_license_names_server", unique_license_names)
        # 获取模型对象列表并陈列
    data_lines, reversed_list = get_draw_line(unique_license_names)
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
        search_value = request.GET.get('keywords')
        request.session['str_value'] = search_value
        result = SeverInfo.objects.filter(license_name=search_value).exists()
        if result:
            # 从SeverInfo中获取唯一的服务器名称
            list_value = search_value.split()  # 将字符串转列表
            data_lines, reversed_list = get_draw_line(list_value)
            return render(request, "eye_on_server/web/search.html",
                          {"data_lines": data_lines, "disk_percent": reversed_list, "search_value": search_value})
        else:
            return JsonResponse({"message": "未找到相关结果"})


@login_required
def day_data(request):
    """
    展示最近一小时或最近一天或最近一周的图标
    :param request:
    :return:
    """
    if request.method == 'GET':
        value = request.GET.get('value')
        current = timezone.now()
        if value == "last_hour":
            start_time = current - datetime.timedelta(hours=1)
        elif value == "last_day":
            start_time = current - datetime.timedelta(days=1)
        elif value == "last_week":
            start_time = current - datetime.timedelta(weeks=1)
        else:
            return JsonResponse({"message": "Invalid value"})
        if 'str_value' in request.session:  # 如果是在搜索界面提出的申请
            str_value = request.session['str_value']
            unique_license = str_value.split()  # 将字符串转列表
            level = str_value
        else:
            # 先从缓存中获取唯一的许可名称
            unique_license = cache.get("unique_license_names")
            # 缓存中没有则从SeverInfo中获取唯一的许可名称
            if unique_license is None:
                unique_license = SeverInfo.objects.values_list('license_name', flat=True).distinct()
            level = '资源图'
        get_time = {"start_time": start_time, "end_time": current, "select_time": value}
        data_lines, reversed_list = get_draw_line(unique_license, **get_time)
        if data_lines:
            return render(request, "eye_on_server/web/DayChart.html",
                          {"new_data_lines": data_lines,
                           "new_disk_percent": reversed_list,
                           "value": value,
                           "level": level})
        else:
            return JsonResponse({"message": "未找到相关结果"})
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


def delete_old_records():
    # 计算七天前的时间日期
    cutoff_date = timezone.now() - datetime.timedelta(weeks=1)
    records_to_delete = SeverInfo.objects.filter(time__lt=cutoff_date)

    # 执行删除
    records_to_delete.delete()
