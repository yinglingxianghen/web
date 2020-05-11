# -*-coding:utf-8-*-

from django.conf.urls import url
from df_cart import views

urlpatterns = [
    url(r'^add/$', views.cart_add),
    url(r'^count/$', views.cart_count), # 获取用户购物车中商品的总数
]