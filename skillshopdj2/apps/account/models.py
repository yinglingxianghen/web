# -*- coding:utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User,on_delete='')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=u'生日')
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True, verbose_name=u'图')
    score = models.IntegerField(default=0, verbose_name=u'积分')
    grender = models.CharField(max_length=1,default='o', verbose_name=u'性别')
    address= models.CharField(max_length=200,default='', verbose_name=u'地址')
    email = models.CharField(max_length=30,default='', verbose_name=u'邮箱')
    moible = models.CharField(max_length=15,default='', verbose_name=u'手机')

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)


#黑名单
class BlackUser(models.Model):
    user= models.OneToOneField(User,on_delete='')
    status=models.CharField(max_length=1,default='1', verbose_name=u'状态')
    lockdate=models.DateTimeField(auto_now=True)
