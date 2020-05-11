# -*-coding:utf-8-*-

from django.db import models
import copy


# 定义抽象模型管理器基类

class BaseManager(models.Manager):
    def get_all_valid_fields(self):
        model_class = self.model
        attr_tuple = model_class._meta.get_fields()
        # 上面方法的返回的数据如下：
        #  <django.db.models.fields.related.ForeignKey: passport>,
        #  <django.db.models.fields.related.ForeignKey: goods>
        # 而数据库中的外键形式是：goods_id、passport_id，所以需要拼接成数据库的形式，从而能够插如数据
        print('attr_tuple:{}'.format(attr_tuple))
        attr_str_list = []
        for attr in attr_tuple:
            if isinstance(attr, models.ForeignKey):
                attr_name = '{}_id'.format(attr.name)
                print('attr_name:{}'.format(attr_name))
            else:
                attr_name = attr.name
            attr_str_list.append(attr_name)
        return attr_str_list

    def get_one_object(self, **filters):
        # 获取self对象所在的模型类
        try:
            obj = self.get(**filters)
        except self.model.DoesNotExist:
            obj = None
        return obj

    def create_one_object(self, **kwargs):
        # 对数据库操作
        print('BASE:{}'.format(kwargs))
        valid_fields = self.get_all_valid_fields()
        kws = copy.copy(kwargs)
        for key in kws:
            if key not in valid_fields:
                # 根据用户名查找账户信息
                kwargs.pop(key)
        model_class = self.model
        print('BASE:{}'.format(model_class))
        obj = model_class(**kwargs)
        print('BASEobj:{}'.format(obj))
        obj.save()
        print('BASEreturn:')
        return obj

    def get_object_list(self,
                        filters={},
                        order_by=('-pk',)):
        print(filters)
        object_list = self.filter(**filters).order_by(*order_by)
        return object_list
