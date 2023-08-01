from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from .models import SeverInfo
import datetime
import json
from django.http import JsonResponse


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


def get_message(request):
    if request.method == "POST":
        ip = get_client_ip(request)

        if not ip:
            return HttpResponseForbidden("Access denied")
        # 获取POST请求中的数据
        try:
            # Parse the JSON payload
            data = json.loads(request.body.decode('utf-8'))
            cpu_count = data.get("cpu_count")
            cpu_percent = data.get("cpu_percent")
            memory_total = data.get("men_total")
            mem_used = data.get("mem_used")
            memory_per = data.get("memory_per")
            disk_total = data.get("disk_total")
            disk_used = data.get("disk_used")
            disk_percent = data.get("disk_percent")
            net_sent = data.get("net_bytes_sent")
            net_rec = data.get("net_bytes_recv")
            time = timezone.now() + datetime.timedelta(hours=8)
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            error_message = str(e)
            cpu_count = 'error'
            cpu_percent = 'error'
            memory_total = 'error'
            mem_used = 'error'
            memory_per = 'error'
            disk_total = 'error'
            disk_used = 'error'
            disk_percent = 'error'
            net_sent = 'error'
            net_rec = 'error'
            # time = timezone.now() + datetime.timedelta(hours=8)
            time = timezone.now()
        # 使用同步方式保存服务器信息
        try:  # 尝试查找数据库中是否有相同ip地址的记录
            SeverInfo.objects.get(ip=ip)
        except:  # 不存在则创建一条新的记录,
            SeverInfo.objects.create(ip=ip, time=time, cpu_count=cpu_count, cpu_percent=cpu_percent,
                                     memory_total=memory_total, mem_used=mem_used, memory_per=memory_per,
                                     disk_total=disk_total, disk_used=disk_used, disk_percent=disk_percent,
                                     net_sent=net_sent, net_rec=net_rec)
        else:  # ip存在,更新字段
            SeverInfo.objects.filter(ip=ip).update(time=time, cpu_count=cpu_count, cpu_percent=cpu_percent,
                                                   memory_total=memory_total, mem_used=mem_used, memory_per=memory_per,
                                                   disk_total=disk_total, disk_used=disk_used,
                                                   disk_percent=disk_percent,
                                                   net_sent=net_sent, net_rec=net_rec)

    return HttpResponse("ok")


def home(request):
    infos = SeverInfo.objects.all()
    context = {'infos': infos}
    return render(request, "home.html", context=context)
