from django.conf.urls import url
from django.utils.translation import gettext_lazy as _
from . import views


urlpatterns = [
    url(r'^create/$', views.order_create, name='order_create'),

]
