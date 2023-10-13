import logging
import threading
import time
from dingtalkchatbot.chatbot import DingtalkChatbot
from django.core.cache import cache

webhook = 'https://oapi.dingtalk.com/robot/send?access_token' \
          '=403401f4b0ee81a7ea4b3355b85327bb71cfb33ef2f9ff6ce1db6e82e182af56'
secret = 'SECda9044fc2385908cadb9d84940c244d4070d6b647788dc29bea29459851de67e'
xiao_ding = DingtalkChatbot(webhook, secret=secret)  # 创建钉钉机器人实例
alerts_list = []  # 存储警告消息的列表
last_sent_time = 0  # 上次发送警告消息的时间戳
timer = None  # 定时器对象,用于定时发送警告消息
timer_ = None  # 定时器对象，用于每日定时发送简报消息


def get_warning(keys):
    messages = []
    for key in keys:
        name = key.split('-')[0]
        license_name = key.split('-')[1]
        target = key.split('-')[2]
        message = f"系统: {name}\n许可:{license_name}\n{target}最高超阈值使用率: {cache.get(key)}%"
        messages.append(message)
    # 将当前收集到的超过阈值的内容传至send_alert_to_dingtalk进行发送钉钉消息准备
    if messages:
        return "\n".join(messages)


def send_alert_to_dingtalk():
    """
    发送警告消息给钉钉    :return: None
    """
    global last_sent_time, alerts_list
    current_time = time.time()  # 获取当前时间戳
    # 尝试发送警告消息给钉钉
    alerts_list = list(set(alerts_list))
    alerts_str = ""
    for alert in alerts_list:
        if isinstance(alert, str):
            alerts_str += alert
        else:
            alerts_str += str(alert)
        alerts_str += '\n\n'
    try:
        xiao_ding.send_text(msg=alerts_str, is_at_all=False)  # 发送警告消息
        logging.info('钉钉消息发送成功')

    except Exception as e:
        logging.info("钉钉消息发送失败: %s", e)
    last_sent_time = current_time
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
    if message is not None:
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
    timer = threading.Timer(30 - (time.time() - last_sent_time), send_alert_to_dingtalk)
    timer.start()
