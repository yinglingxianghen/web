# -*-coding:utf-8-*-

from django.conf.urls import url
from df_user import views

urlpatterns = [
    url(r'^register/$', views.register), # 用户模块
    # url(r'^register_handle/$', views.register_handle), # 实现用户信息的注册
    url(r'^check_user_exit/$', views.check_user_exit), # 校验用户名是否存在
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^login_check/$', views.login_check),

    url(r'^$', views.user),
    url(r'^address/$', views.address),
    url(r'^order/$', views.order),
    url(r'^index/$', views.index),

]