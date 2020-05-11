import logging

from rest_framework import serializers
from applications.workorder_manage.models import Industry
from applications.setup.models import SiteReceptionGroup
from applications.workorder_manage.models import StationInfo


log = logging.getLogger("Django")


class CliIndustrySerializer(serializers.ModelSerializer):
    def get_site_num(self, data):
        site_num = data.company_info.count()
        return site_num

    site_num = serializers.SerializerMethodField()

    class Meta:
        model = Industry
        fields = ('id', 'industry', 'site_num')


class SiteReceptionGroupSerializer(serializers.ModelSerializer):
    """接待组站点序列化器"""
    company_id = serializers.SlugField()

    class Meta:
        model = SiteReceptionGroup
        fields = ('id', 'title', 'group_id', 'avatar', 'manager', 'phone_number', 'email', 'desc', 'url', 'company_id')

    # 验证company_id是否合法
    def validate_company_id(self, value):
        sites = StationInfo.objects.filter(company_id=value)
        if not sites:
            raise serializers.ValidationError("该企业ID对应企业不存在")
        elif len(sites) > 1:
            raise serializers.ValidationError(f"{value}对应多家站点信息，请联系后端管理员更正")
        return value

    def create(self, validated_data):
        company_id = validated_data.pop("company_id")
        if SiteReceptionGroup.objects.all().filter(site__company_id=company_id):
            raise serializers.ValidationError(f"该站点已添加接待组，请勿重复添加")
        validated_data["site"] = StationInfo.objects.get(company_id=company_id)
        # 创建接待组
        reception_group = SiteReceptionGroup.objects.create(**validated_data)
        return reception_group

    def update(self, instance, validated_data):
        company_id = validated_data.pop("company_id")
        validated_data["site"] = StationInfo.objects.get(company_id=company_id)
        # 更新其他字段
        instance = super(SiteReceptionGroupSerializer, self).update(instance, validated_data)
        return instance
