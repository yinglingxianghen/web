# Create your views here.
import csv
import random
import codecs
import collections
import datetime
from django.db.models import Sum, Min, Prefetch
from django.http import HttpResponse
from rest_framework import mixins, status
from rest_framework.decorators import list_route, api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from applications.data_manage.models import OnlineClientData, InquiriesData, OnlineProductData, OperatingRecord
from applications.data_manage.serializers import InquiriesDataSerializer, OnlineClientSerializer, PandectDataSerializer, \
    OnlineProductSerializer
from applications.production_manage.models import Product, Grid, ServerGroup
from applications.workorder_manage.models import OpenStationManage, Industry, StationInfo
from ldap_server.configs import CHANNEL_CHOICES, DEPLOY_WAYS, OPERATE_ACTION_CHOICES, CHANNEL_TYPES
from libs.datetimes import str_to_date, dates_during, date_to_str


class PandectViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = OpenStationManage.objects.all().order_by('-id')
    serializer_class = PandectDataSerializer

    # def check_permissions(self, request):
    #     if not request.user.has_perm("data_manage.view_overview-data"):
    #         self.permission_denied(request)

    def get_queryset(self):
        queryset = OpenStationManage.objects.all(). \
            prefetch_related('station_info', 'company_info', \
                             'company_info__industry', 'station_info__grid',
                             'station_info__server_grp', ).order_by('-id')
        company_name = self.request.GET.get('company_name', "").strip()  #
        company_id = self.request.GET.get('company_id', "").strip()
        deploy_way = self.request.GET.get('deploy_way', "").strip()
        industry = self.request.GET.get('industry', '').strip()

        if company_name:  # 公司名称查询
            queryset = queryset.filter(company_info__company_name=company_name)
        if company_id:  # 企业ID查询
            queryset = queryset.filter(station_info__company_id=company_id)
        if deploy_way:  # 部署方式查询
            queryset = queryset.filter(station_info__deploy_way=deploy_way)
        if industry:  # 行业查询
            queryset = queryset.filter(company_info__industry=industry)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 验证当天是否更新过数据
        is_update = 1 if InquiriesData.objects.all().filter(date=datetime.date.today()) else 0

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for item in serializer.data:
                inq_queryset = InquiriesData.objects.all().filter(company_id=item['company_id'])
                channel_dict = {}
                if inq_queryset:
                    # 取该公司开始有咨询量的日期
                    inq_ret = inq_queryset.aggregate(start_date=Min('date'))
                    # 取该公司的各渠道总咨询量
                    channel_set = inq_queryset.values('channel').annotate(value=Sum('inquires_num')). \
                        values_list('channel', 'value')
                    channel_dict = dict(channel_set)

                # 将各渠道咨询量插入
                for each in dict(CHANNEL_TYPES).keys():
                    if each in channel_dict.keys():
                        item.update({dict(CHANNEL_TYPES)[each]: channel_dict[each]})
                    else:
                        item.update({dict(CHANNEL_TYPES)[each]: 0})

                if inq_queryset:
                    # 将总咨询量插入
                    item.update({'sum_inquiries': sum(channel_dict.values())})
                    # 将平均咨询量插入
                    days = (datetime.date.today() - inq_ret['start_date']).days + is_update
                    item.update({'avg_inquiries': item['sum_inquiries'] / days})

                else:
                    item.update({'sum_inquiries': 0, 'avg_inquiries': 0})

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 线上站点情况
class OnlineClientDataViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = OnlineClientData.objects.all().order_by('-id')
    serializer_class = OnlineClientSerializer

    def check_permissions(self, request):
        if not request.user.has_perm("data_manage.view_prod-oper-data"):
            self.permission_denied(request)

    def handle_online_consumer_industry(self, request):
        queryset = OnlineClientData.objects.all()
        deploy_way = request.GET.get('deploy_way', 0)
        deploy_way = int(deploy_way)
        date = request.GET.get('date', None).strip()

        params = dict()
        if date:
            params['date'] = date
        if deploy_way:
            params['deploy_way'] = deploy_way
            deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]
        else:
            deploy_way_name = '所有'

        queryset = queryset.filter(**params)
        ret = queryset.aggregate(total=Sum('online_num'))
        ret_set = queryset.extra(select={'name': 'industry'}).defer('industry').values(
            'name').annotate(
            value=Sum('online_num'))
        online_dict = dict(list(ret_set.values_list('name', 'value')))
        ret_set = list(ret_set.values('name', 'value'))

        for each in list(Industry.objects.all().values_list('industry', flat=True)):
            if each not in online_dict.keys():
                ret_set.append({'name': each, 'value': 0})
        ret['data'] = ret_set
        return ret, deploy_way_name

    @list_route(methods=['get'])
    def online_consumer_industry(self, request):
        ret, deploy_way_name = self.handle_online_consumer_industry(request)
        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def industry_csv(self, request):
        date_ = request.GET.get("date", None)
        ret, deploy_way_name = self.handle_online_consumer_industry(request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=industry.csv'
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow([f"各行业{date_}站点数量情况"])
        writer.writerow([f"部署方式: {deploy_way_name}"])
        writer.writerow(["行业", "数量(位)", "占比"])
        for each in ret['data']:
            if ret['total']:
                each["占比"] = '%.2f%%' % (each["value"] / ret['total'] * 100)
            else:
                each["占比"] = 0
            writer.writerow(each.values())
        return response

    def handle_online_consumer_deploy(self, request):
        queryset = OnlineClientData.objects.all()
        industry = request.GET.get('industry', 0)
        industry = int(industry)
        date = request.GET.get('date', None).strip()
        params = {}
        if date:
            params['date'] = date
        if industry:
            industry_name = Industry.objects.all().get(pk=industry)
            params['industry'] = industry_name
        else:
            industry_name = '所有'

        queryset = queryset.filter(**params)
        ret = queryset.aggregate(total=Sum('online_num'))
        ret_set = list(queryset.extra(select={'name': 'deploy_way'}).defer('deploy_way').values(
            'name').annotate(value=Sum('online_num')).values('name', 'value'))

        online_list = []
        for iter in ret_set:
            iter['name'] = dict(DEPLOY_WAYS)[iter['name']]
            online_list.append(iter['name'])

        for each in dict(DEPLOY_WAYS).values():
            if each not in online_list:
                ret_set.append({'name': each, 'value': 0})

        ret['data'] = ret_set
        return ret, industry_name

    @list_route(methods=['get'])
    def online_consumer_deploy(self, request):
        ret, industry_name = self.handle_online_consumer_deploy(request)
        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def deploy_way_csv(self, request):
        date_ = request.GET.get("date", None)
        ret, industry_name = self.handle_online_consumer_deploy(request)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=deploy_way.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"各部署方式{date_}站点数量情况"])
        writer.writerow([f"行业: {industry_name}"])
        writer.writerow(["部署方式", "数量(位)", "占比"])
        for each in ret['data']:
            if ret['total']:
                each["占比"] = '%.2f%%' % (each["value"] / ret['total'] * 100)
            else:
                each["占比"] = 0
            writer.writerow(each.values())
        return response

    def handle_online_consumer_allday(self, request):
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())

        idpy_list = request.GET.getlist('idpy')
        ret_list = []

        for item in idpy_list:
            industry, deploy_way = item.split('|')
            industry, deploy_way = int(industry), int(deploy_way)
            idpy_dict = {'date__lte': end_date, 'date__gte': start_date}
            if deploy_way:
                idpy_dict['deploy_way'] = deploy_way
                deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]
            if industry:
                industry_name = Industry.objects.all().get(pk=industry).industry
                idpy_dict['industry'] = industry_name

            # 取有咨询量的日期的数据
            set_dict = {}
            inq_set = OnlineClientData.objects.all().filter(**idpy_dict).values('date').annotate(
                value=Sum('online_num')).values_list('date', 'value')
            for it in inq_set:
                set_dict.update({it[0]: it[1]})

            # 补齐没有咨询量的日期的数据
            que_date = {}
            for day in dates_during(start_date, end_date):
                if day not in set_dict.keys():
                    que_date.update({day: 0})
                else:
                    que_date.update({day: set_dict[day]})

            if industry and deploy_way:
                ret_name = industry_name + '|' + deploy_way_name
            elif industry and not deploy_way:
                ret_name = industry_name
            elif deploy_way and not industry:
                ret_name = deploy_way_name

            ret_list.append({'name': ret_name, 'data': que_date.values()})

        ret = {'data': list(ret_list)}
        return ret

    @list_route(methods=['get'])
    def online_consumer_allday(self, request):
        ret = self.handle_online_consumer_allday(request)
        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def trend_csv(self, request):
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        ret = self.handle_online_consumer_allday(request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=trend.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"{start_date}-{end_date}站点数量变化趋势"])

        whole_days = ['指数']
        for day in dates_during(str_to_date(start_date), str_to_date(end_date)):
            whole_days.append(date_to_str(day))

        writer.writerow(whole_days)
        for each in ret['data']:
            each_data = [each['name']]
            each_data.extend(each['data'])
            writer.writerow(each_data)

        return response


