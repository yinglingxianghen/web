import datetime

from django.db import models

from applications.workorder_manage.models import OpenStationManage
from common.models import DataHistoryModel
from ldap_server.configs import CHANNEL_CHOICES, OPERATE_ACTION_CHOICES, OPERATE_CREATE, OPERATE_RENEWAL, \
    OPERATE_ADD_PRODUCT, OPERATE_ONLINE, OPERATE_OFFLINE
from libs.datetimes import date_to_str


class InquiriesData(DataHistoryModel):
    company_id = models.CharField(max_length=50, help_text="站点ID")
    channel = models.SmallIntegerField(choices=CHANNEL_CHOICES, help_text="渠道类别")
    inquires_num = models.IntegerField(default=0, help_text="咨询量")
    server_grp = models.CharField(max_length=200, help_text="服务组", null=True, blank=True)

    class Meta:
        verbose_name_plural = verbose_name = "渠道别咨询量记录"
        permissions = (
            ("view_overview-data", "查看咨询量"),
        )

    def __str__(self):
        str_date = date_to_str(self.date)
        return f"{self.company_id}-{str_date}"


class OnlineClientData(DataHistoryModel):
    online_num = models.IntegerField(default=0, help_text="在线客户数量")

    class Meta:
        verbose_name_plural = verbose_name = "在线客户数量"

    def __str__(self):
        return date_to_str(self.date)


class OnlineProductData(DataHistoryModel):
    online_num = models.IntegerField(default=0, help_text="在线客户使用产品数量")
    product_id = models.CharField(max_length=50, help_text="产品ID")

    class Meta:
        verbose_name_plural = verbose_name = "在线产品使用数量"

    def __str__(self):
        str_date = date_to_str(self.date)
        return f"{self.product_id}-{str_date}"


class OperatingRecord(DataHistoryModel):
    action = models.SmallIntegerField(choices=OPERATE_ACTION_CHOICES, help_text="操作行为")
    num = models.IntegerField(default=0, help_text="统计数量")

    class Meta:
        verbose_name_plural = verbose_name = "运营记录"
        permissions = (
            ("view_ops-data", "查看运营记录"),
            ("view_prod-oper-data", "查看产品运营记录")
        )

    @classmethod
    def record_create(cls, site_id):
        """新增客户"""
        site = OpenStationManage.objects.get(station_info__company_id=site_id)
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_CREATE,
        )
        record.num += 1
        record.save()

    @classmethod
    def record_renewal(cls, site_id):
        """续费客户"""
        site = OpenStationManage.objects.get(station_info__company_id=site_id)
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_RENEWAL,
        )

        record.num += 1
        record.save()

    @classmethod
    def record_add_product(cls, site_id):
        """新增产品用户"""
        site = OpenStationManage.objects.get(station_info__company_id=site_id)
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_ADD_PRODUCT,
        )
        record.num += 1
        record.save()

    @classmethod
    def record_online(cls, site_id):
        """上线用户"""
        site = OpenStationManage.objects.get(station_info__company_id=site_id)
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_ONLINE,
        )
        record.num += 1
        record.save()

    @classmethod
    def record_offline(cls, site_id):
        """下线用户"""
        site = OpenStationManage.objects.get(station_info__company_id=site_id)
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_OFFLINE,
        )
        record.num += 1
        record.save()
