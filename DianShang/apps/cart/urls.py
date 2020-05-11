from django.conf.urls import url
from django.utils.translation import gettext_lazy as _
from . import views


urlpatterns = [
    url(r'^cart_detail/$', views.cart_detail, name='cart_detail'),
    # url(r'^add/(?P<product_id>\d+)/$', views.cart_add, name='cart_add'),
    url(r'^cart_delete/$', views.cart_delete, name='cart_delete'),
    url(r'^cart_add/$', views.cart_add, name='cart_add'),
    url(r'^cart_add_ajax/$', views.cart_add_ajax, name='cart_add_ajax'),
]
