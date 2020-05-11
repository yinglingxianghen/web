"""hd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from hdvis.views import *

urlpatterns = [
	# url(r'^admin/', admin.site.urls),
	# url(r'^frame/',frame),
	# url(r'^test/', test),

	# data
	url(r'^vis', vis),
	# # login
	# url(r'^login/', login, name='login'),
	# 
	# # signin
	# url(r'^signin/', signin),

	# views
	url(r'^univar', univar),
	url(r'^bivar', bivar),
	url(r'^multivar', multivar),
	url(r'^analysis', analysis),
	url(r'^monitor', monitor),
	url(r'^realtime', realtime),
	
	url(r'^modeldata', modeldata),
	url(r'^modelresult',modelresult),
	url(r'^realtimemonitor',realtimemonitor),
	url(r'^report', report),
	# url(r'^rmonitor', lines),
	# url(r'^srmonitor', realtimemonitor),
	url(r'^getDataJson', getDataJson),

	url(r'^processdata', processdata),
	url(r'^progressrealtime', progressRealtime),
	url(r'^monirealtime', monitor_realtime),

	url(r'^xf_page', xf_page),
	url(r'^getxfsdata', getXfsData),


	url(r'^myindex', myindex),
	url(r'^myindexPost', myindexPost),


	url(r'^sendRawData',sendRawData),
	url(r'^getRawData',getRawData),

	url(r'^sendFengData',sendFengData),
	url(r'^getFengData',getFengData),

	url(r'^sendXfsData',sendXfsData),
	url(r'^getXfsData',getXfsData),

	url(r'^sendIsofData',sendIsofData),
	url(r'^getIsofData',getIsofData),


]

