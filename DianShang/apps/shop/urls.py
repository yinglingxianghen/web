from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^goodbuy/$', views.goodbuy, name='goodbuy'),

    url(r'^category/$', views.category, name='category'),
    url(r'^product_detail/$', views.product_detail, name='product_detail'),

    url(r'^hotsale_list/$', views.hotsale_list, name='hotsale_list'),
    url(r'^mobile_list/$', views.mobile_list, name='mobile_list'),
    url(r'^computer_list/$', views.computer_list, name='computer_list'),


    url(r'^(?P<category_id>[-\w]+)/$', views.category, name='category'),
    url(r'^(?P<id>\d+)/(?P<slug>[-\w]+)/$', views.product_detail, name='product_detail'),
    url(r'^search', include('haystack.urls')), # 全文检索框架
]
