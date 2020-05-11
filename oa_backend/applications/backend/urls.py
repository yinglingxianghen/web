from django.conf.urls import url
from rest_framework import routers

from applications.backend import views
from applications.backend import viewsUtil

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

api_urls = router.urls + [
]

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^verifycode/$', viewsUtil.verifycode),
    url(r'^test/$', views.test),
    url(r'^push_service_infopush/$', views.push_service_infopush),
]
