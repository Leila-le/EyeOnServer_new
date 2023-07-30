import psutil

import time
from datetime import datetime

import requests

while True:
    # 获取CPU信息
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent()

    # 获取内存信息
    mem = psutil.virtual_memory()
    mem_total = mem.total
    mem_used = mem.used
    mem_percent = mem.percent

    # 获取磁盘信息
    disk = psutil.disk_usage('/')
    disk_total = disk.total
    disk_used = disk.used
    disk_percent = disk.percent

    # 获取网络信息
    net = psutil.net_io_counters()
    net_bytes_sent = net.bytes_sent
    net_bytes_recv = net.bytes_recv

    # 输出硬件资源信息
    print("CPU核心数：", cpu_count)
    print("CPU使用率：", cpu_percent, "%")
    print("内存总量：", round(mem_total / (1024 ** 3), 2), "GB")
    print("内存已用：", round(mem_used / (1024 ** 3), 2), "GB")
    print("内存使用率：", mem_percent, "%")
    print("磁盘总容量：", round(disk_total / (1024 ** 3), 2), "GB")
    print("磁盘已用：", round(disk_used / (1024 ** 3), 2), "GB")
    print("磁盘使用率：", disk_percent, "%")
    print("网络发送字节数：", net_bytes_sent)
    print("网络接收字节数：", net_bytes_recv)
    # 构造POST请求体
    data = {
        'cpu_count': cpu_count,
        'cpu_percent': cpu_percent,
        'men_total': mem_total,
        'mem_used': mem_used,
        'mem_percent': mem_percent,
        'disk_total': disk_total,
        'disk_used': disk_used,
        'disk_percent': disk_percent,
        'net_bytes_sent': net_bytes_sent,
        'net_bytes_recv': net_bytes_recv,
    }
    # 构造POST请求体
    # data = {'cpu_percent': cpu_percent,
    #         'mem_percent': mem_percent,
    #         'disk_percent': disk_percent,
    #         'net_io_counters': net}
    url = 'http://127.0.0.1:8001/api/'

    # 发送POST请求
    response = requests.post(url, json=data)  # headers被自动设置

    # 处理响应结果
    if response.status_code == 200:
        print('测试发送成功')
    else:
        print('测试发送失败')
    # 休眠一段时间
    time.sleep(60)
