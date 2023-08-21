from django.contrib.auth.views import LoginView
from django.shortcuts import render
from .data_process import *
from .chart import Chart


# Create your views here.
# unique_license = SeverInfo.objects.values_list('license_name', flat=True).distinct()


def server(request):
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
    unique_license = SeverInfo.objects.values_list('license_name', flat=True).distinct()
    # 获取模型对象列表并陈列
    unique_license_list = list(unique_license)
    return render(request, "base.html", {'unique_license_list': unique_license_list})


class CustomLoginView(LoginView):
    template_name = 'admin/login.html'  # 替换为你自己的登录模板路径
    redirect_authenticated_user = True
    redirect_field_name = 'next'
