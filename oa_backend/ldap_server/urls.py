"""vuejs_adminlte URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from applications.setup.views import help_center

api_urls = [
    url('^workorder/', include('applications.workorder_manage.urls')),
    url('^data/', include('applications.data_manage.urls')),
    url('^setup/', include('applications.setup.urls')),
    url('^product/', include('applications.production_manage.urls')),
]

admin.autodiscover()
urlpatterns = [
    url('^api/', include(api_urls)),
    url('^backend/', include('applications.backend.urls')),
    url('^permission/', include('applications.permission_and_staff_manage.urls')),
    url('^operlog/', include('applications.log_manage.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('^admin/', admin.site.urls),
    url(r'^setup/', include('applications.setup.urls')),
    url(r'^public/help_center', help_center)
]
