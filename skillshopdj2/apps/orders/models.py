# -*- coding:utf-8 -*-
from django.db import models
from seckill.models import SaleProducts
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    STATUS_CHOICE = (('1', u'生成'),
                     ('0', u'取消'),
                     ('2', u'待支付'),
                     ('3', u'已支付'),
                     ('3', u'退款'),
                     ('4', u'评价'),)
    name = models.CharField( max_length=50, verbose_name=u'姓名')
    email = models.EmailField( null=True, blank=True,verbose_name=u'邮箱')
    address = models.CharField( max_length=250, verbose_name=u'地址')
    postal_code = models.CharField( null=True, blank=True,max_length=20, verbose_name=u'邮编')
    city = models.CharField(null=True, blank=True, max_length=100, verbose_name=u'城市')
    mobile = models.CharField(null=True, blank=True,max_length=20, verbose_name=u'手机')
    user = models.ForeignKey(User,on_delete='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(default=1, max_length=1,choices=STATUS_CHOICE, verbose_name=u'状态')
    amount= models.DecimalField(default=0,max_digits=5,decimal_places=2, verbose_name=u'金额')
    coupon = models.CharField(max_length=20,null=True, blank=True, verbose_name=u'优惠券')
    discount = models.IntegerField(default=0,
                                   validators=[MinValueValidator(0),
                                               MaxValueValidator(100)], verbose_name=u'折扣')
    reply_dump = models.CharField(null=True, blank=True,max_length=500, verbose_name=u'支付信息')
    reference_number = models.CharField(null=True, blank=True,max_length=20, verbose_name=u'支付单号')
    class Meta:
       pass

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())
        return total_cost - total_cost * (self.discount / Decimal('100'))

    @property
    def get_productname(self):
        """
        取名称
        """
        productnames = []
        # items = self.items_set.all()
        items = OrderItem.objects.filter(order_id=self.id)
        for item in items:
            productnames.append(item.product.title)
        return productnames


class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete='', related_name='items')
    product = models.ForeignKey(SaleProducts,on_delete='' )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity
