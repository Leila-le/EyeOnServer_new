import time

from django.shortcuts import render
from django.utils import timezone

from .data_process import *
from .send_dingtalk import send_alert_to_dingtalk

from .chart import Chart


# Create your views here.

def server(request):
    # 获取模型对象列表
    overview_data = {}
    data = []
    objects = SeverInfo.objects.all()
    for item in objects.iterator():
        join_time_str = item.time.isoformat()
        overview_data.update(name=item.name,
                             license_name=item.license_name,
                             memory=item.memory_percent,
                             cpu=item.cpu_percent,
                             disk=item.disk_percent,
                             joinTime=join_time_str)
        data.append(overview_data)
    merged_data = {'code': 0, 'data': data}
    file_path = './static/merger.json'
    try:
        with open(file_path, 'w') as f:
            json.dump(merged_data, f)
    except Exception as e:
        print('json文件生成失败', e)
    return render(request, 'ServerList.html')


def draw_line(request):
    chart = Chart()
    x_time = []
    y_cpu = []
    y_memory = []
    y_disk = []
    if request.method == 'GET':
        license_name = request.GET.get('license_name')
        server_info_list = SeverInfo.objects.filter(license_name=license_name)

        for server_info in server_info_list.values_list('cpu_percent', 'time'):
            y_cpu.append(server_info[0])

            time_ = server_info[1].strftime("%Y/%m/%d %H:%M:%S")
            x_time.append(time_)
        cpu_data_line = chart.line_chart('cpu_avg', 'cpu平均使用率', x_time, y_cpu)

        for server_info in server_info_list.values_list('disk_percent', 'time'):
            y_memory.append(server_info[0])
            time_ = server_info[1].strftime("%Y/%m/%d %H:%M:%S")
        memory_data_line = chart.line_chart('memory_avg', '内存平均使用率', x_time, y_memory)

        for server_info in server_info_list.values_list('memory_percent', 'time'):
            y_disk.append(server_info[0])
            time_ = server_info[1].strftime("%Y/%m/%d %H:%M:%S")
        disk_data_line = chart.line_chart('disk_avg', '磁盘平均使用率', x_time, y_disk)

        return render(request, 'chart.html', locals())


def systems(request):
    if request.method == 'GET':
        license_name = request.GET.get('license_name')
        infos = SeverInfo.objects.filter(license_name=license_name)
        context = {'infos': infos}
        print('context: ', context)
        return render(request, "system.html", context=context)


def picture(request):
    pass


def home(request):
    infos = SeverInfo.objects.all().order_by('time')
    context = {'infos': infos}
    return render(request, "base.html", context=context)
