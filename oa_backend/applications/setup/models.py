from django.db import models

from applications.workorder_manage.models import StationInfo
from common.models import SoftDeleteModel


class SiteReceptionGroup(SoftDeleteModel):
    title = models.CharField(max_length=20, help_text="接待组名称")
    group_id = models.CharField(max_length=100, help_text="接待组ID")
    manager = models.CharField(max_length=20, help_text="接待经理")
    phone_number = models.CharField(max_length=20, help_text="电话")
    email = models.EmailField(help_text="Email")
    desc = models.CharField(max_length=100, help_text="一句话介绍")
    url = models.URLField(help_text="网址")
    avatar = models.URLField(help_text="显示头像", default="")
    site = models.OneToOneField(StationInfo, help_text="关联站点")

    class Meta:
        permissions = (
            ("view_sitereceptiongroup", "Can see available site_reception_group"),
        )

    @property
    def company_id(self):
        return self.site.company_id
