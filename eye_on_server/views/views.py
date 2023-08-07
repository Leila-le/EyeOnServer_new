import threading

from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from eye_on_server.models import SeverInfo
import json
import datetime
from .ip_status import test_ip_status
from .send_dingtalk import send_alert_to_dingtalk

from .chart import Chart

# Create your views here.
def get_client_ip(request):
    # 尝试从HTTP_X_FORWARDED_FOR请求头获取IP地址
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # HTTP_X_FORWARDED_FOR可能包含多个IP地址，取第一个即可
        client_ip = x_forwarded_for.split(',')[0]
    else:
        # 如果HTTP_X_FORWARDED_FOR请求头不存在，从REMOTE_ADDR获取IP地址
        client_ip = request.META.get("REMOTE_ADDR")
    if client_ip in ['127.0.0.1', '::1']:
        client_ip = 'localhost'
    return client_ip


@csrf_exempt
# def get_message(request):
#     if request.method == "POST":
#         ip = get_client_ip(request)
#
#         if not ip:
#             return HttpResponseForbidden("Access denied")
#         # 获取POST请求中的数据
#         try:
#             # Parse the JSON payload
#             data = json.loads(request.body.decode('utf-8'))
#             cpu_count = data.get("cpu_count")
#             cpu_percent = data.get("cpu_percent")
#             memory_total = data.get("men_total")
#             mem_used = data.get("mem_used")
#             memory_per = data.get("memory_per")
#             disk_total = data.get("disk_total")
#             disk_used = data.get("disk_used")
#             disk_percent = data.get("disk_percent")
#             net_sent = data.get("net_bytes_sent")
#             net_rec = data.get("net_bytes_recv")
#             status = data.get('status')
#
#         except json.JSONDecodeError as e:
#             # Handle JSON decoding errors
#             # error_message = str(e)
#             cpu_count = '-1'
#             cpu_percent = '-1'
#             memory_total = '-1'
#             mem_used = '-1'
#             memory_per = '-1'
#             disk_total = '-1'
#             disk_used = '-1'
#             disk_percent = '-1'
#             net_sent = '-1'
#             net_rec = '-1'
#             status = 'offline'
#
#             # time = timezone.now() + datetime.timedelta(hours=8)
#         time = timezone.now()  # + datetime.timedelta(hours=8)
#         alerts = {'ip: ': ip}
#         if cpu_percent > 5:
#             alerts.update({"cpu已使用: ": cpu_percent})
#             # send_alert_to_dingtalk(ip, {"cpu已使用:": cpu_percent})
#         if memory_per > 90:
#             alerts.update({"内存已使用: ": memory_per})
#             # send_alert_to_dingtalk(ip, {"内存已使用:": memory_per})
#         if disk_percent > 80:
#             alerts.update({"磁盘已使用: ": disk_percent})
#             # send_alert_to_dingtalk(ip, {"磁盘已使用:": disk_percent})
#         time_ = now_time()
#         alerts.update({" ": time_})
#         if len(alerts) >= 3:
#             send_alert_to_dingtalk("资源使用超过预警:\n", alerts)
#         # 使用同步方式保存服务器信息
#         try:  # 尝试查找数据库中是否有相同ip地址的记录
#             SeverInfo.objects.get(ip=ip)
#         except:  # 不存在则创建一条新的记录,
#             SeverInfo.objects.create(ip=ip, time=time, cpu_count=cpu_count, cpu_percent=cpu_percent,
#                                      memory_total=memory_total, mem_used=mem_used, memory_per=memory_per,
#                                      disk_total=disk_total, disk_used=disk_used, disk_percent=disk_percent,
#                                      net_sent=net_sent, net_rec=net_rec, status=status)
#         else:  # ip存在,更新字段
#             SeverInfo.objects.filter(ip=ip).update(time=time, cpu_count=cpu_count, cpu_percent=cpu_percent,
#                                                    memory_total=memory_total, mem_used=mem_used, memory_per=memory_per,
#                                                    disk_total=disk_total, disk_used=disk_used,
#                                                    disk_percent=disk_percent,
#                                                    net_sent=net_sent, net_rec=net_rec, status=status)
#
#     return HttpResponse("ok")


def upload_files(request):
    # global data_list  # 声明为全局变量
    data_list = []
    if request.method == 'POST':
        files = request.FILES.getlist('files')  # 获取上传的文件列表

        for file in files:
            # 处理每个文件，例如读取内容或保存到数据库等
            file_content = file.read().decode('utf-8')  # 读取文件内容并解码为字符串
            # 处理文件内容
            # 将Json数据解析为Python对象
            json_data = json.loads(file_content)
            print('json_data:',json_data)
            data_list.append(json_data)

        return render(request, 'success.html')

    return render(request, 'base.html')


def cpu_percent_line(request, data):
    chart = Chart()
    cpu_data_line = chart.line_chart('cpu_avg', 'cpu平均使用率', timezone.now(), cpu_percent)

    return render(request, 'monitor/cpu_m.html', locals())


def disk_percent_line(request, data):
    chart = Chart()
    disk_data_line = chart.line_chart('cpu_avg', 'cpu平均使用率', timezone.now(), disk_used / disk_total)

    return render(request, 'monitor/disk_m.html', locals())


def memory_percent_line(request, data):
    chart = Chart()
    cpu_data_line = chart.line_chart('cpu_avg', 'cpu平均使用率', timezone.now(), memory_percent)

    return render(request, 'monitor/memory_m.html', locals())

# def line(request):
#     return render(request, 'basic_line_chart.html')


def home(request):
    alert = {}
    ip_list = SeverInfo.objects.values_list('ip', flat=True)
    threading.Thread(target=test_ip_status, args=(ip_list, alert)).start()
    # test_ip_status(ip_list)

    infos = SeverInfo.objects.all().order_by('-time')
    context = {'infos': infos}
    return render(request, "base.html", context=context)


