# 用于将json数据传输至数据库
import datetime
import json
import os

from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from eye_on_server.models import SeverInfo


def now_time():
    naive_datetime = str(datetime.datetime.now())
    naive_datetime = naive_datetime.split('.')[0]
    return naive_datetime


json_folder = '/home/leila/djangoProject/EyeOnServer/datas'
merged_data = {}


def merge_json_files(folder_path):
    # 遍历文件夹中的所有文件和子文件夹
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # 如果是文件,合并处理
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                file_content = f.read()
                data = json.loads(file_content)
                merged_data.update(data)
        # 如果是子文件夹,则递归
        elif os.path.isdir(file_path):
            merge_json_files(file_path)



@csrf_exempt
def data_to_model(request):
    if request.method == 'POST':
        merge_json_files(json_folder)
        print('merged:', merged_data)
        try:
            files_path = './static/merger.json'
            with open(files_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f)
                print('JSON文件合并完成.')
        except Exception as e:
            print('合并失败:',e)
        else:
            with open(files_path, 'r') as file:
                file_content_str = file.read()
                data = json.loads(file_content_str)
                name = data.get('name')
                license_ = data.get('license_name')
                # cpu使用情况
                cpu_data = data.get('cpu', {})
                cpu_guest = cpu_data.get('guest')
                cpu_guest_nice = cpu_data.get('guest_nice')
                cpu_idle = cpu_data.get('idle')
                cpu_iowait = cpu_data.get('iowait')
                cpu_nice = cpu_data.get('nice')
                cpu_percent = cpu_data.get('percent')
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
                disk_percent = disk_used / disk_total
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
                memory_percent = memory_used_physics / memory_total_physics
                time_ = now_time()
                SeverInfo.objects.create(name=name, license_name=license_, time=time_, cpu_guest=cpu_guest,
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
                                         )

        return HttpResponse("ok")
