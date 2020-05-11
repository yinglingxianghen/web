from collections import OrderedDict

import xlrd
import xlwt
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse
from io import BytesIO
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from applications.data_manage.views import SerGrpInquriesViewSet
from applications.log_manage.models import OperateLog
from applications.production_manage.models import Product, VersionInfo, FunctionInfo, SingleSelection, Server, \
    SerType, ServerGroup, Grid, DataBaseInfo, SerAddress, SerIp
from applications.production_manage.serializers import ProductSerializer, VersionInfoSerializer, \
    SingleSelectionSerializer, ServerSerializer, SerTypeSerializer, \
    GroupSerializer, GridSerializer, DataBaseInfoSerializer, SerAddressSerializer, \
    SimpGroupSerializer, SimpProductSerializer, SimpGridSerializer, ForGroupSerTypeSerializer, \
    SerIpSerializer, ForDateProductSerializer, ForShipGridSerializer, SimpVersionInfoSerializer, \
    ForDetailFunctionSerializer, ForOpenProductSerializer, FunctionInfoSerializer
from ldap_server.configs import DEPLOY_WAYS, CLI_CHOICES, CLI_UNLIMITED, REFACTOR_VERSION, CLASSIC_VERSION, \
    PROD_SERV_VERSIONS
from libs.database import mysql_test
from libs.hash import decrypt, encrypt


