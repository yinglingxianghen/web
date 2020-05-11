from __future__ import unicode_literals

import logging

from django.contrib.auth.models import User, Group, Permission
from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from django.db.models import Q

from applications.log_manage.models import OperateLog
from applications.permission_and_staff_manage.models import Structure
from applications.permission_and_staff_manage.serializers import GroupFromLdapSerializer, PermissionSerializer, \
    StructureSerializer, UserFromLdapSerializer, SimpGroupFromLdapSerializer

log = logging.getLogger("Django")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related("employee__department").order_by('-id')
    serializer_class = UserFromLdapSerializer

    def get_queryset(self):
        # 人员列表的search
        queryset = User.objects.all().select_related("employee__department").order_by('-id')
        group_name = self.request.GET.get('group_name', "").strip()
        user_name = self.request.GET.get('username', "").strip()  # 人员
        dpt_name = self.request.GET.get('department', "").strip()  # 部门
        if dpt_name:
            queryset = queryset.filter(employee__department__dpt_name=dpt_name)
        if group_name:
            queryset = queryset.filter(groups__name=group_name)
        if user_name:
            queryset = queryset.filter(last_name=user_name)
        return queryset

    @detail_route(methods=['get'])
    def get_user_perm(self, request, pk=None):
        perm_dict = {
            'auth': {
                'view': 0,
                'group': {"view": 0},
                'user': {"view": 0},
                'structure': {"view": 0}
            },
            'production_manage': {
                'view': 0,
                'ops': {'view': 0},
                'pro': {"view": 0}
            },
            'workorder_manage': {
                'view': 0,
                'openstationmanage': {"view": 0}
            },
            'log': {
                'view': 0,
                'system-log': {'view': 0},
                'personal-log': {'view': 0}
            },
            'data_manage': {
                'view': 0,
                'overview': {'view': 0},
                'prod_oper': {'view': 0},
                'data_ops': {'view': 0},
            },
            'setup': {
                'view': 0,
                'help_center': {'view': 0},
                'industry': {'view': 0}
            }
        }
        permissions = request.user.get_group_permissions()
        for item in permissions:
            app = item.split('.')[0]
            action, mod = item.split('.')[1].split('_')
            if action == 'view':
                # 角色权限模块
                if app == 'auth' and mod != 'permission':
                    perm_dict['auth']['view'] = 1
                    perm_dict['auth'][mod]['view'] = 1
                elif app == 'permission_and_staff_manage':
                    if mod != 'employee':
                        perm_dict['auth']['view'] = 1
                        perm_dict['auth'][mod]['view'] = 1

                # 产品管理模块权限
                elif app == 'production_manage':
                    perm_dict['production_manage']['view'] = 1
                    if mod in ['grid', 'servergroup', 'server', 'sertype']:
                        perm_dict['production_manage']['ops']['view'] = 1  # 运维配置

                    elif mod in ['versioninfo', 'product', 'singleselection', 'functioninfo']:
                        perm_dict['production_manage']['pro']['view'] = 1  # 产品配置

                # 工单管理
                elif app == 'workorder_manage':
                    perm_dict['workorder_manage']['view'] = 1
                    if mod == 'openstationmanage':
                        perm_dict['workorder_manage'][mod]['view'] = 1  # 开站
                    elif mod == 'industry':
                        perm_dict['setup'][mod]['view'] = 1

                # 日志
                elif app == 'log_manage':
                    perm_dict['log']['view'] = 1
                    if mod == 'system-log':
                        perm_dict['log'][mod]['view'] = 1
                    elif mod == 'personal-log':
                        perm_dict['log'][mod]['view'] = 1

                # 数据管理
                elif app == 'data_manage':
                    perm_dict['data_manage']['view'] = 1
                    if mod == 'overview-data':
                        perm_dict['data_manage']['overview']['view'] = 1
                    elif mod == 'prod-oper-data':
                        perm_dict['data_manage']['prod_oper']['view'] = 1
                    elif mod == 'ops-data':
                        perm_dict['data_manage']['data_ops']['view'] = 1

                elif app == 'setup':
                    perm_dict['setup']['view'] = 1
                    if mod == 'sitereceptiongroup':
                        perm_dict['setup']['help_center']['view'] = 1

            perm_dict.update({'user_name': request.user.last_name})
        return JsonResponse(perm_dict)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(UserViewSet, self).update(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        super(UserViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        super(UserViewSet, self).destroy(request, *args, **kwargs)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return SimpGroupFromLdapSerializer
        else:
            return GroupFromLdapSerializer

    def get_queryset(self):
        # 通过改写queryset ,实现搜索角色和查看人员的角色列表
        queryset = Group.objects.all().order_by('-id')
        group_name = self.request.GET.get('group_name', "").strip()
        if group_name:  # 实现搜索角色
            queryset = queryset.filter(name=group_name)
        return queryset

    def create(self, request, *args, **kwargs):
        # 角色新增
        group_data = request.data
        group_serializer = self.get_serializer(data=group_data)

        try:
            group_serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            instance = group_serializer.create(group_data)
        OperateLog.create_log(request)
        return Response(GroupFromLdapSerializer(instance).data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # 角色修改
        try:
            with transaction.atomic():
                super(GroupViewSet, self).update(request, *args, **kwargs)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        OperateLog.create_log(request)
        return Response({}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        super(GroupViewSet, self).destroy(request, *args, **kwargs)


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class StructureViewSet(viewsets.ModelViewSet):
    queryset = Structure.objects.all().order_by('-id')
    serializer_class = StructureSerializer

    @list_route(methods=['get'])
    def get_structure_tree(self, request):
        # 获取组织架构树
        temp_list = []
        ret = {}
        try:
            dept0 = Structure.objects.all().filter(parent__isnull=True).first()  # 根级
            dept1_list = Structure.objects.all().filter(parent=dept0)  # 一级
            i = 0
            for item in dept1_list:
                dept2_temp = Structure.objects.all().filter(parent=item)  # 二级
                data_temp = []
                if dept2_temp.exists() == 0:
                    temp_list.append({'id': item.id, 'name': item.dpt_name, 'children': data_temp})
                    continue

                for section in dept2_temp:
                    section = StructureSerializer(section)
                    data_temp.append({'id': section.data['id'], 'name': section.data['dpt_name']})

                temp_list.append({'id': item.id, 'name': item.dpt_name, 'children': data_temp})
                i += 1
            ret['id'] = dept0.id
            ret['name'] = dept0.dpt_name
            ret['children'] = temp_list
            return JsonResponse(ret)
        except Exception as e:
            log.error(e)
            return JsonResponse('', safe=False)
