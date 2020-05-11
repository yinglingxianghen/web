from django.db import models

from applications.production_manage.models import Grid, Product, SingleSelection, ServerGroup
from common.models import SoftDeleteModel, TimeStampModel
from ldap_server.configs import STATION_CHOICES, CUSTOM_TYPES, DEPLOY_WAYS, CLI_CHOICES, CUSTOM_NEW, PROD_SERV_VERSIONS


class CompanyUrl(models.Model):
    """公司网址"""
    company_info = models.ForeignKey('CompanyInfo', related_name='company_url', db_constraint=False, null=True)
    company_url = models.CharField(max_length=50)

    def __str__(self):
        return self.company_url


class AreaInfo(models.Model):
    """地区表"""
    atitle = models.CharField(max_length=50)
    aPArea = models.ForeignKey('AreaInfo', null=True)

    class Meta:
        permissions = (
            ("view_areainfo", "Can see available area info"),
        )


class CompanyAddress(models.Model):
    """公司地址"""
    province = models.ForeignKey('AreaInfo', null=True, related_name='province', db_constraint=False)
    city = models.ForeignKey('AreaInfo', null=True, related_name='city', db_constraint=False)
    detail = models.CharField(max_length=100)

    def __str__(self):
        return "%s-%s-%s" % (self.province.atitle, self.city.atitle, self.detail)


class Industry(SoftDeleteModel, TimeStampModel):
    """所属行业"""
    industry = models.CharField(max_length=60)

    class Meta:
        permissions = (
            ("view_industry", "Can see available industry"),
        )

    def __str__(self):
        return self.industry


class ContactInfo(models.Model):
    """联系信息"""
    station = models.ForeignKey('OpenStationManage', related_name='link_info', db_constraint=False, null=True)

    # 联系人 单行文本框 linkman 字符串 - /必填
    linkman = models.CharField(max_length=50)

    # 联系电话 单行文本框 link_phone 字符串 12 / 必填
    link_phone = models.CharField(max_length=30)

    # 电子邮箱 单行文本框 link_email 字符串 50 / 必填
    link_email = models.CharField(max_length=50)

    # QQ号 单行文本框 link_qq 字符串 15 / 必填 
    link_qq = models.CharField(max_length=20)


class AccountConf(models.Model):
    """账户配置"""
    station = models.ForeignKey('OpenStationManage', related_name='account_conf', db_constraint=False, null=True)
    # 用户名  单行文本框  user_name  字符串  必填
    user_name = models.CharField(max_length=50)

    # 设置密码  单行文本框  set_pwd  字符串  16 / 必填
    set_pwd = models.CharField(max_length=200, null=True, blank=True)


class CompanyInfo(models.Model):
    # 站点类型 下拉列表框  整型：站点类型  试用客户1  正式客户2  市场渠道客户3  商务渠道客户4  自用站点5 / 必填
    station_type = models.IntegerField(choices=STATION_CHOICES)

    # 公司名称 单行文本框 company_name 字符串 50 / 必填
    company_name = models.CharField(max_length=50)

    # 【外键】公司网址 单行文本框 company_url 数组

    # 公司地址 下拉列表框 单行文本框 company_address 对象 256 / 必填
    company_address = models.OneToOneField(CompanyAddress, related_name='company_info', on_delete=models.CASCADE,
                                           null=True)
    # 公司简称 单行文本框 abbreviation
    abbreviation = models.CharField(max_length=50)

    # 公司邮箱 单行文本框 company_email 字符串 50 / 必填
    company_email = models.CharField(max_length=50)

    # 【外键】 所属行业 下拉列表框 industry 字符串 必填
    industry = models.ForeignKey(Industry, related_name='company_info', db_constraint=False, null=True)

    # 营业执照名称 单行文本框 GSZZ 字符串 50 / 必填
    GSZZ = models.CharField(max_length=50)

    # 客户性质  customer_type  布尔：0，新客户；1，老客户信息补录- / 必填
    customer_type = models.BooleanField(choices=CUSTOM_TYPES, default=CUSTOM_NEW)

    # 客服工作区域 单行文本框 service_area 字符串 128 / 必填
    service_area = models.CharField(max_length=128)

    class Meta:
        verbose_name = verbose_name_plural = "公司信息"

    def __str__(self):
        return self.company_name


