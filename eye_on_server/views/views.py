from django.contrib.auth.views import LoginView
from django.shortcuts import render

from .data_process import *
from .chart import Chart


# Create your views here.

def server(request):
    data = []
    unique_license = SeverInfo.objects.values_list('license_name', flat=True).distinct()
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


def get_unique_license():
    unique_license = SeverInfo.objects.values_list('license_name', flat=True).distinct()
    unique_name = SeverInfo.objects.values_list('name', flat=True).distinct()
    unique_license_list = list(unique_license)
    unique_license_json = json.dumps(unique_license_list)
    return unique_license, unique_license_json, unique_name


def get_draw_line(unique_license, unique_name):
    data_lines = []
    disk_percent_list = []
    for name in unique_license:
        for name01 in unique_name:
            if SeverInfo.objects.filter(license_name=name, name=name01).exists():

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
                data_line = chart.lines_chart(f'{name}_{name01}', f'CPU_Usage_{name}_{name01}', x_time, y_cpu, y_memory,
                                              value_disk)
                data_lines.append(data_line)
                disk_percent_list.append(value_disk)
    reversed_list = disk_percent_list[::-1]
    return data_lines, reversed_list


# CPU和内存使用率折线图
def draw_lines(request):
    unique_license, unique_license_json, unique_name = get_unique_license()
    # 获取模型对象列表并陈列
    data_lines, reversed_list = get_draw_line(unique_license, unique_name)

    return render(request, "ServerChart.html",
                  {"data_lines": data_lines, "disk_percent": reversed_list, "unique_license_json": unique_license_json})


def search(request):
    if request.method == 'GET':
        search_list = []
        search_value = request.GET.get('keywords', "").strip()
        # print('search_value', search_value)
        search_list.append(search_value)
        _, unique_license_json, search_name = get_unique_license()
        result = SeverInfo.objects.filter(license_name=search_value).exists()
        if result:
            data_lines, reversed_list = get_draw_line(search_list, search_name)
            return render(request, "ServerChart.html", {"data_lines": data_lines, "disk_percent": reversed_list,
                                                        "unique_license_json": unique_license_json})
        # return render(request, "ServerChart.html", {"result": result, "unique_license_json": unique_license_json})
    # 处理非GET请求的情况，例如POST请求
    # return HttpResponseBadRequest("Invalid request method")


def home(request):
    _, unique_license_json, _ = get_unique_license()
    infos = SeverInfo.objects.all().order_by('-time')
    context = {'infos': infos}
    return render(request, "base.html", locals())


class CustomLoginView(LoginView):
    template_name = 'admin/login.html'  # 替换为你自己的登录模板路径
    redirect_authenticated_user = True
    redirect_field_name = 'next'


def systems(request):
    if request.method == 'GET':
        license_name = request.GET.get('license_name')
        infos = SeverInfo.objects.filter(license_name=license_name).order_by('-time')
        info = infos.first()
        context = {'info': info}
        return render(request, "system.html", context=context)

# # 会员登录表单
# def login(request):
#     return render(request, 'myadmin/index/login.html')
