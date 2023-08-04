import subprocess
from eye_on_server.models import SeverInfo
from .send_dingtalk import send_alert_to_dingtalk
import datetime
import threading
from django.db import transaction


def now_time():
    time_ = str(datetime.datetime.now())
    time_ = time_.split('.')[0]
    return time_


def update_ip_status(alert):
    with transaction.atomic():
        # 更新数据库状态
        for ip, status in alert.items():
            print("ip:status::::", ip, status)
            SeverInfo.objects.filter(ip=ip).update(status=status)
    # 发送钉钉消息
    # alert = {'ip ': ip, '此时: ': status}
    time_ = now_time()
    alert.update({" ": time_})
    send_alert_to_dingtalk("请注意", alert)
    alert.clear()


def ping(host):
    # 执行ping命令并解析输出
    output = subprocess.Popen(['ping', '-c', '1', host], stdout=subprocess.PIPE).communicate()[0]
    if 'ttl=' in output.decode('utf-8'):
        return True
    else:
        return False


def test_ip_status(ip_list, alert):
    # 尝试更新已知ip的当前状态及转变
    new_status = {}
    for ip_ in ip_list:
        if ping(ip_):
            new_status[ip_] = "online"
        else:
            new_status[ip_] = "offline"

    # 查询数据库中与new_status中ip相匹配的记录
    old_status = {}
    for obj in SeverInfo.objects.filter(ip__in=new_status.keys()):
        old_status[obj.ip] = obj.status
    for ip, status in new_status.items():
        if old_status.get(ip) != status:
            # 使用新线程更新状态和发送钉钉消息
            # print('ip_', old_status[ip])
            alert.update({'ip': ip, "status: ": status})
    threading.Thread(target=update_ip_status, args=(alert,)).start()
