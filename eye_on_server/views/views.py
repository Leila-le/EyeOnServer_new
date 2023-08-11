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


# def cpu_percent_line(request, data):
#     chart = Chart()
#     cpu_data_line = chart.line_chart('cpu_avg', 'cpu平均使用率', timezone.now(), SeverInfo.cpu_percent)
#     print('cpu_data_line', cpu_data_line)
#     return render(request, 'monitor/cpu_m.html', locals())
#
#
# def disk_percent_line(request, data):
#     chart = Chart()
#     disk_data_line = chart.line_chart('disk_avg', 'cpu平均使用率', timezone.now(), SeverInfo.disk_percent)
#
#     return render(request, 'monitor/disk_m.html', locals())
#
#
# def memory_percent_line(request, data):
#     chart = Chart()
#     memory_data_line = chart.line_chart('memory_avg', 'cpu平均使用率', timezone.now(), SeverInfo.memory_percent)
#
#     return render(request, 'monitor/memory_m.html', locals())

def draw_line(request):
    chart = Chart()
    x_data=[]
    y_data = []
    server_info_list = SeverInfo.objects.filter(license_name='泉州熊猫科技有限公司')
    for server_info in server_info_list.values_list('cpu_percent', 'time'):
        x_data.append(server_info[0])
        y_data.append(server_info[1])

    cpu_data_line = chart.line_chart('cpu_avg', 'cpu平均使用率', x_data, y_data)

    for server_info in server_info_list.values_list('disk_percent', 'time'):
        x_data_d = server_info[0]
        y_data_d = server_info[1]
        disk_data_line = chart.line_chart('disk_avg', '磁盘平均使用率', x_data_d, y_data_d)

    for server_info in server_info_list.values_list('memory_percent', 'time'):
        x_data_m = server_info[0]
        y_data_m = server_info[1]
        memory_data_line = chart.line_chart('memory_avg', '内存平均使用率', x_data_m, y_data_m)
    return render(request, 'monitor/cpu_m.html', locals()), render(request, 'monitor/disk_m.html', locals()), \
        render(request, 'monitor/memory_m.html', locals())


def home(request):
    infos = SeverInfo.objects.all().order_by('time')
    context = {'infos': infos}
    return render(request, "base.html", context=context)
