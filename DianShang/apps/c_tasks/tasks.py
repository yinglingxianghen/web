from django.conf import settings
from django.core.mail import send_mail

import os
import sys
sys.path.insert(0, './')
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myshop.settings")
django.setup()

from c_tasks.celery import app as app

# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    """发送激活邮件"""
    # 组织邮件内容
    subject = '电商平台欢迎你！'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = """
                        <h1>%s, 欢迎您注册会员</h1>
                        请点击以下链接激活您的账户(24个小时内有效)<br/>
                        <a href="http://127.0.0.1:8001/active/?key=%s">http://127.0.0.1:8001//active/?key=%s</a>
                    """ % (username, token, token)

    # 发送激活邮件
    # send_mail(subject=邮件标题, message=邮件正文,from_email=发件人, recipient_list=收件人列表)
    send_mail(subject, message, sender, receiver, html_message=html_message)











