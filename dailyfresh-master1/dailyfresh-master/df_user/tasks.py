# -*-coding:utf-8-*-
from celery import task
from django.core.mail import send_mail
from django.conf import settings
import time

# @task
# def sayhello():
#     print('hello ...')
#     time.sleep(2)
#     print('world ...')

#@task
def send_register_success_mail(username, password, email):
    msg = '<h1>欢迎您成为天天生鲜注册会员</h1>请记好您的信息:<br/>用户名:' + username + '<br/>密码：' + password
    send_mail('欢迎信息',
              '',
              settings.EMAIL_FROM,
              [email],
              html_message=msg)
    time.sleep(5)






