import time

from django.shortcuts import render
from django.utils import timezone

from .data_process import *
from .send_dingtalk import send_alert_to_dingtalk

from .chart import Chart


# Create your views here.

def server(request):
    # 获取模型对象列表并陈列
    unique_license = SeverInfo.objects.values_list('license_name', flat=True).distinct()

    data = []
    for unique_name in unique_license:
        overview_data = {}
        server_info_list = SeverInfo.objects.filter(license_name=unique_name).order_by('-time')
        server_info = server_info_list.first()
        overview_data.update(name=server_info.name,
                             license_name=server_info.license_name,
                             memory=server_info.memory_percent,
                             cpu=server_info.cpu_percent,
                             disk=server_info.disk_percent,
                             joinTime=server_info.time)
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


# CPU和内存使用率折线图
def draw_lines(request):
    unique_license = SeverInfo.objects.values_list('license_name', flat=True).distinct()

    data_lines = []
    disk_percent_list = []
    for name in unique_license:
        x_time = []
        y_cpu = []
        y_memory = []
        server_info_list = SeverInfo.objects.filter(license_name=name).order_by('time')
        # print('server_info_list', server_info_list)
        disk_percent = server_info_list.values('disk_percent').last()
        for server_info in server_info_list:
            x_time.append(server_info.time)
            y_cpu.append(server_info.cpu_percent)
            y_memory.append(server_info.memory_percent)
        chart = Chart()
        value_disk = disk_percent.get("disk_percent")
        data_line = chart.lines_chart(f'{name}', f'CPU_Usage_{name}', x_time, y_cpu, y_memory, value_disk)
        data_lines.append(data_line)
        disk_percent_list.append(value_disk)
    reversed_list = disk_percent_list[::-1]
    return render(request, "ServerChart.html", {'data_lines': data_lines, 'disk_percent': reversed_list})


def systems(request):
    if request.method == 'GET':
        license_name = request.GET.get('license_name')
        infos = SeverInfo.objects.filter(license_name=license_name).order_by('-time')
        info = infos.first()

        context = {'info': info}

        return render(request, "system.html", context=context)


def home(request):
    infos = SeverInfo.objects.all().order_by('time')
    context = {'infos': infos}
    return render(request, "base.html", context=context)
