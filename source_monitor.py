import os
import time

import requests

# def merge_json_files(folder_path, file_content=None):
#     if file_content is None:
#         file_path_content = []
#     # 遍历文件夹中的所有文件和子文件夹
#     for file_name in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, file_name)
#         print('file_path', file_path)
#         # 如果是文件,合并处理
#         if os.path.isfile(file_path):
#             file_path_content.append(file_path)
#         # 如果是子文件夹,则递归
#         elif os.path.isdir(file_path):
#             merge_json_files(file_path, file_path_content)
#     return file_path_content
#


folder_path = '/home/leila/djangoProject/EyeOnServer/datas/unread'
file_list = []
files_path = []
while True:
    # 获取文件夹中的文件列表
    new_file_list = os.listdir(folder_path)

    # 检查是否又新文件出现
    new_files = [file for file in new_file_list if file not in file_list]
    if new_files:
        print('刷新文件列表')
        for file in new_files:
            files_path.append(os.path.join(folder_path, file))
        print('files_path', files_path)
        # 处理新文件
        url = 'http://192.168.199.42:8000/data/'
        requests.post(url, json=files_path)
        print("json_file:", files_path)
        files_path = []

    # 更新文件列表
    file_list = new_file_list
    # 休眠一段时间后再次检查文件夹
    time.sleep(5)
