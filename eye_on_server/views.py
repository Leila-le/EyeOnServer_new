import socket

from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import SeverInfo
import json
import datetime
from dingtalkchatbot.chatbot import DingtalkChatbot


# Create your views here.
def send_alert_to_dingtalk(data_str, alerts):
    # 尝试发送警告消息给钉钉
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=403401f4b0ee81a7ea4b3355b85327bb71cfb33ef2f9ff6ce1db6e82e182af56'
    secret = 'SECda9044fc2385908cadb9d84940c244d4070d6b647788dc29bea29459851de67e'

    for key, value in alerts.items():
        print("key,value:", key, value)
        # 将内容转为字符串:
        data_str += key + str(value) + '\n'

    xiao_ding = DingtalkChatbot(webhook, secret=secret)
    try:
        xiao_ding.send_text(msg=data_str, is_at_all=False)
        print('钉钉消息发送成功')
    except:
        print("钉钉消息发送失败")


def test_ip_status(ip_list):
    # 尝试更新已知ip的当前状态及转变
    new_status = {}
    for ip_ in ip_list:
        try:
            socket.create_connection((ip_, 80), timeout=1)
            new_status[ip_] = "online"
        except(socket.timeout, ConnectionError):
            new_status[ip_] = "offline"

    # 查询数据库中与new_status中ip相匹配的记录
    old_status = {}
    for obj in SeverInfo.objects.filter(ip__in=new_status.keys()):
        old_status[obj.ip] = obj.status

    for ip, status in new_status.items():
        if old_status.get(ip) != status:
            alert = {'ip ': ip, '此时: ': status}
            send_alert_to_dingtalk("请注意", alert)
            time_ = datetime.datetime.now()
            alert.update({" ": time_})
            # 更新数据库状态:
            SeverInfo.objects.filter(ip=ip).update(status=status)


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
            status = data.get('status')

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            # error_message = str(e)
            cpu_count = '-1'
            cpu_percent = '-1'
            memory_total = '-1'
            mem_used = '-1'
            memory_per = '-1'
            disk_total = '-1'
            disk_used = '-1'
            disk_percent = '-1'
            net_sent = '-1'
            net_rec = '-1'
            status = 'offline'

            # time = timezone.now() + datetime.timedelta(hours=8)
        time = timezone.now()  # + datetime.timedelta(hours=8)
        alerts = {'ip: ': ip}
        if cpu_percent > 5:
            alerts.update({"cpu已使用: ": cpu_percent})
            # send_alert_to_dingtalk(ip, {"cpu已使用:": cpu_percent})
        if memory_per > 90:
            alerts.update({"内存已使用: ": memory_per})
            # send_alert_to_dingtalk(ip, {"内存已使用:": memory_per})
        if disk_percent > 80:
            alerts.update({"磁盘已使用: ": disk_percent})
            # send_alert_to_dingtalk(ip, {"磁盘已使用:": disk_percent})

        time_ = str(time + datetime.timedelta(hours=8))
        time_ = time_.split('.')[0]
        alerts.update({" ": time_})
        if len(alerts) >= 3:
            send_alert_to_dingtalk("资源使用超过预警:\n", alerts)
        # 使用同步方式保存服务器信息
        try:  # 尝试查找数据库中是否有相同ip地址的记录
            SeverInfo.objects.get(ip=ip)
        except:  # 不存在则创建一条新的记录,
            SeverInfo.objects.create(ip=ip, time=time, cpu_count=cpu_count, cpu_percent=cpu_percent,
                                     memory_total=memory_total, mem_used=mem_used, memory_per=memory_per,
                                     disk_total=disk_total, disk_used=disk_used, disk_percent=disk_percent,
                                     net_sent=net_sent, net_rec=net_rec, status=status)
        else:  # ip存在,更新字段
            SeverInfo.objects.filter(ip=ip).update(time=time, cpu_count=cpu_count, cpu_percent=cpu_percent,
                                                   memory_total=memory_total, mem_used=mem_used, memory_per=memory_per,
                                                   disk_total=disk_total, disk_used=disk_used,
                                                   disk_percent=disk_percent,
                                                   net_sent=net_sent, net_rec=net_rec, status=status)

    return HttpResponse("ok")


def home(request):
    ip_list = SeverInfo.objects.values_list('ip', flat=True)
    test_ip_status(ip_list)

    infos = SeverInfo.objects.all().order_by('time')
    context = {'infos': infos}
    return render(request, "home.html", context=context)
