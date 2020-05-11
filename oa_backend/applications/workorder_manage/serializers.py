import logging

from django.db import transaction
from rest_framework import serializers

from applications.production_manage.models import Grid, Product, SingleSelection, FunctionInfo
from applications.production_manage.serializers import SingleSelectionSerializer, ForDependSelectionSerializer, \
    ForOpenSelectionSerializer
from applications.workorder_manage.models import CompanyUrl, AreaInfo, CompanyAddress, Industry, ContactInfo, \
    AccountConf, \
    OpenStationManage, CompanyInfo, StationInfo

log = logging.getLogger("Django")


# 公司网址 单行文本框 company_url 数组
class CompanyUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUrl
        fields = ('id', 'company_url')


class AreaInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaInfo
        fields = ('id', 'atitle', 'aPArea')


class CompanyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAddress
        fields = ('id', 'province', 'city', 'detail')


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'industry')


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ('id', 'linkman', 'link_phone', 'link_email', 'link_qq')


class AccountConfSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountConf
        fields = ('id', 'user_name', 'set_pwd')


class SimpCompanyInfoSerializer(serializers.ModelSerializer):
    # 【外键】 所属行业 下拉列表框 industry 字符串 必填 外键
    industry = serializers.SlugRelatedField(
        read_only=True,
        slug_field='industry'
    )

    class Meta:
        model = CompanyInfo
        fields = ('id', 'station_type', 'industry', 'company_name')


class CompanyInfoSerializer(serializers.ModelSerializer):
    # 【外键】公司网址 单行文本框 company_url 数组
    company_url = CompanyUrlSerializer(many=True, read_only=True)

    # 【外键】公司地址 下拉列表框 单行文本框 company_address 对象 256 / 必填
    company_address = CompanyAddressSerializer(read_only=True)

    # 【外键】 所属行业 下拉列表框 industry 字符串 必填 外键
    industry = serializers.SlugRelatedField(
        read_only=True,
        slug_field='industry'
    )

    class Meta:
        model = CompanyInfo
        fields = (
            'id', 'station_type', 'company_name', 'abbreviation', 'company_url', 'company_address', 'industry',
            'company_email', 'GSZZ',
            'customer_type', 'service_area')


class SimpStationInfoSerializer(serializers.ModelSerializer):
    # 节点选择 下拉列表框 grid 对象 必填 数据来源已创建的节点；选择部署方式后才可选择节点
    grid = serializers.SlugRelatedField(
        read_only=True,
        slug_field='grid_name'
    )

    def get_classify_name(self, data):
        return data.classsify_name

    classify_name = serializers.SerializerMethodField()

    class Meta:
        model = StationInfo
        fields = (
            'id', 'company_id', 'grid', 'classify_name', 'deploy_way', 'cli_version', 'open_station_time',
            'close_station_time')


class StationInfoSerializer(serializers.ModelSerializer):
    # 节点选择 下拉列表框 grid 对象 必填 数据来源已创建的节点；选择部署方式后才可选择节点
    # grid = serializers.SlugRelatedField(
    #     read_only=True,
    #     slug_field='grid_name'
    # )

    # 合同产品 复选按钮 pact_products 列表 必填 数据来源于已创建的产品
    # pact_products = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='product'
    # )

    class Meta:
        model = StationInfo
        fields = (
            'id', 'company_id', 'deploy_way', 'validity_days', 'grid', 'classify', 'cli_version', 'pact_products',
            'open_station_time',
            'close_station_time', 'sales', 'pre_sales', 'oper_cslt', 'impl_cslt', 'oper_supt')


class SimpOpenStationManageSerializer(serializers.ModelSerializer):
    company_info = SimpCompanyInfoSerializer(read_only=True)
    station_info = SimpStationInfoSerializer(read_only=True)

    class Meta:
        model = OpenStationManage
        fields = (
            'id', 'online_status', 'company_info', 'station_info')


