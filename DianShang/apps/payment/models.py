from django.db import models
from orders.models import Order
from django.contrib.auth.models import User

# Create your models here.
class Paylist(models.Model):
    PAY_TYPE = (
        (1, '微信支付'),
        (2, '支付宝'),
        (3, '银联支付')
    )
    STATUS = (
        (1, '支付成功'),
        (2, '已退款'),
        (3, '取消')
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True, blank=True)
    status = models.SmallIntegerField( choices=STATUS, default=1,verbose_name="状态")
    paytime = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")
    desc = models.CharField(null=True, blank=True, max_length=1024, verbose_name="支付信息")
    payno = models.CharField(null=True, blank=True, max_length=40, verbose_name="支付单号")
    paytype = models.SmallIntegerField( choices=PAY_TYPE,null=True, blank=True, verbose_name="支付类型")
    payamount = models.DecimalField(max_digits = 5,decimal_places = 2, verbose_name="支付金额")

    class Meta:
        verbose_name = '支付信息'

    def __str__(self):
        return '{}'.format(self.payno)