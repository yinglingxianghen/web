from django.db import models
from db.base_model import BaseModel
from utils.get_hash import get_hash
from db.base_manager import BaseManager


# Create your models here.

class PassportManager(BaseManager):
    def add_one_passport(self, username, password, email):
        obj = self.create_one_object(username=username,
                                       password=get_hash(password),
                                       email=email)
        return obj

    def get_one_passport(self, username, password=None):
        if password is None:
            # 根据用户名查找账户信息
            obj = self.get_one_object(username=username)
        else:
            # 根据用户名和密码查找账户信息
            obj = self.get_one_object(username=username,
                                      password=get_hash(password))
            # print("mod" + username)
            # print("mod" + get_hash(password))
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


class AddressManager(BaseManager):
    def get_one_address(self, passport_id):
        addr = self.get_one_object(passport_id=passport_id, is_default=True)
        return addr

    def add_one_address(self,
                        passport_id,
                        recipient_name,
                        recipient_addr,
                        recipient_phone,
                        zip_code):
        # 添加收货地址
        addr = self.get_one_address(passport_id=passport_id)
        is_default = False
        if addr is None:
            is_default = True
        addr = self.create_one_object(passport_id=passport_id,
                                      recipient_name=recipient_name,
                                      recipient_addr=recipient_addr,
                                      recipient_phone=recipient_phone,
                                      zip_code=zip_code,
                                      is_default=is_default)
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
