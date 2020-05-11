from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^process/$', payment_process, name='process'),
    url(r'^done/$', payment_done, name='done'),
    url(r'^canceled/$', payment_canceled, name='canceled'),
    url(r'^paychoice/$', paychoice, name='paychoice'),
    url(r'^paying', paying, name="paying"),
    url(r'^alipayed_notify/$', alipay_async_notify, name="alipayed_notify"),
    url(r'^alipayed_success/$', alipay_success, name="alipayed_success"),
    url(r'^wxpaying/$', paying_for_weixin_pay, name="wxpaying"),
]