# 线上渠道情况
class ChannelInquiriesViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = InquiriesData.objects.all().order_by('-id')
    serializer_class = InquiriesDataSerializer

    def check_permissions(self, request):
        if not request.user.has_perm("data_manage.view_prod-oper-data"):
            self.permission_denied(request)

    def handle_channel_inquirise(self, request):
        queryset = InquiriesData.objects.all()
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())
        industry = int(request.GET.get('industry', 0))
        deploy_way = int(request.GET.get('deploy_way', 0))
        company_id = request.GET.get('company_id', '').strip()
        params = {}
        industry_name = ''
        deploy_way_name = ''

        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date
        if company_id:
            company = OpenStationManage.objects.all().filter(
                station_info__company_id=company_id)
            if company:
                company_name = company.first().company_info.company_name
                params['company_id'] = company_id
            else:
                raise ValueError('company_id')
        else:
            if industry:
                industry_name = Industry.objects.get(id=industry).industry
                params['industry'] = industry_name
            if deploy_way:
                params['deploy_way'] = deploy_way
                deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]

        queryset = queryset.filter(**params)
        ret = queryset.aggregate(total=Sum('inquires_num'))
        ret_set = queryset.extra(select={'name': 'channel'}).defer('channel') \
            .values('name').annotate(value=Sum('inquires_num')).values('name', 'value')
        ret_set = list(ret_set)

        online_list = []
        for item in ret_set:
            if item['name'] in dict(CHANNEL_CHOICES).keys():
                item['name'] = dict(CHANNEL_CHOICES)[item['name']]
            else:
                item['name'] = '未知渠道' + str(item['name'])
            online_list.append(item['name'])

        for each in dict(CHANNEL_CHOICES).values():
            if each not in online_list:
                ret_set.append({'name': each, 'value': 0})

        ret['data'] = ret_set
        if company_id:
            ret['company_name'] = company_name
        return ret, company_id, industry_name, deploy_way_name,

    @list_route(methods=['get'])
    def get_channel_inquiries(self, request):
        try:
            ret, company_id, industry_name, deploy_way_name = self.handle_channel_inquirise(request)
        except ValueError as e:
            if e.args[0] == 'company_id':
                return Response({'error': '该公司不存在'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def csv_channel_inquiries(self, request):
        start_date = request.GET.get('start_date', None).strip()
        end_date = request.GET.get('end_date', None).strip()

        try:
            ret, company_id, industry_name, deploy_way_name = self.handle_channel_inquirise(request)
        except ValueError as e:
            if e.args[0] == 'company_id':
                return Response({'error': '该公司不存在'}, status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponse(content_type='text/csv')
        if company_id:
            response['Content-Disposition'] = 'attachment; filename=single_customer_channel.csv'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)
            company_name = ret['company_name']
            writer.writerow([f"{company_name}"])
            writer.writerow([f"{start_date}-{end_date}渠道咨询量情况"])
        else:
            response['Content-Disposition'] = 'attachment; filename=industry_deploy_channel.csv'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)
            if deploy_way_name and industry_name:
                writer.writerow([f"行业:{industry_name}     部署方式:{deploy_way_name}"])
            elif deploy_way_name and (not industry_name):
                writer.writerow([f"行业:所有     部署方式:{deploy_way_name}"])
            elif (not deploy_way_name) and industry_name:
                writer.writerow([f"行业:{industry_name}     部署方式:所有"])
            else:
                writer.writerow([f"行业:所有     部署方式:所有"])

            writer.writerow([f"{start_date}--{end_date}渠道咨询量情况"])

        writer.writerow(["渠道名称", "访问量(次)", "占比"])
        for each in ret['data']:
            if ret['total']:
                each.update({"proportion": '%.2f%%' % (each["value"] / ret['total'] * 100)})
            else:
                each.update({"proportion": '0'})

            writer.writerow(each.values())

        return response

    def handle_channel_allday(self, request):
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())
        idpych_list = request.GET.getlist('idpych')
        ret_list = []

        if not (start_date and end_date):
            raise ValueError(1)

        for item in idpych_list:
            industry, deploy_way, channel = item.split('|')
            industry, deploy_way, channel = int(industry), int(deploy_way), int(channel)

            idpych_dict = {'date__lte': end_date, 'date__gte': start_date}
            if deploy_way:
                idpych_dict['deploy_way'] = deploy_way
                deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]
            if industry:
                industry_name = Industry.objects.all().get(pk=industry).industry
                idpych_dict['industry'] = industry_name

            channel_name = dict(CHANNEL_CHOICES)[channel]
            idpych_dict['channel'] = channel

            # 取有咨询量的日期的数据
            set_dict = {}
            inq_set = InquiriesData.objects.all().filter(**idpych_dict).values('date').annotate(
                value=Sum('inquires_num')).values_list('date', 'value')
            for it in inq_set:
                set_dict.update({it[0]: it[1]})

            # 补齐没有咨询量的日期的数据
            que_date = {}
            for day in dates_during(start_date, end_date):
                if day not in set_dict.keys():
                    que_date.update({day: 0})
                else:
                    que_date.update({day: set_dict[day]})

            if industry and deploy_way:
                ret_name = industry_name + '|' + deploy_way_name + '|' + channel_name
            elif industry and not deploy_way:
                ret_name = industry_name + '|' + channel_name
            elif deploy_way and not industry:
                ret_name = deploy_way_name + '|' + channel_name
            else:
                ret_name = channel_name

            ret_list.append({'name': ret_name, 'data': que_date.values()})

        ret = {'data': list(ret_list)}
        return ret

    @list_route(methods=['get'])
    def get_channel_allday(self, request):
        try:
            ret = self.handle_channel_allday(request)
        except ValueError as e:
            if e.args[0] == 1:
                return Response({"error": "日期错误"}, status=status.HTTP_200_OK)

        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def csv_channel_allday(self, request):
        start_date = request.GET.get('start_date', None).strip()
        end_date = request.GET.get('end_date', None).strip()
        try:
            ret = self.handle_channel_allday(request)
        except ValueError as e:
            if e.args[0] == 1:
                return Response({"error": "日期错误"}, status=status.HTTP_200_OK)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=channel_inquiries_trend.csv'

        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"{start_date}至{end_date}渠道咨询量变化趋势"])
        whole_days = ['指数']
        for day in dates_during(str_to_date(start_date), str_to_date(end_date)):
            whole_days.append(date_to_str(day))

        writer.writerow(whole_days)
        for each in ret['data']:
            each_data = [each['name']]
            each_data.extend(each['data'])
            writer.writerow(each_data)
        return response


