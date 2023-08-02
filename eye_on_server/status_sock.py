import socket
from .models import SeverInfo

# 服务器配置
SERVER_IP = '0.0.0.0'  # 监听所有ip地址
SERVER_PORT = 8888  # 监听端口号


def status_now(status):
    # 创建TCP监听器
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen(1)

    while True:
        # 监听客户端状态
        try:
            # 接收客户端连接请求
            conn, addr = sock.accept()
            print('New client:', addr)
            # 接收客户端心跳消息
            data = conn.recv(1024)
            if data == b'heartbeat':
                # 更新客户端状态为在线
                print('Clinet is online:', addr)
                status = 'online'
            else:
                # 心跳消息无效,关闭连接
                print('Invalid heartbeat', data)
            conn.close()
        except Exception as e:
            status = 'offline'
            print('ERROR:', e)
            break

    status = 'offline'

