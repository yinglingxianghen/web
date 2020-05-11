from django.conf.urls import url
from .views import *


urlpatterns = [
     #url(r'^login/$', views.user_login, name='login'),
    url(r'^logout$', do_logout, name='logout'),
    url(r'^ajax_login', ajax_login, name='ajax_login'),
    url(r'^ajax_register', ajax_register, name='ajax_register'),
    url(r'^valicode/$', valicode, name='valicode'),
    url(r'^edit', edit, name='edit'),
    url(r'^password_change', password_change, name='password_change'),
]
