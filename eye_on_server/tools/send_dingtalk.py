import logging
import threading
import time

from dingtalkchatbot.chatbot import DingtalkChatbot

webhook = 'https://oapi.dingtalk.com/robot/send?access_token' \
          '=403401f4b0ee81a7ea4b3355b85327bb71cfb33ef2f9ff6ce1db6e82e182af56'
secret = 'SECda9044fc2385908cadb9d84940c244d4070d6b647788dc29bea29459851de67e'

alerts_list = []
last_sent_time = 0
alerts_str = ""
timer = None


def send_alert_to_dingtalk():
    global last_sent_time, alerts_str
    # alerts_list.append(alerts)
    # 获取当前时间戳
    current_time = time.time()
    print(last_sent_time)
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
        alerts_str +=alert
    xiao_ding = DingtalkChatbot(webhook, secret=secret)
    try:
        xiao_ding.send_text(msg=alerts_str, is_at_all=False)
        logging.info('钉钉消息发送成功')
    except Exception as e:
        logging.info("钉钉消息发送失败: %s", e)
    last_sent_time = current_time
    alerts_str = ""
    alerts_list.clear()


def process_message(message):
    global last_sent_time, alerts_list, timer

    # 将消息添加至列表
    alerts_list.append(message)

    # 检查时间间隔是否超过5秒
    current_time = time.time()
    if current_time - last_sent_time >= 5 or len(alerts_list) >= 10:
        if timer is not None and timer.is_alive():
            # 如果定时器正在运行,则取消重置定时器
            timer.cancel()
            send_alert_to_dingtalk()  # 手动调用发送函数
        else:
            send_alert_to_dingtalk()  # 直接调用发送函数
        # 启动新的定时器，5 秒后执行处理函数
        timer = threading.Timer(5, send_alert_to_dingtalk)
        timer.start()
