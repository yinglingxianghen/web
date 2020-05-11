from django.contrib import admin

from applications.workorder_manage.models import StationInfo, OpenStationManage, CompanyInfo

admin.site.register(StationInfo)
admin.site.register(OpenStationManage)
admin.site.register(CompanyInfo)
