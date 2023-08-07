import datetime
import json
from eye_on_server.models import SeverInfo
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseForbidden
def now_time():
    time_ = str(datetime.datetime.now())
    time_ = time_.split('.')[0]
    return time_


def data_to_model(data_list):
    for data in data_list:
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
        cpu_total_idle = cpu_data('total_idle')
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
        try:  # 尝试查找数据库中是否有相同license_的记录
            SeverInfo.objects.get(license_name=license_)
        except:  # 不存在则创建一条新的记录,
            SeverInfo.objects.create(license_name=license_, time=time_, cpu_guest=cpu_guest,
                                     cpu_guest_nice=cpu_guest_nice,
                                     cpu_idle=cpu_idle, cpu_iowait=cpu_iowait, cpu_nice=cpu_nice,
                                     cpu_percent=cpu_percent,
                                     cpu_softirq=cpu_softirq, cpu_steal=cpu_steal, cpu_system=cpu_system,
                                     cpu_total_active=cpu_total_active,
                                     cpu_total_idle=cpu_total_idle, cpu_user=cpu_user, cpu_count=cpu_count,
                                     disk_free=disk_free, disk_mount_point=disk_mount_point, disk_total=disk_total,
                                     disk_used=disk_used, disk_percent=disk_percent,
                                     memory_free_physics=memory_free_physics, memory_free_swap=memory_free_swap,
                                     memory_processes=memory_processes,
                                     memory_total_physics=memory_total_physics, memory_total_swap=memory_total_swap,
                                     memory_uptime=memory_uptime,
                                     memory_used_physics=memory_used_physics, memory_used_swap=memory_used_swap,
                                     memory_ava=memory_ava,
                                     memory_percent=memory_percent,
                                     )
        else:  # ip存在,更新字段
            SeverInfo.objects.filter(license_name=license_).update(time=time_, cpu_guest=cpu_guest,
                                                                   cpu_guest_nice=cpu_guest_nice,
                                                                   cpu_idle=cpu_idle, cpu_iowait=cpu_iowait,
                                                                   cpu_nice=cpu_nice, cpu_percent=cpu_percent,
                                                                   cpu_softirq=cpu_softirq, cpu_steal=cpu_steal,
                                                                   cpu_system=cpu_system,
                                                                   cpu_total_active=cpu_total_active,
                                                                   cpu_total_idle=cpu_total_idle, cpu_user=cpu_user,
                                                                   cpu_count=cpu_count,
                                                                   disk_free=disk_free,
                                                                   disk_mount_point=disk_mount_point,
                                                                   disk_total=disk_total, disk_used=disk_used,
                                                                   disk_percent=disk_percent,
                                                                   memory_free_physics=memory_free_physics,
                                                                   memory_free_swap=memory_free_swap,
                                                                   memory_processes=memory_processes,
                                                                   memory_total_physics=memory_total_physics,
                                                                   memory_total_swap=memory_total_swap,
                                                                   memory_uptime=memory_uptime,
                                                                   memory_used_physics=memory_used_physics,
                                                                   memory_used_swap=memory_used_swap,
                                                                   memory_ava=memory_ava,
                                                                   memory_percent=memory_percent, )
    return HttpResponse("ok")


def upload_files(request):
    data_list = []  # 声明为全局变量
    if request.method == 'POST':
        files = request.FILES.getlist('files')  # 获取上传的文件列表

        for file in files:
            # 处理每个文件，例如读取内容或保存到数据库等
            file_content = file.read().decode('utf-8')  # 读取文件内容并解码为字符串
            # 处理文件内容
            # 将Json数据解析为Python对象
            json_data = json.loads(file_content)
            data_list.append(json_data)
            data_to_model(data_list)
        return render(request, 'success.html')

    return render(request, 'upload.html')
