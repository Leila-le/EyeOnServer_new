import logging
import threading
import time
import datetime

from dingtalkchatbot.chatbot import DingtalkChatbot
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
timer_ = None  # 定时器对象，用于每日定时发送简报消息


def get_warning():
    # 从SeverInfo中获取唯一的许可名称
    current = timezone.now()
    start_time = current - datetime.timedelta(seconds=30)

    data_list = SeverInfo.objects.filter(time__range=(start_time, current))
    licenses = data_list.values_list('license_name', flat=True).distinct()
    names = data_list.values_list('name', flat=True).distinct()

    # 设置阈值，用于比较
    cpu_threshold = 80
    memory_threshold = 80
    disk_threshold = 80
    # 初始化消息列表和标志变量
    messages = []
    for license_name in licenses:
        for name in names:
            # 得到这段时间内cpu、内存、磁盘的最高使用率
            info = data_list.filter(license_name=license_name, name=name)
            cpu_percent_max = info.order_by('percent').values('percent').last()['percent']
            memory_percent_max = info.order_by('memory_percent').values('memory_percent').last()['memory_percent']
            disk_percent_max = info.order_by('disk_percent').values('disk_percent').last()['disk_percent']
            # 检查CPU使用率是否超过阈值
            if float(cpu_percent_max) > cpu_threshold:
                cpu_time = info.order_by('percent').values('time').last()['time']
                cpu_time_local = cpu_time.astimezone(timezone.get_current_timezone())
                cpu_time_formatted = cpu_time_local.strftime("%Y-%m-%d %H:%M:%S")
                message = f"系统: {name}\n许可:{license_name}\n时间:{cpu_time_formatted}\n" \
                          f"cpu最高超阈值使用率: {cpu_percent_max}%"
                messages.append(message)
            # 检查内存使用率是否超过阈值
            if float(memory_percent_max) > memory_threshold:
                memory_time = info.order_by('memory_percent').values('time').last()['time']
                memory_time_local = memory_time.astimezone(timezone.get_current_timezone())
                memory_time_formatted = memory_time_local.strftime("%Y-%m-%d %H:%M:%S")
                message = f"系统: {name}\n许可:{license_name}\n时间:{memory_time_formatted}\n" \
                          f"内存最高超阈值使用率: {memory_percent_max}%"
                messages.append(message)
                flag = True
            # 检查磁盘使用率是否超过阈值
            if float(disk_percent_max) > disk_threshold:
                disk_time = info.order_by('disk_percent').values('time').last()['time']
                disk_time_local = disk_time.astimezone(timezone.get_current_timezone())
                disk_time_formatted = disk_time_local.strftime("%Y-%m-%d %H:%M:%S")
                message = f"系统: {name}\n许可:{license_name}\n时间:{disk_time_formatted}\n" \
                          f"磁盘最高超阈值使用率: {disk_percent_max}%"
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


def process_message():
    """
    处理受到的消息,并根据一定条件触发发送警告消息给钉钉
    :return: None
    """

    global last_sent_time, alerts_list, timer
    if timer is not None and timer.is_alive():
        return
    message = get_warning()
    alerts_list.append(message)  # 将消息添加至列表

    current_time = time.time()  # 获取当前时间戳
    # 检查时间间隔是否超过30秒
    if current_time - last_sent_time >= 30 or len(alerts_list) >= 10:
        if timer is not None and timer.is_alive():
            timer.cancel()  # 如果定时器正在运行,则取消重置定时器
            send_alert_to_dingtalk()  # 手动调用发送函数
        else:
            send_alert_to_dingtalk()  # 直接调用发送函数

        last_sent_time = time.time()
        alerts_list = []
    # 启动新的定时器，30 秒后执行处理函数(不受执行时间影响）
    timer = threading.Timer(30- (time.time() - last_sent_time), send_alert_to_dingtalk)
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


def send_alert_am9():
    """
    获取当前时间,构建要发送的消息
    :return: None
    """
    message = get_message()
    xiao_ding.send_markdown("服务器基础信息", message)


def schedule_send_alert_am9():
    """
    设置每天9点执行发送消息的定时器
    :return: None
    """
    global timer_
    if timer_ is not None and timer_.is_alive():
        return

    now = datetime.datetime.now()  # 获取当前时间
    # 设置今天的上午9点的目标触发时间
    target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    # 如果已经过了今天9点则将触发时间定位明天9点
    if now >= target_time:
        target_time += datetime.timedelta(days=1)
    # 计算时间间隔（以秒为单位）
    delay = (target_time - now).total_seconds()
    # 启动定时器，在明天的9点执行send_alert_am9函数
    timer_ = threading.Timer(delay, send_alert_am9)
    timer_.start()