# 客户使用情况
class CustomerUseViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = InquiriesData.objects.all().order_by('-id')
    serializer_class = InquiriesDataSerializer

    def check_permissions(self, request):
        if not request.user.has_perm("data_manage.view_prod-oper-data"):
            self.permission_denied(request)

    def handle_customer_inquiries(self, request):
        queryset = InquiriesData.objects.all()
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())
        industry = request.GET.get("industry", None)
        deploy_way = request.GET.get("deploy_way", None)
        industry_name = ''
        deploy_way_name = ''

        params = {}
        whole_list = []  # 全部行业名或全部部署方式名

        if (industry is None and deploy_way is None) or \
                (industry is not None and deploy_way is not None):
            raise ValueError(1)
        elif industry is None and deploy_way is not None:  # 行业客户咨询量
            whole_list = Industry.objects.all().values_list('industry', flat=True)

            if int(deploy_way) != 0:
                params['deploy_way'] = deploy_way
                deploy_way_name = dict(DEPLOY_WAYS)[int(deploy_way)]
            else:
                deploy_way_name = '所有'

            queryset = queryset.extra(select={'name': 'industry'}).defer('industry')
        else:  # 部署方式客户咨询量
            whole_list = dict(DEPLOY_WAYS).values()
            if int(industry) != 0:
                industry_name = Industry.objects.all().get(id=int(industry)).industry
                params['industry'] = industry_name
            else:
                industry_name = '所有'
            queryset = queryset.extra(select={'name': 'deploy_way'}).defer('deploy_way')

        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date

        queryset = queryset.filter(**params)
        ret = queryset.aggregate(total=Sum('inquires_num'))
        ret_set = list(queryset.values('name').annotate(
            value=Sum('inquires_num')).values('name', 'value'))

        online_list = []
        for item in ret_set:
            if industry is not None and deploy_way is None:
                item['name'] = dict(DEPLOY_WAYS)[item['name']]
            online_list.append(item['name'])

        # 补齐没有咨询量的行业或部署方式
        for each in whole_list:
            if each not in online_list:
                ret_set.append({'name': each, 'value': 0})

        ret['data'] = ret_set
        return ret, industry_name, deploy_way_name

    # 行业客户咨询量及占比；部署方式客户咨询量及占比
    @list_route(methods=['get'])
    def get_customer_inquiries(self, request):
        try:
            ret, industry_name, deploy_way_name = self.handle_customer_inquiries(request)
        except ValueError as e:
            if e.args[0] == 1:
                return Response({'error': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ret, status=status.HTTP_200_OK)

    # 导出 行业客户咨询量及占比；部署方式客户咨询量及占比
    @list_route(methods=['get'])
    def csv_customer_inquiries(self, request):
        response = HttpResponse(content_type='text/csv')
        start_date = request.GET.get('start_date', None).strip()
        end_date = request.GET.get('end_date', None).strip()
        try:
            ret, industry_name, deploy_way_name = self.handle_customer_inquiries(request)
        except ValueError as e:
            if e.args[0] == 1:
                return Response({'error': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        if industry_name:
            response['Content-Disposition'] = 'attachment; filename=customer_deploy_inquiries.csv'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)
            writer.writerow([f"各部署方式{start_date}至{end_date}客户咨询量及占比"])
            writer.writerow([f"行业: {industry_name}"])
            writer.writerow(['部署方式', '数量', '占比'])

        if deploy_way_name:
            response['Content-Disposition'] = 'attachment; filename=customer_industry_inquiries.csv'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)
            writer.writerow([f"各行业{start_date}至{end_date}客户咨询量及占比"])
            writer.writerow([f"部署方式: {deploy_way_name}"])
            writer.writerow(['行业', '数量', '占比'])

        for each in ret['data']:
            if ret['total']:
                each.update({'proportion': '%.2f%%' % (each['value'] / ret['total'] * 100)})
            else:
                each.update({'proportion': 0})

            writer.writerow(each.values())

        return response

    # 具体客户咨询量情况
    @list_route(methods=['get'])
    def get_single_company(self, request):
        queryset = InquiriesData.objects.all().order_by('-id')
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())
        company_id = request.GET.get('company_id', '').strip()

        company = OpenStationManage.objects.all().filter(station_info__company_id=company_id)
        if company:
            company_serializer = PandectDataSerializer(company.first())
            company_data = company_serializer.data

        else:
            return Response({'error': '该公司不存在'}, status=status.HTTP_200_OK)
        params = {}

        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date
        params['company_id'] = company_id

        queryset = queryset.filter(**params)
        ret = queryset.aggregate(total=Sum('inquires_num'))

        if ret['total']:
            valid_days = end_date - start_date
            ret['avg'] = int(ret['total']) / (valid_days.days + 1)

        else:
            ret['avg'] = 0
            ret['total'] = 0

        ret['start_date'] = date_to_str(start_date)
        ret['end_date'] = date_to_str(end_date)
        ret['company_name'] = company_data['company_name']
        ret['all_total'] = company_data['sum_inquiries']
        ret['industry'] = company_data['industry']
        ret['deploy_way'] = company_data['deploy_way']
        ret['all_avg'] = company_data['avg_inquiries']
        ret['company_id'] = company_id
        return Response(ret, status=status.HTTP_200_OK)

    def handle_customer_allday(self, request):
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())

        idpy_list = request.GET.getlist('idpy')
        ret_list = []

        if not (start_date and end_date):
            return Response({'error': "日期有误"}, status=status.HTTP_400_BAD_REQUEST)

        for item in idpy_list:
            industry, deploy_way = item.split('|')
            industry, deploy_way = int(industry), int(deploy_way)

            idpy_dict = {'date__lte': end_date, 'date__gte': start_date}
            if deploy_way:
                idpy_dict['deploy_way'] = deploy_way
                deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]
            if industry:
                industry_name = Industry.objects.all().get(pk=industry).industry
                idpy_dict['industry'] = industry_name

            set_dict = {}
            inq_set = InquiriesData.objects.all().filter(**idpy_dict).values('date').annotate(
                value=Sum('inquires_num')).values_list('date', 'value')
            for it in inq_set:
                set_dict.update({it[0]: it[1]})

            # 补齐没有咨询量的日期的数据
            que_date = {}
            for day in dates_during(start_date, end_date):
                if day not in set_dict.keys():
                    que_date.update({day: 0})
                else:
                    que_date.update({day: set_dict[day]})

            if industry and deploy_way:
                ret_name = industry_name + '|' + deploy_way_name
            elif industry and not deploy_way:
                ret_name = industry_name
            elif deploy_way and not industry:
                ret_name = deploy_way_name

            ret_list.append({'name': ret_name, 'data': que_date.values()})

        ret = {'data': list(ret_list)}
        return ret

    # 咨询量变化趋势
    @list_route(methods=['get'])
    def get_customer_allday(self, request):
        ret = self.handle_customer_allday(request)
        return Response(ret, status=status.HTTP_200_OK)

    # 导出 咨询量变化趋势
    @list_route(methods=['get'])
    def csv_customer_allday(self, request):
        start_date = request.GET.get('start_date', '').strip()
        end_date = request.GET.get('end_date', '').strip()
        ret = self.handle_customer_allday(request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=customer_inquiries_trend.csv'

        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"{start_date}至{end_date}咨询量变化趋势"])
        whole_days = ['指数']
        for day in dates_during(str_to_date(start_date), str_to_date(end_date)):
            whole_days.append(date_to_str(day))

        writer.writerow(whole_days)
        for each in ret['data']:
            each_data = [each['name']]
            each_data.extend(each['data'])
            writer.writerow(each_data)
        return response


@api_view(['GET'])
def channellist(request):
    fields = ['id', 'name']
    ret = {'data': []}
    for item in CHANNEL_CHOICES:
        ret['data'].append(dict(zip(fields, item)))
    return Response(ret, status=status.HTTP_200_OK)


class OnlineProductViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = OnlineProductData.objects.all().order_by('-id')
    serializer_class = OnlineProductSerializer

    def check_permissions(self, request):
        if not request.user.has_perm("data_manage.view_prod-oper-data"):
            self.permission_denied(request)

    def handle_day_product(self, request):
        industry = int(request.GET.get('industry', 0))
        date = str_to_date(request.GET.get('date', None).strip())
        deploy_way = int(request.GET.get('deploy_way', 0))
        deploy_way_name = ''
        industry_name = ''
        params = {'date': date}

        if industry:
            industry_name = Industry.objects.get(pk=industry).industry
            params['industry'] = industry_name

        if deploy_way:
            deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]
            params['deploy_way'] = deploy_way

        queryset = OnlineProductData.objects.all().filter(**params)
        ret = queryset.aggregate(total=Sum('online_num'))
        ret_set = list(queryset.extra(select={'name': 'product_id'}).defer('prodcut_id').values('name'). \
                       annotate(value=Sum('online_num')).values('name', 'value'))

        whole_list = Product.objects.all().values_list('product', flat=True)
        online_list = []

        for item in ret_set:
            item['name'] = whole_list.get(pk=item['name'])
            online_list.append(item['name'])
        for each in whole_list:
            if each not in online_list:
                ret_set.append({'name': each, 'value': 0})

        ret['data'] = ret_set
        return ret, industry_name, deploy_way_name

    # 单日线上产品情况
    @list_route(methods=['get'])
    def get_day_product(self, request):
        ret, industry_name, deploy_way_name = self.handle_day_product(request)
        return Response(ret, status=status.HTTP_200_OK)

    # 导出 单日线上产品情况
    @list_route(methods=['get'])
    def csv_day_product(self, request):
        date_ = request.GET.get('date', '').strip()
        ret, industry_name, deploy_way_name = self.handle_day_product(request)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=online_product_day.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        if deploy_way_name and industry_name:
            writer.writerow([f"行业:{industry_name}     部署方式{deploy_way_name}"])
        elif deploy_way_name and (not industry_name):
            writer.writerow([f"行业:所有     部署方式{deploy_way_name}"])
        elif (not deploy_way_name) and industry_name:
            writer.writerow([f"行业:{industry_name}     部署方式:所有"])
        else:
            writer.writerow([f"行业:所有     部署方式:所有"])

        writer.writerow([f"{date_}线上产品数量情况"])
        writer.writerow(['产品', '数量', '占比'])

        for each in ret['data']:
            if ret['total']:
                each.update({'proportion': '%.2f%%' % (each['value'] / ret['total'] * 100)})
            else:
                each.update({'proportion': 0})

            writer.writerow(each.values())

        return response

    def handle_product_allday(self, request):
        start_date = str_to_date(request.GET.get('start_date', '').strip())
        end_date = str_to_date(request.GET.get('end_date', '').strip())

        idpypd_list = request.GET.getlist('idpypd')
        ret_list = []

        if not (start_date and end_date):
            return Response({'error': "日期有误"}, status=status.HTTP_400_BAD_REQUEST)

        for item in idpypd_list:
            industry, deploy_way, product_id = item.split('|')
            industry, deploy_way, product_id = int(industry), int(deploy_way), int(product_id)

            idpypd_dict = {'date__lte': end_date, 'date__gte': start_date}
            if deploy_way:
                idpypd_dict['deploy_way'] = deploy_way
                deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]
            if industry:
                industry_name = Industry.objects.all().get(pk=industry).industry
                idpypd_dict['industry'] = industry_name

            idpypd_dict['product_id'] = product_id
            product_name = Product.objects.all().get(pk=product_id).product

            set_dict = {}
            inq_set = OnlineProductData.objects.all().filter(**idpypd_dict).values('date').annotate(
                value=Sum('online_num')).values_list('date', 'value')
            for it in inq_set:
                set_dict.update({it[0]: it[1]})

            # 补齐没有咨询量的日期的数据
            que_date = {}
            for day in dates_during(start_date, end_date):
                if day not in set_dict.keys():
                    que_date.update({day: 0})
                else:
                    que_date.update({day: set_dict[day]})

            if industry and deploy_way:
                ret_name = industry_name + '|' + deploy_way_name + '|' + product_name
            elif industry and not deploy_way:
                ret_name = industry_name + '|' + product_name
            elif deploy_way and not industry:
                ret_name = deploy_way_name + '|' + product_name
            else:
                ret_name = product_name

            ret_list.append({'name': ret_name, 'data': que_date.values()})

        ret = {'data': list(ret_list)}
        return ret

    # 线上产品数量变化趋势
    @list_route(methods=['get'])
    def get_product_allday(self, request):
        ret = self.handle_product_allday(request)
        return Response(ret, status=status.HTTP_200_OK)

    # 导出 线上产品数量变化趋势
    @list_route(methods=['get'])
    def csv_product_allday(self, request):
        start_date = request.GET.get('start_date', '').strip()
        end_date = request.GET.get('end_date', '').strip()
        ret = self.handle_product_allday(request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=online_product_trend.csv'

        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"{start_date}至{end_date}咨询量变化趋势"])
        whole_days = ['指数']
        for day in dates_during(str_to_date(start_date), str_to_date(end_date)):
            whole_days.append(date_to_str(day))

        writer.writerow(whole_days)
        for each in ret['data']:
            each_data = [each['name']]
            each_data.extend(each['data'])
            writer.writerow(each_data)
        return response