# 经典版 产品
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().filter(classify=CLASSIC_VERSION).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'forgrid':
            return ProductSerializer
        elif self.action == 'foropen':
            return SimpProductSerializer
        elif self.action == 'fordata':
            return ForDateProductSerializer
        elif self.action == 'for_open_func':
            return ForOpenProductSerializer
        elif self.suffix == 'List' and self.request.method == 'GET':
            return SimpProductSerializer
        else:
            return ProductSerializer

    @list_route(methods=['get'])
    def forgrid(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(ProductViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def foropen(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(ProductViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def fordata(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(ProductViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        # 产品中search
        queryset = Product.objects.all().filter(classify=CLASSIC_VERSION).order_by('-id')
        # .prefetch_related('version__function__dependences__function', 'version__function__parent' \
        #                   , 'version__function__selection', 'version__function__selection__childfunc') \
        product = self.request.GET.get('product_name', "").strip()  # 获取单个产品
        products = self.request.GET.getlist('product', [])  # 开站时，取功能列表，需传入多个产品ID
        if product:
            queryset = queryset.filter(product=product)
        if products:
            queryset = queryset.filter(id__in=products)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        data['classify'] = CLASSIC_VERSION
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(ForDateProductSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data
        data['classify'] = CLASSIC_VERSION
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(ForDateProductSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(ProductViewSet, self).destroy(request, *args, **kwargs)

    @list_route(methods=['GET'])
    def for_open_func(self, request):
        grid = int(self.request.GET.get('grid', 0))  # 节点
        cli_version = int(self.request.GET.get('cli_version', 0))  # 客户版本

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        func_grid_list = list(FunctionInfo.objects.all().prefetch_related('version__grid').filter(
            version__grid=grid).values_list('id', flat=True))

        for item in serializer.data:
            del_func_list = []
            for each in item['function']:
                # 验证该功能是否属于该节点所指定的版本，以及 该功能的客户版本条件是否与本站点一致；否则删除
                if not ((each['id'] in func_grid_list) and \
                                (each['cli_version'] == cli_version or each['cli_version'] == CLI_UNLIMITED)):
                    del_func_list.append(each)

            if del_func_list:
                for func_info in del_func_list:
                    item['function'].remove(func_info)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 重构版 产品
class RefProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().filter(classify=REFACTOR_VERSION).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'forgrid':
            return ProductSerializer
        elif self.action == 'foropen':
            return SimpProductSerializer
        elif self.action == 'fordata':
            return ForDateProductSerializer
        elif self.action == 'for_open_func':
            return ForOpenProductSerializer
        elif self.suffix == 'List' and self.request.method == 'GET':
            return SimpProductSerializer
        else:
            return ProductSerializer

    @list_route(methods=['get'])
    def forgrid(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(RefProductViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def foropen(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(RefProductViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def fordata(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(RefProductViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        # 产品中search
        queryset = Product.objects.all().filter(classify=REFACTOR_VERSION).order_by('-id')
        # queryset = Product.objects.all().filter(classify=REFACTOR_VERSION) \
        #     .prefetch_related('function__dependences__function', 'function__parent' \
        #                       , 'function__selection', 'function__selection__childfunc') \
        #     .order_by('-id')
        product = self.request.GET.get('product_name', "").strip()  # 获取单个产品
        products = self.request.GET.getlist('product', [])  # 开站点时，取功能列表，需传入多个产品ID
        if product:
            queryset = queryset.filter(product=product)
        if products:
            queryset = queryset.filter(id__in=products)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        data['classify'] = REFACTOR_VERSION
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(ForDateProductSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data
        data['classify'] = REFACTOR_VERSION
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(ForDateProductSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(RefProductViewSet, self).destroy(request, *args, **kwargs)

    @list_route(methods=['get'])
    def for_open_func(self, request):
        grid = int(self.request.GET.get('grid', 0))  # 节点
        cli_version = int(self.request.GET.get('cli_version', 0))  # 客户版本

        func_grid_list = list(FunctionInfo.objects.all().prefetch_related('version__grid').filter(
            version__grid=grid).values_list('id', flat=True))

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        func_tree = FunctionViewSet.get_func_tree()
        for item in serializer.data:
            del_func_list = []
            for each in item['function']:
                # 验证该功能是否属于该节点所指定的版本，以及 该功能的客户版本条件是否与本站点一致；否则删除
                if (each['id'] in func_grid_list) and \
                        (each['cli_version'] == cli_version or each['cli_version'] == CLI_UNLIMITED):
                    # 通过验证的功能，处理其dependences
                    for i in range(0, len(each['dependences'])):
                        each['dependences'][i] = func_tree[each['dependences'][i]]
                else:
                    del_func_list.append(each)

            if del_func_list:
                for func_info in del_func_list:
                    item['function'].remove(func_info)

        return Response(serializer.data, status=status.HTTP_200_OK)


class VersionViewSet(viewsets.ModelViewSet):
    queryset = VersionInfo.objects.all().order_by('-id')
    serializer_class = VersionInfoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(SimpVersionInfoSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(SimpVersionInfoSerializer(instance).data, status=status.HTTP_200_OK)

    @detail_route(methods=['put'])
    def modify_func(self, request, pk=None):
        function_list = request.data.get('function', [])
        function_set = FunctionInfo.objects.all().filter(id__in=function_list)
        instance = self.get_object()
        with transaction.atomic():
            instance.function.set(function_set)
            instance.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(VersionViewSet, self).destroy(request, *args, **kwargs)


# 功能
class FunctionViewSet(viewsets.ModelViewSet):
    queryset = FunctionInfo.objects.all().order_by('-id')

    def get_serializer_class(self):

        if self.suffix == 'Instance' and self.request.method == 'GET':
            return ForDetailFunctionSerializer

        else:
            return FunctionInfoSerializer

    def create(self, request, *args, **kwargs):
        selection_info = request.data.pop('selection')
        product = request.data['product']
        classify = Product.objects.get(id=product).classify

        if classify == REFACTOR_VERSION:
            parent_set = []
            depend_set = []
            # 若parent_info有id(代表单选项)有值，则获取这些单选项对象
            parent_info = request.data.pop('parent')
            if parent_info['id']:
                parent_set = list(SingleSelection.objects.all().filter(id__in=parent_info['id']))

            # depend_info(代表单选项)有值，则获取这些单选项对象
            depend_info = request.data.pop('dependences')
            if depend_info['id']:
                depend_set = list(SingleSelection.objects.all().filter(id__in=depend_info['id']))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()

            selection_list = []  # 存放未真正执行保存的选项对象
            # 取selection信息，创建selection
            for selc_data in selection_info:
                selc_data['function_id'] = instance.id
                selec = SingleSelection(**selc_data)
                selection_list.append(selec)
            SingleSelection.objects.bulk_create(selection_list)

            if classify == REFACTOR_VERSION:
                if parent_info['ipu']:
                    for func_inpt in parent_info['ipu']:
                        for each_inpt in func_inpt['value']:
                            selec, _ = SingleSelection.objects.get_or_create(function_id=func_inpt['id'],
                                                                                 select_value=each_inpt, \
                                                                             select_name=each_inpt)
                            parent_set.append(selec)
                instance.parent.set(parent_set)

                if depend_info['ipu']:
                    for func_inpt in depend_info['ipu']:
                        for each_inpt in func_inpt['value']:
                            selec, _ = SingleSelection.objects.get_or_create(function_id=func_inpt['id'],
                                                                             select_value=each_inpt, \
                                                                             select_name=each_inpt)
                            depend_set.append(selec)
                instance.dependences.set(depend_set)

            instance.save()
        OperateLog.create_log(request)
        return Response(ForDetailFunctionSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        selection_info = request.data.pop('selection')
        product = request.data['product']
        classify = Product.objects.get(id=product).classify

        if classify == REFACTOR_VERSION:
            parent_set = []
            depend_set = []

            # 为添加父级展示条件做准备
            # 若parent_info有id(代表单选项)有值，则获取这些单选项对象
            parent_info = request.data.pop('parent')
            if parent_info['id']:
                parent_set = list(SingleSelection.objects.all().filter(id__in=parent_info['id']))

            # 为添加联动展示条件做准备
            # depend_info(代表单选项)有值，则获取这些单选项对象
            depend_info = request.data.pop('dependences')
            if depend_info['id']:
                depend_set = list(SingleSelection.objects.all().filter(id__in=depend_info['id']))

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
            if classify == REFACTOR_VERSION:
                if parent_info['id']:
                    instance.parent.set(parent_set)
                if depend_info['id']:
                    instance.dependences.set(depend_set)

            selection_list = []  # 不同于新增，这个列表的元素是对象
            # 取selection信息，创建selection
            for selec_data in selection_info:
                selec_data['function_id'] = instance.id
                del selec_data['childfunc']
                selec, _ = SingleSelection.objects.update_or_create(**selec_data)
                selection_list.append(selec)
            instance.selection.set(selection_list)

            if classify == REFACTOR_VERSION:
                if parent_info['ipu']:
                    for func_inpt in parent_info['ipu']:
                        for each_inpt in func_inpt['value']:
                            selec, _ = SingleSelection.objects.get_or_create(function_id=func_inpt['id'],
                                                                             select_value=each_inpt, \
                                                                             select_name=each_inpt)
                            parent_set.append(selec)
                instance.parent.set(parent_set)

                if depend_info['ipu']:
                    for func_inpt in depend_info['ipu']:
                        for each_inpt in func_inpt['value']:
                            selec, _ = SingleSelection.objects.get_or_create(function_id=func_inpt['id'],
                                                                             select_value=each_inpt, \
                                                                             select_name=each_inpt)
                            depend_set.append(selec)
                            instance.dependences.set(depend_set)

                            instance.save()

                            OperateLog.create_log(request)
        return Response(ForDetailFunctionSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(FunctionViewSet, self).destroy(request, *args, **kwargs)

    @classmethod
    def get_func_tree(cls):
        func_tree = {}
        func_id_list = FunctionInfo.objects.all().values_list('id', flat=True)
        par_dict = {}
        count = 0
        while True:
            queryset = FunctionInfo.objects.all().filter(
                Q(id__in=func_id_list) & Q(parent__isnull=False)).distinct().prefetch_related(
                'parent__select_name', 'parent__function', 'parent__function__func_name').values('parent__function',
                                                                                                 'parent__function__func_name',
                                                                                                 'parent__select_name',
                                                                                                 'id')
            # 获取functionInfo_id 和 父级功能名称parent__function__func_name的对应关系
            map_ = {}
            for item in queryset:
                map_.setdefault(item['id'], '')
                map_[item['id']] = item['parent__function__func_name']

            if not queryset:
                break

            # 将 父级展示条件的选项名和选项值取出，对应存储
            for item in queryset:
                str_ = map_[item['id']]
                if not par_dict:
                    dict_tree = OrderedDict()
                    dict_tree[str_] = []
                    func_tree.setdefault(item['id'], dict_tree)
                    func_tree[item['id']][str_].append(item['parent__select_name'])

                else:
                    child_id_list = par_dict[item['id']]
                    for child_id in child_id_list:
                        func_tree[child_id].setdefault(str_, [])
                        func_tree[child_id][str_].append(item['parent__select_name'])

            par_dict_new = {}
            for item in queryset:
                par_dict_new.setdefault(item['parent__function'], [])
                if not queryset.filter(id=item['id']):
                    continue
                if par_dict:
                    for each in par_dict[item['id']]:
                        par_dict_new[item['parent__function']].append(each)
                else:
                    par_dict_new[item['parent__function']].append(item['id'])

            par_dict = par_dict_new
            for each in par_dict.keys():
                par_dict[each] = set(par_dict[each])

            func_id_list = list(par_dict.keys())
            count += 1

        for key, value in func_tree.items():
            values_str = ''
            for l_key, l_value in value.items():
                str_l = str(l_value).lstrip('[').rstrip(']').replace("'", "").replace(",", "/")
                values_str = l_key + "(" + str_l + ')' + '-->' + values_str

            func_tree[key] = values_str.rstrip('-->')

        return func_tree

    def get_queryset(self):
        queryset = FunctionInfo.objects.all().order_by('-id')
        parent = int(self.request.GET.get('parent', 0))
        depend = int(self.request.GET.get('depend', 0))
        product = self.request.GET.get('product', 0)  # 产品
        grid = int(self.request.GET.get('grid', 0))  # 节点
        cli_version = int(self.request.GET.get('cli_version', 0))  # 客户版本

        if parent:
            self.pagination_class = None
            queryset = queryset.filter(product_id=product)
        elif depend:
            self.pagination_class = None
            queryset = queryset.exclude(product_id=product)
        elif product:
            queryset = queryset.filter(product_id=product)

        return queryset.distinct()  # 选项


class SelectionViewSet(viewsets.ModelViewSet):
    queryset = SingleSelection.objects.all().select_related('function').order_by('-id')
    serializer_class = SingleSelectionSerializer

    @detail_route(methods=['put'])
    def modify_default(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        selection = SingleSelection.objects.all() \
            .filter(function__id=instance.function.id,
                    is_default=True)

        with transaction.atomic():
            if selection.exists():
                for selec in selection:
                    selec.is_default = 0
                    selec.save()

            instance.is_default = 1
            instance.save()
        OperateLog.create_log(request)
        return Response({}, status=status.HTTP_200_OK)


# 服务器
class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all().prefetch_related('ser_url').order_by('-id')
    serializer_class = ServerSerializer

    def get_queryset(self):
        # 服务器中search
        queryset = Server.objects.all().prefetch_related("ser_url", "ser_url__ser_ip", "ser_name").order_by('-id')
        ser_id = self.request.GET.get('ser_id', "").strip()  # 服务器ID
        if ser_id:
            queryset = queryset.filter(ser_id=ser_id)
        version_type = self.request.GET.get('version_type', None)
        if not version_type:
            version_type = CLASSIC_VERSION
        queryset = queryset.filter(version_type=version_type)
        return queryset

    def valid(self, server_serializer, seraddress_data_list):
        try:
            server_serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for adrs_data in seraddress_data_list:
            ip_data_list = adrs_data['ser_ip']
            adrs_serializer = SerAddressSerializer(data=adrs_data)
            try:
                adrs_serializer.is_valid(raise_exception=True)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            for ip_data in ip_data_list:
                try:
                    ip_serializer = SerIpSerializer(data=ip_data)
                    ip_serializer.is_valid(raise_exception=True)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        server_data = request.data
        seraddress_data_list = server_data.pop('ser_url')
        if server_data['ser_id'] in Server.objects.all().values_list('ser_id', flat=True):
            return Response({'error': '服务ID不能重复'}, status=status.HTTP_400_BAD_REQUEST)

        ser_serializer = self.get_serializer(data=server_data)

        self.valid(ser_serializer, seraddress_data_list)

        with transaction.atomic():
            server = ser_serializer.create(server_data)
            for adrs_data in seraddress_data_list:
                ip_data_info = adrs_data.pop('ser_ip')
                adrs_data['server'] = server
                adrs_serializer = SerAddressSerializer(data=adrs_data)
                adrs_instance = adrs_serializer.create(adrs_data)

                # 创建address下的所有ip
                ip_serializer = SerIpSerializer(data=ip_data_info, many=True)
                ip_create_list = ip_serializer.create(ip_data_info)
                # 为该address设置ip
                adrs_instance.ser_ip.set(ip_create_list)
        OperateLog.create_log(request)
        return Response(ServerSerializer(server).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        server_data = request.data
        seraddress_data_list = server_data.pop('ser_url')
        instance = self.get_object()
        if server_data['ser_id'] != instance.ser_id:
            if server_data['ser_id'] in Server.objects.all().values_list('ser_id', flat=True):
                return Response({'error': '服务ID不能重复'}, status=status.HTTP_400_BAD_REQUEST)

        ser_serializer = self.get_serializer(data=server_data)
        self.valid(ser_serializer, seraddress_data_list)

        with transaction.atomic():
            server = ser_serializer.update(instance, server_data)
            adrs_list = []

            for adrs_data in seraddress_data_list:
                ip_data_list = adrs_data.pop('ser_ip')
                adrs_data['server'] = server
                ip_list = []
                ip_creat_info = []
                if 'id' in adrs_data.keys():
                    adrs = SerAddress.objects.all().get(pk=adrs_data['id'])
                    adrs_serializer = SerAddressSerializer(data=adrs_data)
                    adrs_instance = adrs_serializer.update(adrs, adrs_data)

                    for ip_data in ip_data_list:
                        if 'id' in ip_data.keys():
                            ip = SerIp.objects.all().get(pk=ip_data['id'])
                            ip_serializer = SerIpSerializer(data=ip_data)
                            ip_serializer.update(ip, ip_data)
                            ip_list.append(ip)
                        else:
                            ip_creat_info.append(ip_data)

                else:
                    adrs_serializer = SerAddressSerializer(data=adrs_data)
                    adrs_instance = adrs_serializer.create(adrs_data)
                    for ip_data in ip_data_list:
                        ip_creat_info.append(ip_data)
                ip_creat_serializer = SerIpSerializer(data=ip_creat_info, many=True)
                ip_creat_list = ip_creat_serializer.create(ip_creat_info)
                ip_list.extend(ip_creat_list)
                adrs_instance.ser_ip.set(ip_list)

                adrs_list.append(adrs_instance)
            server.ser_url.set(adrs_list)
        OperateLog.create_log(request)
        return Response(ServerSerializer(server).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(ServerViewSet, self).destroy(request, *args, **kwargs)


# 服务器类型
class SerTypeViewSet(viewsets.ModelViewSet):
    queryset = SerType.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action == 'forgroup':
            return ForGroupSerTypeSerializer
        else:
            return SerTypeSerializer

    @list_route(methods=['get'])
    def forgroup(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(SerTypeViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def forserver(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(SerTypeViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(SerTypeViewSet, self).get_queryset()
        version_type = self.request.GET.get('version_type', None)
        if not version_type:
            version_type = CLASSIC_VERSION
        queryset = queryset.filter(version_type=version_type)
        return queryset.filter(version_type=version_type)

    def create(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        super(SerTypeViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(SerTypeViewSet, self).update(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': '修改关联信息失败', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(SerTypeViewSet, self).destroy(request, *args, **kwargs)


# 服务组
class GroupViewSet(viewsets.ModelViewSet):
    queryset = ServerGroup.objects.all().order_by("-id")

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return SimpGroupSerializer
        elif self.action == 'forgrid':
            return SimpGroupSerializer
        else:
            return GroupSerializer

    @list_route(methods=['get'])
    def forgrid(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(GroupViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        # 服务组search
        queryset = ServerGroup.objects.all().order_by("-id")
        group_name = self.request.GET.get('group_name', "").strip()  # 服务组名称
        version_type = self.request.GET.get('version_type', None)
        if not version_type:
            version_type = CLASSIC_VERSION
        queryset = queryset.filter(version_type=version_type)
        if group_name:
            queryset = queryset.filter(group_name=group_name)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(GroupViewSet, self).create(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(GroupViewSet, self).update(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(GroupViewSet, self).destroy(request, *args, **kwargs)


# 节点
class GridViewSet(viewsets.ModelViewSet):
    queryset = Grid.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action == 'foropen':
            return SimpGridSerializer

        elif self.suffix == 'List' and self.request.method == 'GET':
            return SimpGridSerializer
        else:
            return GridSerializer

    @list_route(methods=['get'])
    def foropen(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(GridViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Grid.objects.all().order_by('-id')
        grid_name = self.request.GET.get('grid_name', "").strip()  # 节点名称
        grid_site = self.request.GET.get('grid_site', "").strip()  # 机房
        deploy_way = int(self.request.GET.get('deploy_way', 0))  # 部署方式
        is_open = self.request.GET.get('is_open', "").strip()  # 是否是开站
        if grid_name:
            queryset = queryset.filter(grid_name=grid_name)
        if grid_site:
            queryset = queryset.filter(grid_site=grid_site)
        if deploy_way:
            queryset = queryset.filter(deploy_way=deploy_way)
        # if is_open:
        #     grid_ids = SerGrpInquriesViewSet.under_grid()
        #     queryset = queryset.filter(pk__in=grid_ids)
        return queryset

    def grid_valid(self, db_serializer, grid_serializer):

        db_serializer.is_valid(raise_exception=True)

        grid_serializer.is_valid(raise_exception=True)

    def get_related_id_list(self, gd_info):
        group_list = gd_info.pop('grp_list')
        grp_id_list = []
        for group in group_list:
            grp_id_list.append(group['group_id'])

        verinfo_list = gd_info.pop('verinfo_list')
        ver_id_list = []
        for version in verinfo_list:
            ver_id_list.append(version['id'])

        return grp_id_list, ver_id_list

    def create(self, request, *args, **kwargs):
        for db in request.data['database']:
            ret = mysql_test(host=db['db_address'], user=db['db_username'], password=db['db_pwd'],
                             db=db['db_name'],
                             port=db['db_port'])
            if not ret:
                return Response({'error': '数据库配置录入数据错误，连接失败，请验证后重试'},
                                status=status.HTTP_424_FAILED_DEPENDENCY)

        # 取数据库信息，验证数据库信息valid；取节点信息，验证节点数据valid
        del request.data['group']
        del request.data['versionInfos']
        del request.data['db_info']
        grid_info = request.data
        databases_info = grid_info.pop('database')

        db_serializer = DataBaseInfoSerializer(data=databases_info, many=True)
        grid_serializer = SimpGridSerializer(data=grid_info)

        try:
            self.grid_valid(db_serializer, grid_serializer)
        except ValidationError as v:
            return Response({'error': str(v)}, status=status.HTTP_400_BAD_REQUEST)

        group_id_list, version_id_list = self.get_related_id_list(grid_info)

        # 创建节点对象, 创建数据库对象
        try:
            with transaction.atomic():
                grid = grid_serializer.create(grid_info)
                for db in databases_info:
                    db['grid'] = grid
                    db['db_pwd'] = encrypt(db['db_pwd'])
                    if 'dele' in db.keys():
                        del db['dele']

                # 创建数据库对象
                db = db_serializer.create(databases_info)
                # 为该节点设置数据库
                grid.db_info.set(db)
                # 为该节点设置服务组
                grid.group.set(ServerGroup.objects.all().filter(pk__in=group_id_list))
                # 为该节点设置版本信息
                grid.versionInfos.set(VersionInfo.objects.all().filter(pk__in=version_id_list))
                grid.save()
                OperateLog.create_log(request)
                return Response(GridSerializer(grid).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        for db in request.data['database']:
            if ('id' in db.keys()) and (db['db_pwd'] == DataBaseInfo.objects.all().get(id=db['id']).db_pwd):
                db['db_pwd'] = decrypt(db['db_pwd'])
            ret = mysql_test(host=db['db_address'], user=db['db_username'], password=db['db_pwd'],
                             db=db['db_name'],
                             port=db['db_port'])
            if not ret:
                return Response({'error': '数据库配置录入数据错误，连接失败，请验证后重试'},
                                status=status.HTTP_424_FAILED_DEPENDENCY)
        # 取数据库信息，验证数据库信息valid；取节点信息，验证节点数据valid
        del request.data['group']
        del request.data['versionInfos']
        del request.data['db_info']
        grid_info = request.data
        databases_info = grid_info.pop('database')

        db_serializer = DataBaseInfoSerializer(data=databases_info, many=True)
        instance = self.get_object()
        grid_serializer = SimpGridSerializer(instance, data=grid_info)
        try:
            # 校验数据库信息和节点信息
            self.grid_valid(db_serializer, grid_serializer)
        except ValidationError as v:
            return Response({'error': str(v)}, status=status.HTTP_400_BAD_REQUEST)

        group_id_list, version_id_list = self.get_related_id_list(grid_info)

        # 创建节点对象, 创建数据库对象
        try:
            with transaction.atomic():
                grid = grid_serializer.update(instance, grid_info)
                db_list = []
                db_create_info = []
                for db in databases_info:
                    db['grid'] = grid
                    if 'dele' in db.keys():
                        del db['dele']
                    # 修改已存在的数据库信息
                    if 'id' in db.keys():
                        db_instance = DataBaseInfo.objects.filter(id=db['id'])
                        # 若密码修改，需将新密码加密后再入库
                        if db['db_pwd'] != db_instance.first().db_pwd:
                            db['db_pwd'] = encrypt(db['db_pwd'])

                        db_instance.update(**db)
                        # 将数据库对象添加至节点数据库列表中
                        db_list.append(db_instance.first())

                    else:  # 新增数据库，需将密码加密后再入库，将改数据库信息，放入新建数据库列表
                        db['db_pwd'] = encrypt(db['db_pwd'])
                        db_create_info.append(db)

                # 创建新增数据库的serializer对象
                db_create_serializer = DataBaseInfoSerializer(data=db_create_info, many=True)
                # 创建新增数据库
                db_create_list = db_create_serializer.create(db_create_info)
                db_list.extend(db_create_list)

                grid.db_info.set(db_list)
                grid.group.set(ServerGroup.objects.all().filter(pk__in=group_id_list))
                grid.versionInfos.set(VersionInfo.objects.all().filter(pk__in=version_id_list))
                grid.save()
                OperateLog.create_log(request)
                return Response(GridSerializer(grid).data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(GridViewSet, self).destroy(request, *args, **kwargs)


# 数据库
class DataBaseInfoViewSet(viewsets.ModelViewSet):
    queryset = DataBaseInfo.objects.all().order_by('-id')
    serializer_class = DataBaseInfoSerializer


class SerAddressViewSet(viewsets.ModelViewSet):
    queryset = SerAddress.objects.all().order_by('-id')
    serializer_class = SerAddressSerializer

    @list_route(methods=['get'])
    def export(self, request, *args, **kwargs):
        version_type = int(self.request.GET.get('version_type', 0))
        if not version_type:
            return Response({'error': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)

        data = []

        first_grp = ServerGroup.objects.all().filter(version_type=version_type).first()
        if first_grp:
            ser_adrs_set = SerAddress.objects.all().filter(group=first_grp)
            serializer = SerAddressSerializer(ser_adrs_set, many=True)
            data = serializer.data

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=server.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        sheet_prd = wb.add_sheet('server')

        style_heading = xlwt.easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x19;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """
                                    )
        style_body = xlwt.easyxf("""
                font:
                    name Arial,
                    bold off,
                    height 0XA0;
                align:
                    wrap on,
                    vert center,
                    horiz left;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """
                                 )

        # 1st line
        sheet_prd.write(0, 0, '服务ID', style_heading)
        sheet_prd.write(0, 1, '服务', style_heading)
        sheet_prd.write(0, 2, '地址名称', style_heading)
        sheet_prd.write(0, 3, 'IP', style_heading)
        sheet_prd.write(0, 4, 'IP', style_heading)
        sheet_prd.write(0, 5, 'IP', style_heading)
        sheet_prd.write(0, 6, 'IP', style_heading)

        row = 1
        for content in data:
            sheet_prd.write(row, 0, content['server'], style_body)
            sheet_prd.write(row, 1, content['ser_type'], style_body)
            sheet_prd.write(row, 2, content['ser_address'], style_body)
            n = 3
            for each in content['ser_ip']:
                sheet_prd.write(row, n, each['ser_ip'], style_body)
                n += 1

            # 第一行加宽
            sheet_prd.col(0).width = 100 * 50
            sheet_prd.col(1).width = 100 * 50
            sheet_prd.col(2).width = 400 * 50
            sheet_prd.col(3).width = 100 * 50
            sheet_prd.col(4).width = 100 * 50
            sheet_prd.col(5).width = 100 * 50
            sheet_prd.col(6).width = 100 * 50
            row += 1

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response

    def _excel_table_by_name(self, file_contents=None,
                             col_name_index=0, sheet_name=u'server'):
        """
            根据名称获取Excel表格中的数据
            参数: file_excel：Excel文件路径
                 col_name_index：表头列名所在行的索引
                 sheet_name：Sheet1名称
        """
        data = xlrd.open_workbook(file_contents=file_contents)
        table = data.sheet_by_name(sheet_name)
        n_rows = table.nrows  # 行数
        col_names = table.row_values(col_name_index)  # 某一行数据
        row_data = []
        for row_num in range(1, n_rows):
            row = table.row_values(row_num)
            row_data.append(row)
        return row_data

    @list_route(methods=['post'])
    def import_save(self, request, *args, **kwargs):
        myFile = request.FILES["file"]  # 获取上传的文件，如果没有文件，则默认为None
        if not myFile:
            return Response({"error": "没有文件上传"}, status=status.HTTP_400_BAD_REQUEST)

        file = myFile.read()
        data = self._excel_table_by_name(file_contents=file)

        version_type = self.request.GET.get('version_type', 0)

        ser_dict = {}

        num = 0
        for adrs in data:
            """
            adrs[0] 服务ID
            adrs[1] 服务类型
            adrs[2] 地址名称
            adrs[3-6] ip
            """
            """
            逻辑：先改造数据结构，再创建服务，最后创建地址和IP
            """
            num += 1
            # 考虑 服务ID或服务未填的情况
            if not str(adrs[0]) and str(adrs[1]):
                return Response({'error': '第{}行服务ID不能为空'.format(num)}, status=status.HTTP_400_BAD_REQUEST)
            elif str(adrs[0]) and not str(adrs[1]):
                return Response({'error': '第{}行服务不能为空'.format(num)}, status=status.HTTP_400_BAD_REQUEST)
            elif not (str(adrs[0]) and str(adrs[1])):
                continue

            temp_key = str(adrs[0]).strip() + '_' + str(adrs[1]).strip()
            ser_dict.setdefault(temp_key, [])
            ser_url = str(adrs[2]).strip() + '<>'
            for num in range(3, 7):
                if adrs[num]:
                    ser_url += str(adrs[num]).strip() + '++'
            ser_url.rstrip('++')
            ser_dict[temp_key].append(ser_url)

        ser_id_set = Server.objects.all().values_list('ser_id', flat=True)
        ser_type_set = SerType.objects.all().values_list('ser_type', 'id')
        ser_type_map = dict(ser_type_set)

        for key, value in ser_dict.items():
            ser_ID, ser_type = key.split('_')
            ser_ID = ser_ID.strip()
            ser_type = ser_type.strip()
            if ser_ID not in ser_id_set:
                return Response({'error': '服务ID{}不存在'.format(ser_ID)}, status=status.HTTP_400_BAD_REQUEST)
            if ser_type not in ser_type_map.keys():
                return Response({'error': '服务{}不存在'.format(ser_type)}, status=status.HTTP_400_BAD_REQUEST)

        server_list = []
        url_create_info = []
        url_create_list = []
        ip_create_info = []
        ip_create_list = []
        for key, value in ser_dict.items():
            ser_ID, _ = key.split('_')
            ser_ID = ser_ID.strip()
            server_list.append(ser_ID)

            for url_data in value:
                ser_url, ser_ip_info = url_data.split('<>')
                ip_list = ser_ip_info.split('++')
                ser_url = ser_url.strip()
                url_create_info.append({'server_id': ser_ID, 'ser_address': ser_url})
                serid_adrs = str(ser_ID) + '_' + ser_url
                for ip in ip_list:
                    ip = ip.strip()
                    if ip:
                        ip_create_info.append({'ser_ip': ip, 'serid_adrs': serid_adrs})

        ser_id_list = Server.objects.all().filter(version_type=version_type, ser_id__in=server_list).values_list(
            'ser_id', 'id')
        ser_id_map = dict(ser_id_list)

        ser_address_list = []
        for url in url_create_info:
            ser_adrs = SerAddress(server_id=ser_id_map[url['server_id']], ser_address=url['ser_address'])
            url_create_list.append(ser_adrs)
            ser_address_list.append(url['ser_address'])

        SerAddress.objects.bulk_create(url_create_list)

        # 服务地址会否被重复利用
        adrs_id_list = SerAddress.objects.all(). \
            filter(server_id__in=ser_id_map.values(), ser_address__in=ser_address_list). \
            select_related('server__ser_id').values_list('server__ser_id', "ser_address", 'id')
        adrs_id_map = {}
        for each in adrs_id_list:
            key = str(each[0]) + '_' + each[1]
            adrs_id_map[key] = each[2]

        for ip in ip_create_info:
            ip_item = SerIp(ser_address_id=adrs_id_map[ip['serid_adrs']], ser_ip=ip['ser_ip'])
            ip_create_list.append(ip_item)
        SerIp.objects.bulk_create(ip_create_list)
        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def deployway(request):
    fields = ['id', 'name']
    ret = {'data': []}
    for item in DEPLOY_WAYS:
        ret['data'].append(dict(zip(fields, item)))
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def cli_version(request):
    fields = ['id', 'name']
    ret = {'data': []}
    for item in CLI_CHOICES:
        ret['data'].append(dict(zip(fields, item)))
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def deploy_way_grid_ship(request):
    ships = Grid.objects.all().values_list("grid_name", "id", "deploy_way")
    deploy_ways_map = dict(DEPLOY_WAYS)
    data = {}
    for grid_name, grid_id, deploy_way in ships:
        deploy_way = deploy_ways_map[deploy_way]
        data.setdefault(deploy_way, [])
        data[deploy_way].append({
            "id": grid_id,
            "name": grid_name
        })
    all_deploy_way = deploy_ways_map.values()
    for d_w in all_deploy_way:
        if d_w not in data.keys():
            data[d_w] = []
    return Response([{"name": k, "children": v} for k, v in data.items()])


@api_view(['GET'])
def deploy_way_group_ship(request):
    grid_set = Grid.objects.all()
    deploy_way_map = dict(DEPLOY_WAYS)

    grid_serializer = ForShipGridSerializer(grid_set, many=True)
    grid_data = grid_serializer.data
    data = {}
    for each in grid_data:

        group_list = []
        deploy_way = each['deploy_way']
        for group in each['group']:
            group_id, group_name = group.values()
            group_list.append({'id': group_id, 'name': group_name})

        data.setdefault(deploy_way, [])

        data[deploy_way].append(
            {
                "id": each['id'],
                "name": each['grid_name'],
                "children": group_list
            })
    for dep_way in deploy_way_map.keys():
        if dep_way not in data.keys():
            data[dep_way] = []

    return Response([{"id": key, "name": deploy_way_map[key], "children": value} for key, value in data.items()],
                    status=status.HTTP_200_OK)


@api_view(['GET'])
def version_type(request):
    data = [{"id": i[0], "name": i[1]} for i in PROD_SERV_VERSIONS]
    # data = [dict(zip(("id", "name"), i)) for i in PROD_SERV_VERSIONS]
    return Response(data)


def function_selection_import(request):
    if not request.method == "POST":
        return JsonResponse({"error": "method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    product_name = request.GET.get("product")
    # version = request.GET.get("version")
    excel = xlrd.open_workbook(file_contents=request.FILES["file"].read())
    table = excel.sheets()[0]
    if table.nrows < 2 or (table.row_values(1) != ['功能名称', '功能路径', '功能类型', '客户版本', '选项名称', '选项值', '是否默认']):
        return JsonResponse({"error": "导入文件格式有误，请联系管理员"}, status=status.HTTP_400_BAD_REQUEST)

    for num in range(2, table.nrows):
        func_code, func_name, func_type, cli_ver, slc_name, slc_val, is_default = table.row_values(num)
        product_obj, _ = Product.objects.get_or_create(product=product_name)
        # version_obj, _ = VersionInfo.objects.get_or_create(product=product_obj, pro_version=version)
        # function_obj, _ = FunctionInfo.objects.update_or_create(
        #     defaults=dict(func_name=func_name, cli_version=cli_ver, func_type=func_type),
        #     func_code=func_code, version=version_obj, )
        function_obj, _ = FunctionInfo.objects.update_or_create(
            defaults=dict(func_name=func_name, cli_version=cli_ver, func_type=func_type),
            func_code=func_code)
        SingleSelection.objects.update_or_create(
            defaults=dict(select_value=slc_val, is_default=bool(int(is_default))),
            function=function_obj, select_name=slc_name, )

    return JsonResponse({"msg": "import success"})
