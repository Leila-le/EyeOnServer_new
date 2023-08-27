from django.contrib.auth.views import LoginView
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse

from .data_process import *
from .chart import Chart
from django.contrib import messages

# from ..models import User


# from models import User

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


# 会员登录表单
def login(request):
    return render(request, 'myadmin/index/login.html')


# 会员执行登录
# def dologin(request):
#     '''执行登录'''
#     try:
#         # 根据登录账号获取用户信息
#         user = User.objects.get(username=request.POST['username'])
#         # 校验当前用户状态是否是管理员
#         if user.status == 6:
#             # 获取密码并md5
#             import hashlib
#             md5 = hashlib.md5()
#             n = user.password_salt
#             s = request.POST['pass'] + str(n)
#             md5.update(s.encode('utf-8'))
#             # 校验密码是否正确
#             if user.password_hash == md5.hexdigest():
#                 # 将当前登录成功用户信息以adminuser这个key放入到session中
#                 request.session['adminuser'] = user.toDict()
#                 return redirect(reverse('myadmin_index'))
#             else:
#                 context = {"info": "登录密码错误！"}
#         else:
#             context = {"info": "此用户非后台管理账号！"}
#     except Exception as err:
#         print(err)
#         context = {"info": "登录账号不存在！"}
#     return render(request, "myadmin/index/login.html", context)
#
#
# # 会员退出
# def logout(request):
#     """执行退出"""
#     del request.session['adminuser']
#     return redirect(reverse('myadmin_login'))


# def verify(request):
#     # 引入随机函数模块
#     import random
#     from PIL import Image, ImageDraw, ImageFont
#     # 定义变量，用于画面的背景色、宽、高
#     # bgcolor = (random.randrange(20, 100), random.randrange(
#     #    20, 100),100)
#     bgcolor = (242, 164, 247)
#     width = 100
#     height = 25
#     # 创建画面对象
#     im = Image.new('RGB', (width, height), bgcolor)
#     # 创建画笔对象
#     draw = ImageDraw.Draw(im)
#     # 调用画笔的point()函数绘制噪点
#     for i in range(0, 100):
#         xy = (random.randrange(0, width), random.randrange(0, height))
#         fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
#         draw.point(xy, fill=fill)
#     # 定义验证码的备选值
#     # str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
#     str1 = '0123456789'
#     # 随机选取4个值作为验证码
#     rand_str = ''
#     for i in range(0, 4):
#         rand_str += str1[random.randrange(0, len(str1))]
#     # 构造字体对象，ubuntu的字体路径为“/usr/share/fonts/truetype/freefont”
#     font = ImageFont.truetype('static/arial.ttf', 21)
#     # font = ImageFont.load_default().font
#     # 构造字体颜色
#     fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
#     # 绘制4个字
#     draw.text((5, -3), rand_str[0], font=font, fill=fontcolor)
#     draw.text((25, -3), rand_str[1], font=font, fill=fontcolor)
#     draw.text((50, -3), rand_str[2], font=font, fill=fontcolor)
#     draw.text((75, -3), rand_str[3], font=font, fill=fontcolor)
#     # 释放画笔
#     del draw
#     # 存入session，用于做进一步验证
#     request.session['verifycode'] = rand_str
#     """
#     python2的为
#     # 内存文件操作
#     import cStringIO
#     buf = cStringIO.StringIO()
#     """
#     # 内存文件操作-->此方法为python3的
#     import io
#     buf = io.BytesIO()
#     # 将图片保存在内存中，文件类型为png
#     im.save(buf, 'png')
#     # 将内存中的图片数据返回给客户端，MIME类型为图片png
#     return HttpResponse(buf.getvalue(), 'image/png')