class StationInfo(models.Model):
    # 企业ID 单行文本框 company_id 字符串 20 / 必填
    company_id = models.CharField(max_length=20, unique=True)
    # 部署方式 下拉列表框 deploy_way 整数：1.标准版 2.vip;3.vpc;4.企业版 /必填 部署方式选项：标准版 vip vpc 企业版
    deploy_way = models.IntegerField(choices=DEPLOY_WAYS)

    # 有效期 / 天 单行文本框 validity_days 整数 4 / 必填 输入限制：数字
    validity_days = models.IntegerField()

    # 节点选择 下拉列表框 grid 对象 必填 数据来源已创建的节点；选择部署方式后才可选择节点
    # apps.get_app_config('production_manage').get_model('Grid')
    grid = models.ForeignKey(Grid, null=True,
                             related_name='station_info', db_constraint=False)

    server_grp = models.ForeignKey(ServerGroup, null=True)

    # 客户版本 下拉列表框 cli_version  必填 客户版本选项：b2b2c b2c
    cli_version = models.IntegerField(choices=CLI_CHOICES)

    # 产品分类 经典版 重构版
    classify = models.SmallIntegerField(choices=PROD_SERV_VERSIONS, null=False, help_text="产品类别")

    # 合同产品 复选按钮 pact_products 列表 必填 数据来源于已创建的产品 apps.get_app_config('production_manage').get_model('Product')
    pact_products = models.ManyToManyField(Product,
                                           related_name='station_info', db_constraint=False)

    # 开站日期 日历控件 open_station_time 字符串 必填 不可选择历史日期
    open_station_time = models.DateField()

    # 到期日期 文字信息 close_station_time 字符串 必填 数据来源于已录入的从开站日期开始计算有效期，得出的结束时间；
    close_station_time = models.DateField()

    # 销售人员 单行文本框 sales 字符串 - / 必填
    sales = models.CharField(max_length=254)
    # 售前人员 单行文本框 pre_sales 字符串 - / 必填
    pre_sales = models.CharField(max_length=254)
    # 运营顾问 单行文本框 oper_cslt 字符串 - / 必填
    oper_cslt = models.CharField(max_length=254)
    # 实施顾问 单行文本框 impl_cslt 字符串 - / 必填
    impl_cslt = models.CharField(max_length=254)
    # 运营支持 单行文本框 oper_supt 字符串 - / 必填
    oper_supt = models.CharField(max_length=254)

    class Meta:
        verbose_name = verbose_name_plural = "站点信息"

    def __str__(self):
        return self.company_id

    @property
    def classsify_name(self):
        return dict(PROD_SERV_VERSIONS)[self.classify]


class OpenStationManage(SoftDeleteModel, TimeStampModel):
    STATUS_OFFLINE = False
    STATUS_ONLINE = True
    STATUS_TYPES = (
        (STATUS_OFFLINE, "下线"),
        (STATUS_ONLINE, "上线"),
    )
    online_status = models.BooleanField(default=False, choices=STATUS_TYPES)

    # 企业信息
    company_info = models.OneToOneField(CompanyInfo, related_name='open_station',
                                        on_delete=models.CASCADE, null=True)
    # 联系人信息
    # 【外键】 联系人信息：点击增加联系人 联系电话 电子邮箱和QQ号文本；最多增加三个联系人；增加的文本均必填。

    # 站点信息
    station_info = models.OneToOneField(StationInfo, related_name='open_station',
                                        on_delete=models.CASCADE, null=True)
    # 功能开关列表信息
    # func_list 选项 单行文本框、下拉列表框 selections 对象 选填 数据来源于功能开关带动的文本类型
    func_list = models.ManyToManyField(SingleSelection, related_name='station', db_constraint=False)

    # 联系人信息
    # 【外键】 联系人信息：点击增加联系人 联系电话 电子邮箱和QQ号文本；最多增加三个联系人；增加的文本均必填。

    # 【外键】 账户配置信息
    class Meta:
        permissions = (
            ("view_openstationmanage", "Can see available open station manage"),
        )
        verbose_name = verbose_name_plural = "开站管理"

    def __str__(self):
        return self.station_info.company_id