class SiteOperViewSet(GenericViewSet):
    queryset = OperatingRecord.objects.all().order_by('-id')

    def check_permissions(self, request):
        if not request.user.has_perm("data_manage.view_prod-oper-data"):
            self.permission_denied(request)

    def handle_site_oper(self, request):
        queryset = OperatingRecord.objects.all().order_by('-id')
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())
        industry = int(request.GET.get('industry', 0))
        deploy_way = int(request.GET.get('deploy_way', 0))
        params = {}
        industry_name = ''
        deploy_way_name = ''

        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date

        if industry:
            industry_name = Industry.objects.get(id=industry).industry
            params['industry'] = industry_name
        if deploy_way:
            params['deploy_way'] = deploy_way
            deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]

        queryset = queryset.filter(**params)
        ret = queryset.aggregate(total=Sum('num'))
        online_set = queryset.extra(select={'name': 'action'}).defer('action') \
            .values('name').annotate(value=Sum('num')).values('name', 'value')
        online_set = list(online_set)

        ret_dict = {}
        for item in online_set:
            if item['name'] in dict(OPERATE_ACTION_CHOICES).keys():
                item['name'] = dict(OPERATE_ACTION_CHOICES)[item['name']]
            else:
                item = '未知运营方式' + str(item)
            ret_dict.update({item['name']: item['value']})

        for each in dict(OPERATE_ACTION_CHOICES).values():
            if each not in ret_dict.keys():
                ret_dict.update({each: 0})
                online_set.append({'name': each, 'value': 0})

        return ret, ret_dict, online_set, industry_name, deploy_way_name

    @list_route(methods=['get'])
    def get_site_oper(self, request):
        ret, ret_set, _, _, _ = self.handle_site_oper(request)
        ret['name'] = list(ret_set.keys())
        ret['data'] = list(ret_set.values())
        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def csv_site_oper(self, request):
        start_date = request.GET.get('start_date', None).strip()
        end_date = request.GET.get('end_date', None).strip()

        ret, _, online_set, industry_name, deploy_way_name = self.handle_site_oper(request)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=site_oper_type.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        if deploy_way_name and industry_name:
            writer.writerow([f"行业:{industry_name}     部署方式{deploy_way_name}"])
        elif deploy_way_name and (not industry_name):
            writer.writerow([f"行业:所有     部署方式{deploy_way_name}"])
        elif (not deploy_way_name) and industry_name:
            writer.writerow([f"行业:{industry_name}     部署方式:所有"])
        else:
            writer.writerow([f"行业:所有     部署方式:所有"])

        writer.writerow([f"{start_date}至{end_date}站点运营情况"])
        writer.writerow(['站点运营类型', '数量', '占比'])

        for each in online_set:
            if ret['total']:
                each.update({'proportion': '%.2f%%' % (each['value'] / ret['total'] * 100)})
            else:
                each.update({'proportion': 0})

            writer.writerow(each.values())

        return response

    def handle_site_oper_allday(self, request):
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())
        idpyop_list = request.GET.getlist('idpyop')
        ret_list = []

        if not (start_date and end_date):
            raise ValueError(1)

        for item in idpyop_list:
            industry, deploy_way, oper = item.split('|')
            industry, deploy_way, oper = int(industry), int(deploy_way), int(oper)

            idpyop_dict = {'date__lte': end_date, 'date__gte': start_date}
            if deploy_way:
                idpyop_dict['deploy_way'] = deploy_way
                deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]
            if industry:
                industry_name = Industry.objects.all().get(pk=industry).industry
                idpyop_dict['industry'] = industry_name

            oper_name = dict(OPERATE_ACTION_CHOICES)[oper]
            idpyop_dict['action'] = oper

            # 取有咨询量的日期的数据
            oper_dict = {}
            oper_set = OperatingRecord.objects.all().filter(**idpyop_dict).values('date').annotate(
                value=Sum('num')).values_list('date', 'value')

            oper_dict = dict(oper_set)

            # 补齐没有咨询量的日期的数据
            ret_dict = {}
            for day in dates_during(start_date, end_date):
                if day not in oper_dict.keys():
                    ret_dict.update({day: 0})
                else:
                    ret_dict.update({day: oper_dict[day]})

            if industry and deploy_way:
                ret_name = industry_name + '|' + deploy_way_name + '|' + oper_name
            elif industry and not deploy_way:
                ret_name = industry_name + '|' + oper_name
            elif deploy_way and not industry:
                ret_name = deploy_way_name + '|' + oper_name
            else:
                ret_name = oper_name

            ret_list.append({'name': ret_name, 'data': ret_dict.values()})

        ret = {'data': list(ret_list)}
        return ret

    @list_route(methods=['get'])
    def get_site_oper_allday(self, request):
        ret = self.handle_site_oper_allday(request)
        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def csv_site_oper_allday(self, request):
        start_date = request.GET.get('start_date', None).strip()
        end_date = request.GET.get('end_date', None).strip()

        ret = self.handle_site_oper_allday(request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=site_oper_trend.csv'

        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"{start_date}至{end_date}站点运营变化趋势"])
        whole_days = ['指数']
        for day in dates_during(str_to_date(start_date), str_to_date(end_date)):
            whole_days.append(date_to_str(day))

        writer.writerow(whole_days)
        for each in ret['data']:
            each_data = [each['name']]
            each_data.extend(each['data'])
            writer.writerow(each_data)
        return response


