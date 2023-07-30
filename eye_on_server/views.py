import datetime

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from .models import SeverInfo


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
    return client_ip


def get_message(request):
    if request.method == "POST":
        ip = get_client_ip(request)
        if not ip:
            return HttpResponseForbidden("Access denied")
        # 获取POST请求中的数据
        cpu_count = request.POST.get("cpu_count")
        cpu_percent = request.POST.get("cpu_percent")
        memory_total = request.POST.get("men_total")
        mem_used = request.POST.get("mem_used")
        memory_per = request.POST.get("mem_percent")
        disk_total = request.POST.get("disk_total")
        disk_used = request.POST.get("disk_used")
        disk_percent = request.POST.get("disk_percent")
        net_sent = request.POST.get("net_bytes_sent")
        net_rec = request.POST.get("net_bytes_recv")
        time = request.POST.get("time")
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

    text = ""
    num = 1

    for info_ in infos:
        info_.time = info_.time + datetime.timedelta(hours=8)

        text += str(num) + " " + info_.time.strftime("%m-%d %H:%M:%S") + ' - ' + info_.ip + ' - ' + info_.cpu_num + ' - ' \
                + info_.cpu_percent + ' - ' + info_.memory_total + ' - ' + info_.memory_ava + ' - ' + info_.memory_per + \
                ' - ' + info_.disk_total + ' - ' + info_.disk_free + ' - ' + info_.net_sent + ' - ' + info_.net_rec + " <br> "
        num += 1
    return render(request, "home.html", {"text": text})
