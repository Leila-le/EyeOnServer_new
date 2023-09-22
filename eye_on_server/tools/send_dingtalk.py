import logging
import threading
import time

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from dingtalkchatbot.chatbot import DingtalkChatbot
import hmac
import hashlib
import base64
import urllib.parse
from time import time

webhook = 'https://oapi.dingtalk.com/robot/send?access_token' \
          '=403401f4b0ee81a7ea4b3355b85327bb71cfb33ef2f9ff6ce1db6e82e182af56'
secret = 'SECda9044fc2385908cadb9d84940c244d4070d6b647788dc29bea29459851de67e'

alerts_list = []  # 存储警告消息的列表
last_sent_time = 0  # 上次发送警告消息的时间戳
alerts_str = ""  # 警告消息的字符串形式
timer = None  # 定时器对象,用于定时发送警告消息


def send_alert_to_dingtalk():
    """
    发送警告消息给钉钉
    :return: None
    """
    global last_sent_time, alerts_str
    current_time = time.time()  # 获取当前时间戳
    # 尝试发送警告消息给钉钉
    i = 1
    while i < len(alerts_list):

        system_license_previous = alerts_list[i - 1].split("\n")[:2]
        system_license_new = alerts_list[i].split("\n")[:2]
        have_cpu = alerts_list[i - 1].split("\n")[3]
        print('system_license', system_license_previous)
        if system_license_previous == system_license_new:
            if "CPU" in have_cpu:
                cpu_value = have_cpu.split(':')[1].strip('%')

            alerts_list[i - 1] = alerts_list[i]
            alerts_list.remove(alerts_list[i])
            last_sent_time = current_time
        else:
            i += 1
    for alert in alerts_list:
        alerts_str += alert
    xiao_ding = DingtalkChatbot(webhook, secret=secret)  # 创建钉钉机器人实例
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
    if current_time - last_sent_time >= 20 or len(alerts_list) >= 30:
        if timer is not None and timer.is_alive():
            timer.cancel()  # 如果定时器正在运行,则取消重置定时器
            send_alert_to_dingtalk()  # 手动调用发送函数
        else:
            send_alert_to_dingtalk()  # 直接调用发送函数
        # 启动新的定时器，5 秒后执行处理函数
        timer = threading.Timer(5, send_alert_to_dingtalk)
        timer.start()


# 钉钉机器人数字签名计算
def get_digest():
    # 取毫秒级别时间戳，round(x, n) 取x小数点后n位的结果，默认取整
    timestamp = str(round(time() * 1000))
    secret_enc = secret.encode('utf-8')  # utf-8编码
    string_to_sign = '{}\n{}'.format(timestamp, secret)  # 字符串格式化拼接
    string_to_sign_enc = string_to_sign.encode('utf-8')  # utf-8编码
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()  # HmacSHA256算法计算签名
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # Base64编码后进行urlEncode
    #  返回时间戳和计算好的编码拼接字符串，后面直接拼接到Webhook即可
    return f"&timestamp={timestamp}&sign={sign}"


# 简单发送markdown消息
def warning_bot(massage, title):
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": massage
        },
    }
    # 机器人链接地址，发post请求 向钉钉机器人传递指令
    webhook_url = webhook
    # 利用requests发送post请求
    req = requests.post(webhook_url + get_digest(), json=data)


# 每天定时9:00发送服务器情况到钉群
def every_day_nine(message):

    title = '服务器基本信息'
    warning_bot(message, title)


#
# 选择BlockingScheduler调度器
sched = BlockingScheduler(timezone='Asia/Shanghai')

# job_every_nine 每天早上9点运行一次  日常发送
sched.add_job(every_day_nine, 'cron', hour=21, minute=55)

# 启动定时任务
sched.start()
