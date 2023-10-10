import logging
import threading
import time
from dingtalkchatbot.chatbot import DingtalkChatbot
from django.core.cache import cache
from eye_on_server.models import SeverInfo

webhook = 'https://oapi.dingtalk.com/robot/send?access_token' \
          '=403401f4b0ee81a7ea4b3355b85327bb71cfb33ef2f9ff6ce1db6e82e182af56'
secret = 'SECda9044fc2385908cadb9d84940c244d4070d6b647788dc29bea29459851de67e'
xiao_ding = DingtalkChatbot(webhook, secret=secret)  # 创建钉钉机器人实例
alerts_list = []  # 存储警告消息的列表
last_sent_time = 0  # 上次发送警告消息的时间戳
alerts_str = ""  # 警告消息的字符串形式
timer = None  # 定时器对象,用于定时发送警告消息
timer_ = None  # 定时器对象，用于每日定时发送简报消息


def get_warning(keys):
    messages = []
    for key in keys:
        name = key.split('-')[0]
        license_name = key.split('-')[1]
        target = key.split('-')[2]
        message = f"系统: {name}\n许可:{license_name}\n" \
                  f"{target}最高超阈值使用率: {cache.get(key)}%\n"
        print("message", message)
        messages.append(message)
    # 将当前收集到的超过阈值的内容传至send_alert_to_dingtalk进行发送钉钉消息准备
    if messages:
        return "\n".join(messages)


def send_alert_to_dingtalk():
    """
    发送警告消息给钉钉    :return: None
    """
    global last_sent_time, alerts_str
    current_time = time.time()  # 获取当前时间戳
    # 尝试发送警告消息给钉钉
    i = 1
    new_alerts_list = []
    while i < len(alerts_list):
        if alerts_list[i - 1] is None or alerts_list[i] is None:
            i += 1
            continue

        system_license_previous = alerts_list[i - 1].split("\n")[:2]
        system_license_new = alerts_list[i].split("\n")[:2]

        if system_license_previous == system_license_new:
            # alerts_list[i - 1] = alerts_list[i]
            # alerts_list.remove(alerts_list[i])
            i += 1
            last_sent_time = current_time
            continue
        else:
            new_alerts_list.append(alerts_list[i - 1])
            i += 1
    for alert in alerts_list:
        if isinstance(alert, str):
            alerts_str += alert
        else:
            alerts_str += str(alert)

    try:
        xiao_ding.send_text(msg=alerts_str, is_at_all=False)  # 发送警告消息
        logging.info('钉钉消息发送成功')

    except Exception as e:
        logging.info("钉钉消息发送失败: %s", e)
    last_sent_time = current_time
    alerts_str = "".join(new_alerts_list)
    alerts_list.clear()


def process_message(keys):
    """
    处理受到的消息,并根据一定条件触发发送警告消息给钉钉
    :return: None
    """

    global last_sent_time, alerts_list, timer
    if timer is not None and timer.is_alive():
        return
    message = get_warning(keys)

    alerts_list.append(message)  # 将消息添加至列表

    current_time = time.time()  # 获取当前时间戳
    # 检查时间间隔是否超过30秒
    if current_time - last_sent_time >= 30:
        if timer is not None and timer.is_alive():
            timer.cancel()  # 如果定时器正在运行,则取消重置定时器
            send_alert_to_dingtalk()  # 手动调用发送函数
        else:
            send_alert_to_dingtalk()  # 直接调用发送函数

        last_sent_time = time.time()
        alerts_list = []
    # 启动新的定时器，30 秒后执行处理函数(不受执行时间影响）
    timer = threading.Timer(30 - (time.time() - last_sent_time), send_alert_to_dingtalk)
    timer.start()


def get_message():
    """
    获取服务器基础信息的消息内容
    :return:服务器基础信息的消息内容
    """
    # 从SeverInfo中获取唯一的许可名称
    unique_license_names = SeverInfo.objects.values_list('license_name', flat=True).distinct()
    # 从SeverInfo中获取唯一的服务器名称
    unique_names = SeverInfo.objects.values_list('name', flat=True).distinct()
    # 遍历唯一的许可证名称和服务器名称
    for unique_license_name in unique_license_names:
        for unique_name in unique_names:
            # 查询服务器信息
            server_info_list = SeverInfo.objects.filter(license_name=unique_license_name,
                                                        name=unique_name).order_by('time')
            # 遍历results_five并获取每个对象的loadavg属性
            for info in server_info_list:
                base_info = f"""> 您的云服务器已运行-{info.uptime}，
                        <br>- 目前CPU使用率为：{info.percent}%，
                        <br>- 系统运行内存使用率为：{info.memory_percent}%，
                        <br>- 剩余可用运行内存为：{float(info.free_physics) / (1024 * 1024 * 1024)}GiB，
                        <br>- 系统存储内存使用率为：{info.disk_percent}%，
                        <br>- 剩余可用存储内存为：{float(info.free) / (1024 * 1024 * 1024)}GiB,
                        <br>**{'机器CPU使用率正常' if float(info.percent) <= 80 else '机器CPU使用率过高，可能触发预警'}**
                        <br>**{'机器内存使用率正常' if float(info.memory_percent) <= 80 else '机器内存使用率过高，可能触发预警'}**
                        <br>**{'机器磁盘使用率正常' if float(info.disk_percent) <= 80 else '机器磁盘使用率过高，可能触发预警'}**
                        """
                return base_info