class GridInquiresView(GenericViewSet):
    """运维统计-节点情况入口"""
    queryset = InquiriesData.objects.all()

    def check_permissions(self, request):
        if not request.user.has_perm("data_manage.view_ops-data"):
            self.permission_denied(request)

    @staticmethod
    def get_params(request) -> dict:
        """筛选入参"""
        params = dict()
        deploy_way = request.GET.get("deploy_way", "")
        from_date = request.GET.get("from_date", "")
        to_date = request.GET.get("to_date", "")
        if from_date and to_date:
            params["date__gte"] = str_to_date(from_date)
            params["date__lte"] = str_to_date(to_date)
        if deploy_way != "":
            params["deploy_way"] = deploy_way
        return params

    def get_trend_params(self, request) -> dict:
        """趋势筛选入参"""
        params = dict()
        grid_id_list = request.GET.getlist("grid_id", "")
        if grid_id_list:
            grid_site_map = self.get_grid_site_map()
            company_ids = grid_site_map.keys()
            params["company_id__in"] = company_ids
        from_date = request.GET.get("from_date", "")
        to_date = request.GET.get("to_date", "")
        if from_date and to_date:
            params["date__gte"] = str_to_date(from_date)
            params["date__lte"] = str_to_date(to_date)
        return params

    def get_grid_site_map(self) -> dict:
        grid_list = self.request.GET.getlist("grid_id", [])
        ret = StationInfo.objects.filter(grid_id__in=grid_list) \
            .select_related("grid__grid_name") \
            .values_list("company_id", "grid__grid_name")
        return dict(ret)

    def get_inquires_data(self) -> list:
        """获取咨询量数据"""
        params = self.get_params(self.request)
        if params["deploy_way"] == "0":
            params.pop("deploy_way")
        query_set = InquiriesData.objects.filter(**params)
        company_ids = query_set.values_list("company_id", flat=True)
        inquires = query_set.values("company_id").annotate(num=Sum("inquires_num")).values_list("company_id", "num")
        grid_company_ship = dict(
            StationInfo.objects.filter(company_id__in=company_ids).select_related("grid__grid_name").values_list(
                "company_id", "grid__grid_name")
        )
        result = {}
        total = 0
        for company_id, inquires_num in inquires:
            result.setdefault(grid_company_ship[company_id], 0)
            result[grid_company_ship[company_id]] += inquires_num
            total += inquires_num

        if "deploy_way" in params.keys():
            all_grid = Grid.objects.all().filter(deploy_way__in=params["deploy_way"]).values_list("grid_name",
                                                                                                  flat=True)
        else:
            all_grid = Grid.objects.all().values_list("grid_name", flat=True)
        for each in all_grid:
            if each not in result.keys():
                result[each] = 0
        return [{"name": k, "value": v} for (k, v) in result.items()]

    def get_inquires_trend_data(self) -> dict:
        params = self.get_trend_params(self.request)
        grid_id_list = self.request.GET.getlist("grid_id", "")
        query_set = InquiriesData.objects.filter(**params).values('company_id', 'date').annotate(
            value=Sum('inquires_num')).values_list('company_id', 'date', 'value')
        grid_site_map = self.get_grid_site_map()
        grid_name_map = dict(Grid.objects.all().filter(id__in=grid_id_list).values_list("id", "grid_name"))
        result = {}
        for company_id, date, num in query_set:
            grid_name = grid_site_map[company_id]
            result.setdefault(grid_name, {})
            result[grid_name].setdefault(date_to_str(date), 0)
            result[grid_name][date_to_str(date)] += num

        for grid_id in grid_id_list:
            grid_name = grid_name_map[int(grid_id)]
            if grid_name not in result.keys():
                result[grid_name] = {}

        dates = dates_during(params.get("date__gte"), params.get("date__lte"))
        for grid, data in result.items():
            for day in dates:
                if date_to_str(day) not in data.keys():
                    data[date_to_str(day)] = 0
            result[grid] = collections.OrderedDict(sorted(data.items(), key=lambda x: str_to_date(x[0])))
        return result

    @list_route(methods=['get'])
    def inquires(self, request):
        """获取咨询量"""
        data = self.get_inquires_data()
        total = 0
        for each in data:
            total += each["value"]

        return Response({
            "total": total,
            "data": data
        })

    @list_route(methods=['get'])
    def inquires_csv(self, request):
        """咨询量csv导出"""
        data = self.get_inquires_data()
        raw_data = [each.values() for each in data]
        total = 0
        for each in data:
            total += each["value"]

        deploy_way = request.GET.get("deploy_way", None)
        if deploy_way == "0":
            dp_str = "所有"
        elif deploy_way is not None:
            dp_str = dict(DEPLOY_WAYS)[int(deploy_way)]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=inquires.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"部署方式: {dp_str}"])
        writer.writerow([f"{request.GET.get('from_date')}至{request.GET.get('to_date')}各节点咨询量情况"])
        writer.writerow(["节点名称", "访问量（次）", "占比"])
        writer.writerows([(name, num, "%f%%" % (num / total * 100)) for (name, num) in raw_data])
        return response

    @list_route(methods=['get'])
    def inquires_trend(self, request):
        """咨询量趋势"""
        data = self.get_inquires_trend_data()
        result = []
        for grid_name, values in data.items():
            result.append({
                "name": grid_name,
                "data": values.values()
            })
        return Response(result)

    @list_route(methods=['get'])
    def inquires_trend_csv(self, request):
        """咨询量趋势csv导出"""
        data = self.get_inquires_trend_data()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=inquires_trend.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"{request.GET.get('from_date')}至{request.GET.get('to_date')}各节点咨询量趋势"])
        writer.writerow(["节点名称", "日期", "访问量（次）"])
        lines = []
        for grid_name, values in data.items():
            for date, num in values.items():
                lines.append((grid_name, date, num))
        writer.writerows(lines)
        return response


