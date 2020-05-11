import logging

from django.contrib.auth.models import Group, Permission, User
from rest_framework import serializers

from applications.permission_and_staff_manage.models import Structure, Employee

log = logging.getLogger("Django")


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'content_type')


class GroupForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class SimpGroupFromLdapSerializer(serializers.ModelSerializer):
    def get_own_user_count(self, group):
        count = group.user_set.count()
        return count

    own_user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('id', 'name', 'own_user_count')


class GroupFromLdapSerializer(serializers.ModelSerializer):
    PERMS_MAP = {
        "GROUP_PERMS": {
            "modify": ("change_group", "add_group"),
            "delete": "delete_group",
            "view": "view_group"
        },
        "USER_PERMS": {
            "modify": ("change_user", "add_user"),
            "delete": "delete_user",
            "view": "view_user"
        },
        "STRUCTURE_PERMS": {
            "modify": ("change_structure", "add_structure"),
            "delete": "delete_structure",
            "view": "view_structure"
        },
        "OPS_PERMS": {
            "modify": ("add_product", "change_product",
                       "add_grid", "change_grid",
                       'add_servergroup', "change_servergroup",
                       'add_server', "change_server",
                       "add_sertype", "change_sertype"),
            "delete": ("delete_product", "delete_grid",
                       "delete_servergroup", "delete_server",
                       "delete_sertype"),
            "view": ("view_product", "view_grid",
                     "view_servergroup", "view_server",
                     "view_sertype")
        },
        "PRO_PERMS": {
            "modify": ('add_versioninfo', 'change_versioninfo',
                       'add_product', 'change_product',
                       'add_singleselection', "change_singleselection",
                       'add_functioninfo', "change_functioninfo"),
            "delete": ("delete_versioninfo", "delete_product",
                       "delete_singleselection", "delete_functioninfo"),
            "view": ("view_versioninfo", "view_product",
                     "view_singleselection")
        },
        "OPEN_STATION_PERMS": {
            "modify": ("change_openstationmanage", "add_openstationmanage"),
            "delete": "delete_openstationmanage",
            "view": "view_openstationmanage"
        },
        "SYSTEM_LOG_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_system-log",
        },
        "PERSONAL_LOG_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_personal-log",
        },
        "DATA_OVERVIEW": {
            "modify": 0,
            "delete": 0,
            "view": "view_overview-data",
        },
        "DATA_PROD_OPER": {
            "modify": 0,
            "delete": 0,
            "view": "view_prod-oper-data",
        },
        "DATA_OPS": {
            "modify": 0,
            "delete": 0,
            "view": "view_ops-data",
        },
        "SETUP_HELP_CENTER": {
            "modify": ("add_sitereceptiongroup", "change_sitereceptiongroup"),
            "delete": "delete_sitereceptiongroup",
            "view": "view_sitereceptiongroup",
        },
        "SETUP_INDUSTRY": {
            "modify": ("add_industry", "change_industry"),
            "delete": "delete_industry",
            "view": "view_industry",
        }
    }

    def get_permissions(self, group):
        permission_list = group.permissions.all().values_list("codename", flat=True)

        # param perms: codename， 或者包含codename的元祖
        # 检测是否拥有权限， 如果传入codename元祖，则拥有其中任一权限，则认为拥有权限（或关系）
        def has_perm(perms):
            if isinstance(perms, tuple):
                for perm in perms:
                    if perm in permission_list:
                        return 1
                return 0
            else:
                if perms in permission_list:
                    return 1
                return 0

        perm_dict = {
            'auth': {
                'view': 0,
                'group': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["GROUP_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["GROUP_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["GROUP_PERMS"]['view']),
                },
                'user': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["USER_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["USER_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["USER_PERMS"]['view']),
                },
                'structure': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["STRUCTURE_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["STRUCTURE_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["STRUCTURE_PERMS"]['view']),
                }
            },
            'production_manage': {
                'view': 0,
                'ops': {
                    'ref-server': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-SERVER_PERMS"]['modify']),
                                   "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-SERVER_PERMS"]['delete']),
                                   "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-SERVER_PERMS"]['view'])},
                    'server': {},
                    'ser-grp': {},
                    'grid': {},
                },
                'pro': {
                    'ref-product': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"]['modify']),
                                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"]['delete']),
                                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"]['view'])},
                    'product': {}
                    }
            },
            'workorder_manage': {
                'view': 0,
                'openstationmanage': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["OPEN_STATION_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["OPEN_STATION_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["OPEN_STATION_PERMS"]['view']),
                }
            },
            'log': {
                'view': 0,
                'system-log': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SYSTEM_LOG_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SYSTEM_LOG_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SYSTEM_LOG_PERMS"]['view']),
                },
                'personal-log': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"]['view']),
                }
            },
            'data_manage': {
                'view': 0,
                'overview': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_OVERVIEW"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_OVERVIEW"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_OVERVIEW"]['view']),
                },
                'prod_oper': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_PROD_OPER"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_PROD_OPER"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_PROD_OPER"]['view']),
                },
                'data_ops': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_OPS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_OPS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_OPS"]['view']),
                }
            },
            'setup': {
                'view': 0,
                'help_center': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_HELP_CENTER"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_HELP_CENTER"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_HELP_CENTER"]['view']),
                },
                'industry': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_INDUSTRY"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_INDUSTRY"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_INDUSTRY"]['view']),
                }
            }
        }

        # 修改一级模块的查看权限
        for first, second in perm_dict.items():
            for key, options in second.items():
                if isinstance(options, dict):
                    if options.get("view") == 1:
                        perm_dict[first]["view"] = 1
                        break
        return perm_dict

    def get_own_user(self, group):
        own_user = group.user_set.all().values_list("last_name", "employee__department__dpt_name")
        user_list = []
        for username, department in own_user:
            user_list.append({
                "user_name": username,
                "department": department
            })
        return user_list

    def get_own_user_count(self, group):
        count = group.user_set.count()
        return count

    permissions = serializers.SerializerMethodField()
    own_user = serializers.SerializerMethodField()
    own_user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions', 'own_user', 'own_user_count')

    def set_permissions(self, instance, validated_data):
        # param name: json数据中对应模块的名称
        # param perm_map: 在类中指定的权限列表

        def to_new_permissions(name, perm_map):
            for action in ['modify', 'delete', 'view']:
                if formatted_data[name].get(action, 0):
                    if isinstance(perm_map[action], tuple):
                        new_permissions.update(perm_map[action])
                    else:
                        new_permissions.add(perm_map[action])

        # 将前端传来的数据格式化，剔除冗余数据，只保留二级模块的权限信息
        def get_formatted_data():
            formatted = dict()
            for each in validated_data.values():
                for k, v in each.items():
                    if isinstance(v, dict):
                        formatted.update({k: v})
            return formatted

        formatted_data = get_formatted_data()
        new_permissions = set()  # 前端传来的新权限列表

        # 指定二级模块的名称，以及该二级模块拥有的权限列表，添加至new_permissions
        to_new_permissions("user", GroupFromLdapSerializer.PERMS_MAP["USER_PERMS"])
        to_new_permissions("group", GroupFromLdapSerializer.PERMS_MAP["GROUP_PERMS"])
        to_new_permissions("structure", GroupFromLdapSerializer.PERMS_MAP["STRUCTURE_PERMS"])
        to_new_permissions("ops", GroupFromLdapSerializer.PERMS_MAP["OPS_PERMS"])
        to_new_permissions("pro", GroupFromLdapSerializer.PERMS_MAP["PRO_PERMS"])
        to_new_permissions("openstationmanage", GroupFromLdapSerializer.PERMS_MAP["OPEN_STATION_PERMS"])
        to_new_permissions("system-log", GroupFromLdapSerializer.PERMS_MAP["SYSTEM_LOG_PERMS"])
        to_new_permissions("personal-log", GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"])
        to_new_permissions("personal-log", GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"])
        to_new_permissions("overview", GroupFromLdapSerializer.PERMS_MAP["DATA_OVERVIEW"])
        to_new_permissions("prod_oper", GroupFromLdapSerializer.PERMS_MAP["DATA_PROD_OPER"])
        to_new_permissions("data_ops", GroupFromLdapSerializer.PERMS_MAP["DATA_OPS"])
        to_new_permissions("help_center", GroupFromLdapSerializer.PERMS_MAP["SETUP_HELP_CENTER"])
        to_new_permissions("industry", GroupFromLdapSerializer.PERMS_MAP["SETUP_INDUSTRY"])
        instance.permissions.set(objs=Permission.objects.filter(codename__in=new_permissions))

    # 重写post请求的方法
    def create(self, validated_data):
        # 新建group,无permissions信息
        group = Group()
        group.name = validated_data['name']
        group.save()

        # 根据发送请求的格式为self.context['request'].content_type ："application/json"，即json式请求，取permission_dict
        permission_dict = self.initial_data['permissions']

        self.set_permissions(instance=group, validated_data=permission_dict)
        return group

    # 重写put请求的方法
    def update(self, instance, validated_data):
        super(GroupFromLdapSerializer, self).update(instance, validated_data)
        permission_dict = self.initial_data['permissions']

        self.set_permissions(instance=instance, validated_data=permission_dict)
        return instance


class UserFromLdapSerializer(serializers.ModelSerializer):
    groups = GroupForUserSerializer(many=True)

    def get_department(self, instance):
        ret = ''
        try:
            employee = instance.employee
            department = employee.department
            ret = department.dpt_name

        except Exception as e:
            raise TypeError(e)
        finally:
            return ret

    department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'groups', 'department')

    # 重写put请求的方法
    def update(self, instance, validated_data):
        # 忽略groups信息，update本user,
        del validated_data['groups']
        super(UserFromLdapSerializer, self).update(instance, validated_data)

        #  self.context['request'].content_type == "application/json":  # json式请求
        group_list = self.initial_data['grop_list'].split(',')
        dpt_name = self.initial_data['department']

        # 清空本user中的groups信息，插入新的groups
        instance.groups.clear()
        for item in group_list:
            item = item.strip()
            instance.groups.add(Group.objects.get(name=item))

        department = Structure.objects.all().filter(dpt_name=dpt_name).first()
        if not department:
            raise Structure.DoesNotExist('%s部门信息填写错误' % dpt_name)

        employee = Employee.objects.filter(user=instance)
        if not employee.exists():
            Employee.objects.create(user=instance)
        instance.employee.department = department
        instance.employee.save()
        instance.save()
        return instance


class StructureSerializer(serializers.ModelSerializer):
    def get_own_user(self, department):
        own_user = User.objects.filter(employee__department=department)
        user_list = []
        role = []  # 角色
        for item in own_user:
            try:
                role = item.groups.values()

            except Exception as e:
                log.error(e)

            finally:
                user_list.append({'id': item.id, 'user_name': item.last_name, 'group': role})

        return user_list

    own_user = serializers.SerializerMethodField()

    class Meta:
        model = Structure
        fields = ('id', 'dpt_name', 'parent', 'own_user')
