from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route, api_view
from rest_framework.response import Response

from applications.data_manage.models import OperatingRecord
from applications.data_manage.views import SerGrpInquriesViewSet
from applications.log_manage.models import OperateLog
from applications.production_manage.models import ServerGroup
from applications.workorder_manage.models import OpenStationManage, Industry, AreaInfo, CompanyInfo, StationInfo
from applications.workorder_manage.serializers import OpenStationManageSerializer, IndustrySerializer, \
    AreaInfoSerializer, \
    CompanyInfoSerializer, StationInfoSerializer, SimpOpenStationManageSerializer
from common.custom_exception import PushError
from ldap_server.configs import OPERATE_ACTION_CHOICES
from libs.datetimes import str_to_datetime, str_to_date
from libs.push_service.site_push import checksiteid, delsiteid
from libs.staion_msg_handle import station_msg_push


class OpenStationManageSet(viewsets.ModelViewSet):
    queryset = OpenStationManage.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return SimpOpenStationManageSerializer
        else:
            return OpenStationManageSerializer

    def get_queryset(self):
        queryset = OpenStationManage.objects.all().order_by('-id')
        company_name = self.request.GET.get('company_name', "").strip()  #
        station_type = self.request.GET.get('station_type', "").strip()
        deploy_way = self.request.GET.get('deploy_way', "").strip()
        cli_version = self.request.GET.get('cli_version', "").strip()
        abbreviation = self.request.GET.get('abbreviation', '').strip()
        company_id = self.request.GET.get('company_id', '').strip()

        if company_name:  # 公司名称查询
            queryset = queryset.filter(company_info__company_name__contains=company_name)
        if abbreviation:  # 公司简称查询
            queryset = queryset.filter(company_info__abbreviation=abbreviation)
        if company_id:  # 企业id查询
            queryset = queryset.filter(station_info__company_id=company_id)
        if station_type:  # 站点类型查询
            queryset = queryset.filter(company_info__station_type=station_type)
        if deploy_way:  # 部署方式查询
            queryset = queryset.filter(station_info__deploy_way=deploy_way)
        if cli_version:  # 客户版本查询
            queryset = queryset.filter(station_info__cli_version=cli_version)
        return queryset

    @detail_route(methods=['put'])
    def modify_status(self, request, pk=None, *args, **kwargs):
        site = OpenStationManage.objects.all().get(pk=pk)
        company_id = site.station_info.company_id
        input_online_status = request.data.get('online_status', None)

        if input_online_status is None:
            return Response({'error': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)

        # 前端发送请求时未判断状态是否改变，所以，为减少对数据库不必要的读写，上线状态没变则直接返回
        if input_online_status == site.online_status:
            return Response(status=status.HTTP_200_OK)

        try:
            with transaction.atomic():
                site.online_status = input_online_status
                site.save()
                station_msg_push(site.station_info.company_id)
        except PushError as p:
            if p.value.startswith('11'):
                return Response({'error': p.value.lstrip('11')}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': '消息推送失败'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            OperateLog.create_log(request)
            # 如果新的上线状态为True，则将上线记录写入统计表
            if input_online_status:
                OperatingRecord.record_online(company_id)

            # 如果新的上线状态为False,则将下线记录写入统计表
            else:
                OperatingRecord.record_offline(company_id)

            return Response(status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def verify_company_id(self, request):
        company_id = request.GET.get('company_id', '').strip()
        grid_id = request.GET.get('grid_id', '').strip()
        if not (company_id and grid_id):
            return Response({'error': '参数错误'},
                            status=status.HTTP_400_BAD_REQUEST)
        if OpenStationManage.objects.all().filter(station_info__company_id=company_id):
            return Response({'error': '企业id重复'},
                            status=status.HTTP_400_BAD_REQUEST)
        success = checksiteid(siteid=company_id, grid_id=int(grid_id))
        if not success:
            return Response({"error": "线上该企业已存在"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def get_pact_products(self, request, pk=None, *args, **kwargs):
        site = self.get_object()
        ret = {'data': []}
        pact_products = site.station_info.pact_products.all().values_list('product', flat=True)
        ret['data'] = list(pact_products)
        return Response(ret, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        function：创建开站对象
        describe：用serializer的create将开站数据录入库,增加根据昨日该节点下各服务组咨询量，取咨询量最少的，为站点指定服务组
        date：20171130
        author：gzh
        version:1.10
        """
        open_data = request.data
        company_id = open_data['station_info']['company_id']
        grid_id = open_data['station_info']['grid']
        server_grp_name = SerGrpInquriesViewSet.min_sergrp_inquries(grid_id)
        server_grp = ServerGroup.objects.all().filter(group_name=server_grp_name).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                self.perform_create(serializer)
                site = serializer.instance
                site.station_info.server_grp = server_grp
                site.station_info.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            OperateLog.create_log(request)
            # 将新增客户记录写入统计表中
            OperatingRecord.record_create(company_id)

        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        open_data = request.data
        # 获取企业ID
        company_id = open_data['station_info']['company_id']
        # 获取本次请求传入的站点到期时间和产品名称列表
        input_close_station_time = str_to_date(open_data['station_info']['close_station_time'])
        input_pact_products = open_data['station_info']['pact_products']

        # 获取修改前的站点到期时间和产品名称列表
        pre_station_info = StationInfo.objects.filter(open_station__id=kwargs['pk']).select_related(
            'pact_products__product').values_list('pact_products__product', 'close_station_time')
        pre_station_dict = dict(pre_station_info)

        # 获取传入的节点名称和修改前的节点名称，对比，若不同，则获取新节点下的访问量最少的服务组对象
        input_grid_id = open_data['station_info']['grid']
        pre_grid_id = instance.station_info.grid
        pre_server_grp = getattr(instance.station_info, 'server_grp_id', None)
        if (input_grid_id != pre_grid_id) or (pre_server_grp is None):
            server_grp_name = SerGrpInquriesViewSet.min_sergrp_inquries(input_grid_id)
            server_grp = ServerGroup.objects.all().filter(group_name=server_grp_name).first()

        # 获取上线状态
        online_status = instance.online_status

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=open_data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 分经典版站点修改和重构版站点修改两种情况：流程---在保存完数据后，验证一下上线状态，若是上线，则调用推送接口；
        # 经典版站点修改：保存和推送都包在事务中
        if instance.station_info.classify == 1:
            try:
                with transaction.atomic():
                    self.perform_update(serializer)
                    if (input_grid_id != pre_grid_id) or (pre_server_grp is None):
                        instance.station_info.server_grp = server_grp
                        instance.station_info.save()

                    if online_status:
                        station_msg_push(company_id)
            except PushError as p:
                if p.value.startswith('11'):
                    return Response({'error': p.value.lstrip('11')}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': '消息推送失败'}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # 重构版站点修改：仅保存包在事务中，推送过程为异步方法
        else:
            try:
                with transaction.atomic():
                    self.perform_update(serializer)
                    if (input_grid_id != pre_grid_id) or (pre_server_grp is None):
                        instance.station_info.server_grp = server_grp
                        instance.station_info.save()
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            if online_status:
                station_msg_push(company_id)

        OperateLog.create_log(request)

        # 将续费客户记录写入统计表中
        if input_close_station_time != pre_station_info[0][1]:
            OperatingRecord.record_renewal(company_id)

        # 将新增产品客户记录写入统计表中
        for each in input_pact_products:
            if each not in pre_station_dict.keys():
                OperatingRecord.record_add_product(company_id)

        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if delsiteid(obj.station_info.grid.id, obj.station_info.company_id):
            OperateLog.create_log(request)
            return super(OpenStationManageSet, self).destroy(request, *args, **kwargs)
        else:
            return Response({'error': '删除站点推送失败'}, status=status.HTTP_400_BAD_REQUEST)


class CompanyInfoSet(viewsets.ModelViewSet):
    queryset = CompanyInfo.objects.all().order_by("-id")
    serializer_class = CompanyInfoSerializer


class StationInfoSet(viewsets.ModelViewSet):
    queryset = StationInfo.objects.all().order_by("-id")
    serializer_class = StationInfoSerializer


class IndustrySet(viewsets.ModelViewSet):
    queryset = Industry.objects.all().order_by('-id')
    serializer_class = IndustrySerializer
    pagination_class = None


class AreaInfoSet(viewsets.ModelViewSet):
    queryset = AreaInfo.objects.all().order_by('-id')
    serializer_class = AreaInfoSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = AreaInfo.objects.all().order_by('-id')
        level = self.request.GET.get('level', "").strip()  # 是什么级别的：省或市
        province = self.request.GET.get('province', "").strip()

        if level:  # 查询所有省, level为1
            if level == '1':
                queryset = queryset.filter(aPArea__isnull=True)
        if province:  # 查询某省所有城市
            queryset = queryset.filter(aPArea__id=province)

        return queryset


@api_view(['GET'])
def customer_oper_type(request):
    fields = ['id', 'name']
    ret = {'data': []}
    for item in OPERATE_ACTION_CHOICES:
        ret['data'].append(dict(zip(fields, item)))
    return Response(ret, status=status.HTTP_200_OK)
