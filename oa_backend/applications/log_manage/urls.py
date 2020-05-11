from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'system-log', views.SystemLogViewSet)
router.register(r'personal-log', views.PersonalLogViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
