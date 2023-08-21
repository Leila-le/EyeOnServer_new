# 用于将json数据传输至数据库
import datetime
import os
import json
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from eye_on_server.models import SeverInfo
from eye_on_server.views.send_dingtalk import send_alert_to_dingtalk
import shutil

json_folder = '/home/leila/djangoProject/EyeOnServer/datas'


# 存放未存入数据库的json文件路径


@csrf_exempt
def data_to_model(request):
    if request.method == 'POST':
        target_file = '/home/leila/djangoProject/EyeOnServer/datas/read'
        datas = []
        # file_path_content = merge_json_files(json_folder)
        file_path_content = json.loads(request.body)
        # 在data字典中获取files_path的值
        print("file_path_content", file_path_content)
        if file_path_content:
            for file_path in file_path_content:
                merged_data = {}
                with open(file_path) as f:
                    merged_data.update(eval(f.read()))

                    time_ = os.path.getctime(file_path)
                    time_datetime = datetime.datetime.fromtimestamp(time_)
                    time_str = time_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    merged_data.update({'time': time_str})
                shutil.move(file_path, target_file)
                datas.append(merged_data)
        # 将数据存入数据表中
        for data in datas:
            name = data.get('name')
            license_ = data.get('license_name')

            # cpu使用情况
            cpu_data = data.get('cpu', {})
            cpu_guest = cpu_data.get('guest')
            cpu_guest_nice = cpu_data.get('guest_nice')
            cpu_idle = cpu_data.get('idle')
            cpu_iowait = cpu_data.get('iowait')
            cpu_nice = cpu_data.get('nice')
            cpu_percent = cpu_data.get('percent') * 100
            cpu_softirq = cpu_data.get('softirq')
            cpu_steal = cpu_data.get('steal')
            cpu_system = cpu_data.get('system')
            cpu_total_active = cpu_data.get('total_active')
            cpu_total_idle = cpu_data.get('total_idle')
            cpu_user = cpu_data.get('user')
            cpu_count = cpu_data.get('count')
            # 磁盘使用情况
            disk_data = data.get('disk', {})
            disk_free = disk_data.get('free')
            disk_mount_point = disk_data.get('mount_point')
            disk_total = disk_data.get('total')
            disk_used = disk_data.get('used')
            disk_percent = disk_used / disk_total * 100
            # 内存使用情况
            memory_data = data.get('memory', {})
            memory_free_physics = memory_data.get('free_physics')
            memory_free_swap = memory_data.get('free_swap')
            memory_processes = memory_data.get('processes')
            memory_total_physics = memory_data.get('total_physics')
            memory_total_swap = memory_data.get('total_swap')
            memory_uptime = memory_data.get('uptime')
            memory_used_physics = memory_data.get('used_physics')
            memory_used_swap = memory_data.get('used_swap')
            memory_ava = memory_total_physics - memory_used_physics
            memory_percent = memory_used_physics / memory_total_physics * 100
            memory_swap_percent = memory_used_swap / memory_total_swap * 100
            time_ = data.get('time')
            alerts = {'name: ': name, "license_name: ": license_}
            send_alert = False
            if cpu_percent > 70:
                alerts.update({"当前cpu使用率: ": cpu_percent})
                send_alert = True
                # send_alert_to_dingtalk(ip, {"cpu已使用:": cpu_percent})
            if memory_percent > 80:
                alerts.update({"当前内存使用率: ": memory_percent})
                send_alert = True
                # send_alert_to_dingtalk(ip, {"内存已使用:": memory_per})
            if disk_percent > 80:
                alerts.update({"当前磁盘使用率: ": disk_percent})
                send_alert = True
                # send_alert_to_dingtalk(ip, {"磁盘已使用:": disk_percent})
            alerts.update({" ": time_})
            if send_alert:
                send_alert_to_dingtalk("资源使用预警:\n", alerts)
            SeverInfo.objects.create(name=name, license_name=license_, cpu_guest=cpu_guest,
                                     cpu_guest_nice=cpu_guest_nice,
                                     cpu_idle=cpu_idle, cpu_iowait=cpu_iowait, cpu_nice=cpu_nice,
                                     cpu_percent=cpu_percent,
                                     cpu_softirq=cpu_softirq, cpu_steal=cpu_steal, cpu_system=cpu_system,
                                     cpu_total_active=cpu_total_active,
                                     cpu_total_idle=cpu_total_idle, cpu_user=cpu_user, cpu_count=cpu_count,
                                     disk_free=disk_free, disk_mount_point=disk_mount_point,
                                     disk_total=disk_total,
                                     disk_used=disk_used, disk_percent=disk_percent,
                                     memory_free_physics=memory_free_physics, memory_free_swap=memory_free_swap,
                                     memory_processes=memory_processes,
                                     memory_total_physics=memory_total_physics,
                                     memory_total_swap=memory_total_swap,
                                     memory_uptime=memory_uptime,
                                     memory_used_physics=memory_used_physics, memory_used_swap=memory_used_swap,
                                     memory_ava=memory_ava,
                                     memory_percent=memory_percent,
                                     memory_swap_percent=memory_swap_percent,
                                     time=time_,
                                     )
        return HttpResponse("ok")