class SerGrpInquriesViewSet(GenericViewSet):
    queryset = InquiriesData.objects.all().order_by('-id')

    def check_permissions(self, request):
        if not request.user.has_perm("data_manage.view_ops-data"):
            self.permission_denied(request)

    @classmethod
    def under_grid(cls):
        queryset = InquiriesData.objects.all().order_by('-id')
        params = {}
        grp_grid_list = ServerGroup.objects.all().filter(grid_id__isnull=False).values_list('group_name', 'grid_id')

        grp_grid_map = {}
        for each in grp_grid_list:
            grp_grid_map.setdefault(each[1], [])
            grp_grid_map[each[1]].append(each[0])

        date = datetime.date.today() - datetime.timedelta(days=1)
        params.setdefault('date', date)

        ret = []

        # 获取各节点的访问量
        grp_num_set = queryset.filter(**params).values('server_grp').annotate(total=Sum('inquires_num')).values_list(
            'server_grp', 'total')
        grp_num_map = dict(grp_num_set)
        for grid in grp_grid_map.keys():
            grid_num = 0
            for grp in grp_grid_map[grid]:
                if grp in grp_num_map.keys():
                    grid_num += grp_num_map[grp]
            if grid_num <= 20000:
                ret.append(grid)
        return ret

    @classmethod
    def min_sergrp_inquries(cls, grid_id):
        queryset = InquiriesData.objects.all().order_by('-id')
        params = {}
        grp_name_list = ServerGroup.objects.all().filter(grid_id=grid_id). \
            values_list('group_name', flat=True)
        date = datetime.date.today() - datetime.timedelta(days=1)
        params.setdefault('date', date)
        params['server_grp__in'] = grp_name_list

        queryset = queryset.filter(**params)
        if queryset:
            # 获取访问量最小的服务组名和最小访问量
            grp_set = queryset.values('server_grp').annotate(total=Sum('inquires_num')).values_list(
                'server_grp', 'total')
            grp_dict = dict(grp_set)
            grp_name = min(grp_dict.items(), key=lambda x: x[1])[0]
        else:
            grp_name = random.choice(grp_name_list)
        return grp_name

    def handle_sergrp_inquries(self, request):
        queryset = InquiriesData.objects.all().order_by('-id')
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())
        grid_id = int(request.GET.get('grid', 0))
        deploy_way = int(request.GET.get('deploy_way', 0))
        params = {}
        deploy_way_name = ''
        grp_name_list = ServerGroup.objects.all().values_list('group_name', flat=True)

        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date

        if deploy_way:
            params['deploy_way'] = deploy_way
            deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]

        if grid_id:  # 若在页面上不选择节点，此处不过滤服务组名，本系统不存在服务组也会出现在结果里
            grp_name_list = grp_name_list.filter(grid_id=grid_id)
            params['server_grp__in'] = grp_name_list

        queryset = queryset.filter(**params)

        ret = queryset.aggregate(total=Sum('inquires_num'))
        ret.setdefault('data', [])

        online_set = queryset.extra(select={'name': 'server_grp'}).defer('server_grp') \
            .values('name').annotate(value=Sum('inquires_num')).values_list('name', 'value')
        online_dict = dict(online_set)
        ret_set = []

        for each in grp_name_list:
            if each not in online_dict.keys():
                ret_set.append({'name': each, 'value': 0})
            else:
                ret_set.append({'name': each, 'value': online_dict[each]})
        ret['data'] = ret_set

        return ret, grid_id, deploy_way_name

    @list_route(methods=['get'])
    def get_sergrp_inquries(self, request):
        ret, _, _, = self.handle_sergrp_inquries(request)

        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def csv_sergrp_inquries(self, request):
        start_date = request.GET.get('start_date', None).strip()
        end_date = request.GET.get('end_date', None).strip()

        ret, grid_id, deploy_way_name = self.handle_sergrp_inquries(request)
        grid_name = ''
        if grid_id:
            grid_name = Grid.objects.get(id=grid_id).grid_name
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=sergrp_inquries.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        if deploy_way_name and grid_name:
            writer.writerow([f"部署方式{deploy_way_name}    节点:{grid_name}"])
        elif deploy_way_name and (not grid_name):
            writer.writerow([f"部署方式{deploy_way_name}    节点:所有"])
        elif (not deploy_way_name) and grid_name:
            writer.writerow([f"部署方式:所有     节点:{grid_name}"])
        else:
            writer.writerow([f"部署方式:所有     节点:所有"])

        writer.writerow([f"{start_date}至{end_date}各服务组咨询量情况"])
        writer.writerow(['服务组名称', '数量', '占比'])

        for each in ret['data']:
            if ret['total']:
                each.update({'proportion': '%.2f%%' % (each['value'] / ret['total'] * 100)})
            else:
                each.update({'proportion': 0})

            writer.writerow(each.values())

        return response

    def handle_sergrp_inquries_allday(self, request):
        start_date = str_to_date(request.GET.get('start_date', None).strip())
        end_date = str_to_date(request.GET.get('end_date', None).strip())
        dpgdgp_list = request.GET.getlist('dpgdgp')
        ret_list = []

        if not (start_date and end_date):
            raise ValueError(1)

        for item in dpgdgp_list:
            deploy_way, grid, ser_grp = item.split('|')
            deploy_way, grid, ser_grp = int(deploy_way), int(grid), int(ser_grp)

            dpgdgp_dict = {'date__lte': end_date, 'date__gte': start_date}
            # 添加过滤参数中的部署方式，并取部署方式名
            dpgdgp_dict['deploy_way'] = deploy_way
            deploy_way_name = dict(DEPLOY_WAYS)[deploy_way]
            # 取节点的名字
            grid_name = Grid.objects.all().get(pk=grid).grid_name
            # 取过滤条件中的服务组名，并添加至过滤参数中
            ser_grp_name = ServerGroup.objects.all().get(pk=ser_grp).group_name
            dpgdgp_dict['server_grp'] = ser_grp_name

            # 取有咨询量的日期的数据
            inq_dict = {}
            inq_set = InquiriesData.objects.all().filter(**dpgdgp_dict).values('date').annotate(
                value=Sum('inquires_num')).values_list('date', 'value')

            inq_dict = dict(inq_set)

            # 补齐没有咨询量的日期的数据
            ret_dict = {}
            for day in dates_during(start_date, end_date):
                if day not in inq_dict.keys():
                    ret_dict.update({day: 0})
                else:
                    ret_dict.update({day: inq_dict[day]})

            ret_name = deploy_way_name + '|' + grid_name + '|' + ser_grp_name

            ret_list.append({'name': ret_name, 'data': ret_dict.values()})

        ret = {'data': list(ret_list)}
        return ret

    @list_route(methods=['get'])
    def get_sergrp_inquries_allday(self, request):
        ret = self.handle_sergrp_inquries_allday(request)
        return Response(ret, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def csv_sergrp_inquries_allday(self, request):
        start_date = request.GET.get('start_date', None).strip()
        end_date = request.GET.get('end_date', None).strip()

        ret = self.handle_sergrp_inquries_allday(request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=sergrp_inquries_trend.csv'

        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"{start_date}至{end_date}服务组咨询量变化趋势"])
        whole_days = ['指数']
        for day in dates_during(str_to_date(start_date), str_to_date(end_date)):
            whole_days.append(date_to_str(day))

        writer.writerow(whole_days)
        for each in ret['data']:
            each_data = [each['name']]
            each_data.extend(each['data'])
            writer.writerow(each_data)
        return response
