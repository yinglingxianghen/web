"""careerushop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import  include, url
import xadmin
xadmin.autodiscover()


urlpatterns = [
    re_path(r'^admin/', xadmin.site.urls),
    re_path(r'^account/', include('account.urls')),
    re_path(r'^ueditor/', include('DjangoUeditor.urls')),
    re_path(r'^orders/', include('orders.urls')),
    re_path(r'^payment/', include('payment.urls')),
    re_path(r'^coupons/', include('coupons.urls')),
    re_path(r'^', include('shop.urls')),
    re_path(r'^cart/', include('cart.urls')),
    re_path(r'^search', include('haystack.urls')),  # 全文检索框架
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
