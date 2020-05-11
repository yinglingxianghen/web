from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'openstation', views.OpenStationManageSet)
router.register(r'companyinfo', views.CompanyInfoSet)
router.register(r'stationinfo', views.StationInfoSet)
router.register(r'industry', views.IndustrySet)
router.register(r'areainfo', views.AreaInfoSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='workorder_rest_framework')),
    url(r'^customer-oper/$', views.customer_oper_type),
]
