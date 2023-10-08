import os
import time

import requests

folder_path = './datas/unread'
file_list = []
files_path = []
while True:
    # # 获取文件夹中的文件列表
    # new_file_list = os.listdir(folder_path)
    #
    # # 检查是否又新文件出现
    # new_files = [file for file in new_file_list if file not in file_list]
    # if new_files:
    #     print('刷新文件列表')
    #     for file in new_files:
    #         files_path.append(os.path.join(folder_path, file))
    #     print('files_path', files_path)
    #     # 处理新文件
    #     url = 'http://192.168.199.42:8000/data/'
    #     requests.post(url, json=files_path)
    #     print("json_file:", files_path)
    #     files_path = []
    #
    # # 更新文件列表
    # file_list = new_file_list

    # 处理新文件
    with open('media/json/shortman01.json', 'r') as f:
        data = eval(f.read())
    # url = 'http://192.168.199.42:8000/data/'
    url = 'http://110.43.54.174:8001/shortman/'
    requests.post(url, json=data)
    print('type-data', type(data))
    print("data:", data)
    # 休眠一段时间后再次检查文件夹
    time.sleep(2)
