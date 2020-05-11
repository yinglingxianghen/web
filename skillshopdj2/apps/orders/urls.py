from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^orderlist/$', views.orderlist, name='orderlist'),
    url(r'^seckillproduct_list/$', views.seckillproduct_list, name='seckillproduct_list'),
    url(r'^initstock/$', views.initstock, name='initstock'),
    url(r'^endseckill/$', views.endseckill, name='endseckill'),
]
