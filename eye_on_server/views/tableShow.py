# 用于将数据表中的数据转为json格式,传至对应的html页面中的table中
import json

from django.shortcuts import render

from eye_on_server.models import SeverInfo


def data_to_json(request, url, file_path):
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

    # file_path = './static/merger.json'
    try:
        with open(file_path, 'w') as f:
            json.dump(merged_data, f)
    except Exception as e:
        print('json文件生成失败', e)
    return render(request, url)
