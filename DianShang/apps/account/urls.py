from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^login/$', views.user_login, name='login'),
    # url(r'^$', views.dashboard, name='dashboard'),
    #
    url(r'^register/$', views.register, name='register'),
    url(r'^active/$', views.Active, name='active'),  # 激活
    url(r'^updateuserinfo/$', views.updateuserinfo, name='updateuserinfo'),
    url(r'^address/$', views.address, name='address'),
    url(r'^getCity/$', views.getCity, name='getCity'),
    url(r'^getAreas/$', views.getAreas, name='getAreas'),
    url(r'^getProvince/$', views.getProvince, name='getProvince'),
    url(r'^do_logout', views.do_logout, name='do_logout'),
    url(r'^updatepassword', views.updatepassword, name='updatepassword'),
    url(r'^myscore', views.myscore, name='myscore'),
    url(r'^myorder', views.myorder, name='myorder'),
    url(r'^mycomment', views.mycomment, name='mycomment'),
    url(r'^mycart', views.mycart, name='mycart'),
    url(r'^coupon', views.coupon, name='coupon'),
    url(r'^mymessage', views.mymessage, name='mymessage'),
    url(r'^myfav', views.myfav, name='myfav'),
]
