import logging
import threading
import time
import datetime

from dingtalkchatbot.chatbot import DingtalkChatbot
from django.db.models import Q
from django.utils import timezone

from eye_on_server.models import SeverInfo


webhook = 'https://oapi.dingtalk.com/robot/send?access_token' \
          '=403401f4b0ee81a7ea4b3355b85327bb71cfb33ef2f9ff6ce1db6e82e182af56'
secret = 'SECda9044fc2385908cadb9d84940c244d4070d6b647788dc29bea29459851de67e'
xiao_ding = DingtalkChatbot(webhook, secret=secret)  # 创建钉钉机器人实例
alerts_list = []  # 存储警告消息的列表
last_sent_time = 0  # 上次发送警告消息的时间戳
alerts_str = ""  # 警告消息的字符串形式
timer = None  # 定时器对象,用于定时发送警告消息


def send_alert_to_dingtalk():
    """
    发送警告消息给钉钉    :return: None
    """
    global last_sent_time, alerts_str
    current_time = time.time()  # 获取当前时间戳
    # 尝试发送警告消息给钉钉
    i = 1
    while i < len(alerts_list):

        system_license_previous = alerts_list[i - 1].split("\n")[:2]
        system_license_new = alerts_list[i].split("\n")[:2]

        if system_license_previous == system_license_new:
            alerts_list[i - 1] = alerts_list[i]
            alerts_list.remove(alerts_list[i])
            last_sent_time = current_time
        else:
            i += 1
    for alert in alerts_list:
        alerts_str += alert

    try:
        xiao_ding.send_text(msg=alerts_str, is_at_all=False)  # 发送警告消息
        logging.info('钉钉消息发送成功')

    except Exception as e:
        logging.info("钉钉消息发送失败: %s", e)
    last_sent_time = current_time
    alerts_str = ""
    alerts_list.clear()


def process_message(message):
    """
    处理受到的消息,并根据一定条件触发发送警告消息给钉钉
    :param message: 收到的消息
    :return: None
    """
    global last_sent_time, alerts_list, timer

    # 将消息添加至列表
    alerts_list.append(message)
    current_time = time.time()  # 获取当前时间戳
    # 检查时间间隔是否超过5秒
    if current_time - last_sent_time >= 5 or len(alerts_list) >= 10:
        if timer is not None and timer.is_alive():
            timer.cancel()  # 如果定时器正在运行,则取消重置定时器
            send_alert_to_dingtalk()  # 手动调用发送函数
        else:
            send_alert_to_dingtalk()  # 直接调用发送函数
        # 启动新的定时器，5 秒后执行处理函数
        timer = threading.Timer(5, send_alert_to_dingtalk)
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
            loadavg_five = []
            loadavg_fif = []
            # 查询服务器信息
            server_info_list = SeverInfo.objects.filter(license_name=unique_license_name, name=unique_name).order_by(
                'time')
            current_time = datetime.datetime.now()
            five_minutes_ago = current_time - datetime.timedelta(minutes=5)
            five_minutes_ago = five_minutes_ago.replace(second=0, microsecond=0)
            fifteen_minutes_ago = current_time - datetime.timedelta(minutes=15)
            fifteen_minutes_ago = fifteen_minutes_ago.replace(second=0, microsecond=0)
            # 执行查询，获取在5分钟前的那一分钟中创建的数据库信息
            results_five = server_info_list.filter(Q(time__gte=five_minutes_ago))
            results_fifteen = server_info_list.filter(Q(time__gte=fifteen_minutes_ago))
            # 遍历results_five并获取每个对象的loadavg属性
            for result in results_five:
                loadavg_five = result.loadavg
            for result in results_fifteen:
                loadavg_fif = result.loadavg
            for info in server_info_list:
                base_info = f"""> 您的云服务器已运行-{info.uptime}，
                        <br>机器负载情况为(最近1、5、15分钟)：{info.loadavg, loadavg_five[0], loadavg_fif[0]},
                        <br>- 目前CPU使用率为：{info.percent}%，
                        <br>- 系统运行内存使用率为：{info.memory_percent}%，
                        <br>- 剩余可用运行内存为：{float(info.free_physics) / (1024 * 1024 * 1024)}GiB，
                        <br>- 系统存储内存使用率为：{info.disk_percent}%，
                        <br>- 剩余可用存储内存为：{float(info.free) / (1024 * 1024 * 1024)}GiB,
                        <br>**{'机器CPU使用率正常' if float(info.percent) <= 80 else '机器CPU使用率过高，可能触发预警'}**
                        <br>**{'机器内存使用率正常' if float(info.memory_percent) <= 80 else '机器CPU使用率过高，可能触发预警'}**
                        <br>**{'机器磁盘使用率正常' if float(info.disk_percent) <= 80 else '机器CPU使用率过高，可能触发预警'}**
                        """
                return base_info


def send_alert_am9(message):
    """
    获取当前时间,构建要发送的消息
    :param message: 服务器基础信息的消息内容
    :return: None
    """
    # 获取当前时间
    current_time = datetime.datetime.now().time()
    print(current_time)
    # 检查是否在9点以后
    if current_time >= datetime.time(9, 0, 0):
        # 构建要发送的消息
        xiao_ding.send_markdown("服务器基础信息", message)


def schedule_send_alert_am9():
    """
    设置明天9点执行发送消息的定时器
    :return: None
    """
    # 设置明天9点执行发送消息的定时器
    next_run_time = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1),
                                              datetime.time(9, 0, 0))
    time_delta = next_run_time - datetime.datetime.now()
    seconds_until_next_run = time_delta.total_seconds()
    # 启动定时器，在明天的9点执行send_alert_am9函数
    timer_ = threading.Timer(seconds_until_next_run, send_alert_am9, args=get_message())
    timer_.start()

    # 取消定时器，避免重复执行send_alert_am9函数
    timer_.cancel()
