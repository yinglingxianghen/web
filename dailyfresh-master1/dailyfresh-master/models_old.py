from django.db import models
from db.base_model import BaseModel
from utils.get_hash import get_hash


# Create your models here.

class PassportManager(models.Manager):
    def add_one_passport(self, username, password, email):
        # 获取self对象所在的模型类
        model_class = self.model
        # 创建一个model_class类对象
        obj = model_class(username=username,
                          password=get_hash(password),
                          email=email)
        obj.save()
        return obj

    def get_one_passport(self, username, password=None):
        # 对数据库操作
        try:
            if password is None:
                # 根据用户名查找账户信息
                obj = self.get(username=username)
            else:
                # 根据用户名和密码查找账户信息
                obj = self.get(username=username, password=get_hash(password))
                print("mod" + username)
                print("mod" + get_hash(password))
        except self.model.DoesNotExist:
            print("mod  dosnot")
            obj = None
        # except Exception as e:
        #     print("e"+e)
        return obj


class Passport(BaseModel):
    username = models.CharField(max_length=20,
                                verbose_name='账户名称')
    password = models.CharField(max_length=40,
                                verbose_name='密码')
    email = models.EmailField(verbose_name='邮箱')

    objects = PassportManager()  # 自定义管理模型类对象

    class Meta:
        db_table = 's_user_account'


class AddressManager(models.Manager):
    def get_one_address(self, passport_id):
        try:
            addr = self.get(passport_id=passport_id,
                            is_default=True)
        except self.model.DoesNotExist:
            addr = None
        return addr

    def add_one_address(self,
                        passport_id,
                        recipient_name,
                        recipient_addr,
                        recipient_phone,
                        zip_code):
        # 添加收货地址
        addr = self.get_one_address(passport_id=passport_id)
        # 获取self对象所在的模型类
        model_class = self.model
        if addr is None:
            addr = model_class(passport_id=passport_id,
                               recipient_name=recipient_name,
                               recipient_addr=recipient_addr,
                               recipient_phone=recipient_phone,
                               zip_code=zip_code,
                               is_default=True)
        else:
            addr = model_class(passport_id=passport_id,
                               recipient_name=recipient_name,
                               recipient_phone=recipient_phone,
                               recipient_addr=recipient_addr,
                               zip_code=zip_code)
        addr.save()
        return addr


class Address(BaseModel):
    passport = models.ForeignKey('Passport',
                                 verbose_name='所属账户')
    recipient_name = models.CharField(max_length=24,
                                      verbose_name='收件人')
    recipient_addr = models.CharField(max_length=256,
                                      verbose_name='收件地址')
    recipient_phone = models.CharField(max_length=11,
                                       verbose_name='练习电话')
    zip_code = models.CharField(max_length=6,
                                verbose_name='邮政编码')
    is_default = models.BooleanField(default=False,
                                     verbose_name='是否默认')

    objects = AddressManager()

    class Meta:
        db_table = 's_user_address'
