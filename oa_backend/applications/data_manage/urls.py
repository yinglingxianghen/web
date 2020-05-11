from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'pandect', views.PandectViewSet)
router.register(r'online-client', views.OnlineClientDataViewSet)
router.register(r'channel', views.ChannelInquiriesViewSet)
router.register(r'customer-use', views.CustomerUseViewSet)
router.register(r'online-product', views.OnlineProductViewSet)
router.register(r'site-oper', views.SiteOperViewSet)
router.register(r'grid_inquires', views.GridInquiresView)
router.register(r'sergrp_inquires', views.SerGrpInquriesViewSet)





urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^channellist/$', views.channellist),
    # url(r'^customer-oper/get_customer_oper/$', views.get_customer_oper),

]

api_urls = router.urls + urlpatterns
