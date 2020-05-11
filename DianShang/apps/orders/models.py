from django.db import models
from shop.models import Product

from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Order(models.Model):
    PAY_CHOICES = (
        (4, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (1, '银联支付')
    )
    first_name = models.CharField(_('first name'), null=True,
                                  max_length=50)
    last_name = models.CharField(_('last name'), null=True,
                                 max_length=50)
    email = models.EmailField(_('e-mail'), null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True, blank=True)
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话")
    remark = models.CharField(null=True, blank=True, max_length=1024, verbose_name="备注")
    address = models.CharField(_('address'), null=True,
                               max_length=250)
    postal_code = models.CharField(_('postal code'), null=True, max_length=20)
    #（1、购物车2、待支付3、已购买4、已评介5、已退款0、已取消）
    status = models.CharField( max_length=2,default='1')
    city = models.CharField(_('city'), null=True,
                            max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    pay_type = models.IntegerField(default=1, choices=PAY_CHOICES, verbose_name=u'状态')
    trans_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')
    pay_no = models.CharField(max_length=128, default='', verbose_name='支付编号')
    amount = models.DecimalField(default=0.00,max_digits=8,decimal_places=2 )
    coupon = models.CharField(max_length=20,
                               null=True,
                               blank=True)
    discount = models.IntegerField(default=0,
                                   validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

    class Meta:
        ordering = ('-created',)

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
            productnames.append(item.product.name)
        return productnames

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order')
    product = models.ForeignKey(Product,on_delete=models.CASCADE, related_name='product')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity