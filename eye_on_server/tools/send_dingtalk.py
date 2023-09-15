import logging

from dingtalkchatbot.chatbot import DingtalkChatbot


def send_alert_to_dingtalk(data_str, alerts):
    # 尝试发送警告消息给钉钉
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=403401f4b0ee81a7ea4b3355b85327bb71cfb33ef2f9ff6ce1db6e82e182af56'
    secret = 'SECda9044fc2385908cadb9d84940c244d4070d6b647788dc29bea29459851de67e'

    for key, value in alerts.items():
        # 将内容转为字符串:
        data_str += key + str(value) + '\n'

    xiao_ding = DingtalkChatbot(webhook, secret=secret)
    try:
        xiao_ding.send_text(msg=data_str, is_at_all=False)
        logging.debug('钉钉消息发送成功')
    except Exception as e:
        logging.debug("钉钉消息发送失败: %s", e)
