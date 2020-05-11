# -*- coding:utf-8 -*-
from django.db import models
from datetime import datetime
from shop.models import Product
from orders.models import Order
from django.contrib.auth.models import User

class Coupon(models.Model):
    """
    This table contains coupon codes
    A user can get a discount offer on course if provide coupon code
    """


    coupon_type = ((1, '单一商品'),  (2, '全部商品'),)
    code = models.CharField(max_length=32, db_index=True,verbose_name='兑换码')
    description = models.CharField(max_length=255, null=True, blank=True,verbose_name='说明')
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    percentage_discount = models.IntegerField(default=0,verbose_name='优惠折扣')
    preamount = models.IntegerField(default=0,verbose_name='优惠金额')
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True,verbose_name='生成时间')
    is_active = models.BooleanField(default=True,verbose_name='是否有效')
    expiration_date = models.DateTimeField(null=True, blank=True,verbose_name='失效时间')
    type = models.CharField(max_length=2,default=1,choices=coupon_type, db_index=True,verbose_name='类型')
    maxnum = models.IntegerField(null=True, blank=True,verbose_name='最大数量')
    remark = models.CharField(max_length=400, null=True, blank=True, db_index=True, verbose_name='备注')

    class Meta(object):
        verbose_name = u'优惠券主表'
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return "[Coupon] code: {} course: {}".format(self.code, self.course_id)


class CouponRedemption(models.Model):
    """
    This table contain coupon redemption info
    #记录优惠券领用及使用情况
    """
    CHOICESTATUS=(('1','有效'),('2','已使用'),('3','失效'),('4','删除'),)

    order = models.ForeignKey(Order,on_delete=models.SET_NULL, db_index=True, null=True, blank=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True, db_index=True, blank=True)
    coupon = models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True, db_index=True)
    usedate = models.DateTimeField(null=True, blank=True,verbose_name='使用时间')
    getdate = models.DateTimeField(null=True, blank=True,verbose_name='领用时间')
    status =  models.CharField(max_length=2,default=1, db_index=True,choices=CHOICESTATUS,verbose_name='状态') #1、有效，2、已使用，3、失效
    percentage_discount = models.IntegerField(default=0, verbose_name='优惠折扣')

    class Meta(object):
        verbose_name = u'优惠券明细表'
        verbose_name_plural = verbose_name
    @classmethod
    def use_coupon_redemption(cls, user, order):
        coupon_redemption = cls.objects.filter(user=user, status=1)
        if coupon_redemption:
            coupon_redemption.order = order
            coupon_redemption.usedate = datetime.now()
            coupon_redemption.status =2
            coupon_redemption.save()