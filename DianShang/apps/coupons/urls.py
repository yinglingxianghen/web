from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^coupon_list/$', views.coupon_list, name='coupon_list'),
]