class OpenStationManageSerializer(serializers.ModelSerializer):
    """
    企业信息
    """
    company_info = CompanyInfoSerializer(read_only=True)

    # 【外键】 联系人信息：点击增加联系人 联系电话 电子邮箱和QQ号文本；最多增加三个联系人；增加的文本均必填。
    link_info = ContactInfoSerializer(many=True, read_only=True)

    """
    站点信息
    """
    station_info = StationInfoSerializer(read_only=True)

    # func_list 选项 单行文本框、下拉列表框 selections 对象 选填 数据来源于功能开关带动的文本类型
    # 具体到节点和版本 请求product/version/
    func_list = ForOpenSelectionSerializer(many=True, read_only=True)

    # 【外键】 账户配置信息 account_conf
    account_conf = AccountConfSerializer(many=True, read_only=True)

    class Meta:
        model = OpenStationManage
        fields = (
            'id', 'online_status', 'company_info', 'func_list', 'account_conf', 'station_info', 'link_info')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                station = super(OpenStationManageSerializer, self).create(validated_data)

                """
                公司信息
                """
                company_url_list = self.initial_data['company_info'].pop('company_url')
                company_address = self.initial_data['company_info'].pop('company_address')
                industry = self.initial_data['company_info'].pop('industry')

                cmp_data = self.initial_data['company_info']
                company_info = CompanyInfo.objects.create(open_station=station, **cmp_data)
                company_info.open_station = station

                # compcany_url
                for url in company_url_list:
                    com_url = CompanyUrl.objects.create(company_url=url['company_url'], company_info=company_info)
                    com_url.company_info = company_info
                    com_url.save()

                # company_address
                province = AreaInfo.objects.all().get(pk=company_address['province'])
                city = AreaInfo.objects.all().get(pk=company_address['city'])
                com_ad = CompanyAddress.objects.all().create(company_info=company_info, province=province, city=city,
                                                             detail=company_address['detail'])
                com_ad.company_info = company_info
                com_ad.save()

                # industry
                company_info.industry = Industry.objects.all().get(industry=industry)

                company_info.save()

                """
                联系人信息
                """
                # link_info
                link_info_list = self.initial_data['link_info']
                for link_info in link_info_list:
                    ContactInfo.objects.create(station=station, **link_info)

                """
                站点信息
                """
                grid = self.initial_data['station_info'].pop('grid')
                pact_products_list = self.initial_data['station_info'].pop('pact_products')

                sta_data = self.initial_data['station_info']
                station_info = StationInfo.objects.create(open_station=station, **sta_data)
                station_info.open_station = station

                # grid
                station_info.grid = Grid.objects.all().get(id=grid)

                # pact_products
                for product in pact_products_list:
                    station_info.pact_products.add(Product.objects.all().get(id=product))
                station_info.save()

                """
                功能开关表信息
                """
                # func_list
                prod_selc_list = self.initial_data['func_list']
                for prod_selc in prod_selc_list:
                    for selc in prod_selc['id']:
                        station.func_list.add(SingleSelection.objects.all().get(pk=selc))
                    for txt in prod_selc['ipu']:
                        func = FunctionInfo.objects.all().get(pk=txt['id'])
                        text = SingleSelection.objects.create(function=func, select_name=txt['value'],
                                                              select_value=txt['value'])
                        text.save()
                        station.func_list.add(text)

                """
                账户配置信息
                """
                # account_conf
                account_conf_list = self.initial_data['account_conf']
                for account_conf in account_conf_list:
                    AccountConf.objects.create(station=station, **account_conf)

                station.save()
                return station
        except Exception as e:
            log.error(e)
            raise TypeError(e)

    def update(self, instance, validated_data):

        instance = super(OpenStationManageSerializer, self).update(instance, validated_data)

        """
        公司信息
        """
        cmp_data = self.initial_data['company_info']
        company_info = instance.company_info

        company_url_list = cmp_data.pop('company_url')
        CompanyUrl.objects.all().filter(company_info=company_info).delete()

        company_address = cmp_data.pop('company_address')

        industry = cmp_data.pop('industry')

        # compcany_url
        for url in company_url_list:
            com_url = CompanyUrl.objects.create(company_url=url['company_url'], company_info=company_info)
            com_url.save()

        # company_address
        if company_info.company_address:
            company_info.company_address.province = AreaInfo.objects.all().get(pk=company_address['province'])
            company_info.company_address.city = AreaInfo.objects.all().get(pk=company_address['city'])
            company_info.company_address.detail = company_address['detail']
            company_info.company_address.save()
        else:
            province = AreaInfo.objects.all().get(pk=company_address['province'])
            city = AreaInfo.objects.all().get(pk=company_address['city'])
            com_ad = CompanyAddress.objects.all().create(company_info=company_info, province=province, city=city,
                                                         detail=company_address['detail'])
            com_ad.company_info = company_info
            com_ad.save()

        # industry
        company_info.industry = Industry.objects.all().get(industry=industry)

        company_info.station_type = cmp_data.get('station_type', company_info.station_type)
        company_info.company_name = cmp_data.get('company_name', company_info.company_name)
        company_info.abbreviation = cmp_data.get('abbreviation', company_info.abbreviation)

        company_info.company_email = cmp_data.get('company_email', company_info.company_email)
        company_info.GSZZ = cmp_data.get('GSZZ', company_info.GSZZ)
        company_info.customer_type = cmp_data.get('customer_type', company_info.customer_type)
        company_info.service_area = cmp_data.get('service_area', company_info.service_area)

        company_info.save()

        """
        联系人信息
        """
        # link_info
        ContactInfo.objects.all().filter(station=instance).delete()
        link_info_list = self.initial_data['link_info']
        for link_info in link_info_list:
            ContactInfo.objects.create(station=instance, **link_info)

        """
        站点信息
        """
        sta_data = self.initial_data['station_info']
        grid = sta_data.pop('grid')
        pact_products_list = sta_data.pop('pact_products')
        station_info = instance.station_info

        station_info.deploy_way = sta_data.get('deploy_way', station_info.deploy_way)
        station_info.validity_days = sta_data.get('validity_days', station_info.validity_days)
        station_info.cli_version = sta_data.get('cli_version', station_info.cli_version)
        station_info.open_station_time = sta_data.get('open_station_time', station_info.open_station_time)
        station_info.close_station_time = sta_data.get('close_station_time', station_info.close_station_time)
        station_info.sales = sta_data.get('sales', station_info.sales)
        station_info.pre_sales = sta_data.get('pre_sales', station_info.pre_sales)
        station_info.oper_cslt = sta_data.get('oper_cslt', station_info.oper_cslt)
        station_info.impl_cslt = sta_data.get('impl_cslt', station_info.impl_cslt)
        station_info.oper_supt = sta_data.get('oper_supt', station_info.oper_supt)

        station_info.open_station = instance

        # grid
        station_info.grid = Grid.objects.all().get(id=grid)

        # pact_products
        station_info.pact_products.clear()
        for product in pact_products_list:
            station_info.pact_products.add(Product.objects.all().get(id=product))
        station_info.save()

        """
        功能开关表信息
        """
        # func_list
        instance.func_list.clear()
        prod_selc_list = self.initial_data['func_list']
        for prod_selc in prod_selc_list:
            for selc in prod_selc['id']:
                instance.func_list.add(SingleSelection.objects.all().get(pk=selc))
            for txt in prod_selc['ipu']:
                func = FunctionInfo.objects.all().get(pk=txt['id'])
                text = SingleSelection.objects.create(function=func, select_name=txt['value'],
                                                      select_value=txt['value'])
                text.save()
                instance.func_list.add(text)

        """
        账户配置信息
        """
        # account_conf
        AccountConf.objects.all().filter(station=instance).delete()
        account_conf_list = self.initial_data['account_conf']

        for account_conf in account_conf_list:
            AccountConf.objects.create(station=instance, **account_conf)

        instance.save()
        return instance
