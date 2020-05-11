# __author__ = itsneo1990
from django.conf.urls import url, include
from rest_framework import routers

from applications.setup import views

router = routers.DefaultRouter()
router.register('site-reception-group', views.SiteReceptionGroupView)
router.register(r'cli-industry', views.CliIndustrySet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^reception-groups', views.reception_groups),
    url(r'^avatar-upload', views.avatar_upload)
]

api_urls = router.urls + urlpatterns
