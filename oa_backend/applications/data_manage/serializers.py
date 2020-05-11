import datetime

from django.db.models import Sum, Min
from rest_framework import serializers

from applications.data_manage.models import InquiriesData, OnlineClientData, OnlineProductData
from applications.workorder_manage.models import OpenStationManage
from ldap_server.configs import DEPLOY_WAYS, CHANNEL_UNKNOWN, CHANNEL_PC, CHANNEL_WECHAT, CHANNEL_APP, CHANNEL_WAP, \
    CHANNEL_IOS, CHANNEL_ANDROID, CHANNEL_WEIBO, CHANNEL_QQ


class PandectDataSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(source='station_info.company_id', read_only=True)
    company_name = serializers.CharField(source='company_info.company_name', read_only=True)
    open_station_time = serializers.DateField(source='station_info.open_station_time', read_only=True)
    close_station_time = serializers.DateField(source='station_info.close_station_time', read_only=True)
    industry = serializers.CharField(source='company_info.industry.industry', read_only=True)
    grid = serializers.CharField(source='station_info.grid.grid_name', read_only=True)
    server_grp = serializers.CharField(source='station_info.server_grp.group_name', read_only=True)

    def get_deploy_way(self, data):
        obj = dict(DEPLOY_WAYS)[data.station_info.deploy_way]
        if obj:
            return obj
        return None

    deploy_way = serializers.SerializerMethodField()

    class Meta:
        model = OpenStationManage
        fields = ('id', 'company_id', 'company_name', 'open_station_time', 'close_station_time', 'industry', \
                  'deploy_way', 'grid', 'server_grp')


class OnlineClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineClientData
        fields = '__all__'


class InquiriesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiriesData
        fields = '__all__'


class OnlineProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineProductData
        fields = ('id', 'online_num', 'product_id', 'deploy_way', 'industry', 'date')
