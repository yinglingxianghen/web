from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
from shop.models import Product

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    #photo = models.ImageField(upload_to='users/%Y/%m/%d',default='/static/img/avatar.png', blank=True)
    photo = models.TextField(null=True, blank=True,verbose_name="头像")
    gender = models.CharField(max_length=6, choices=(("male", u"男"), ("female", "女"), ("O", "秘密")), default="O",
                              verbose_name="性别")
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")
    score = models.IntegerField(default=0,verbose_name='积分')

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)

class UserFav(models.Model):
    """
    用户收藏
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="用户")
    products = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品", help_text="商品id")
    addtime = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name
        unique_together = ("user", "products")

    def __str__(self):
        return self.user.username

class UserMessage(models.Model):
    """
    用户留言
    """
    MESSAGE_CHOICES = (
        (1, "留言"),
        (2, "投诉"),
        (3, "询问"),
        (4, "售后")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="用户")
    messagetype = models.IntegerField(default=1, choices=MESSAGE_CHOICES, verbose_name="留言类型",
                                      help_text=u"留言类型: 1(留言),2(投诉),3(询问),4(售后)")
    subject = models.CharField(max_length=100, default="", verbose_name="主题")
    message = models.TextField(default="", verbose_name="留言内容", help_text="留言内容")
    file = models.FileField(upload_to="message/", verbose_name="上传的文件", help_text="上传的文件")
    addtime = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    senduser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senduser',verbose_name="发送人")

    class Meta:
        verbose_name = "用户留言"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.subject




class Provinces(models.Model):
    """
    省
    """
    province_code = models.CharField(max_length=30, default="", verbose_name="省份code")
    province = models.CharField(max_length=50, default="", verbose_name="省份")

    class Meta:
        db_table = "provinces"  # 更改表名
        verbose_name = "省"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.province

class Cities(models.Model):
    """
    市
    """
    city_code = models.CharField(max_length=30, default="", verbose_name="市code")
    city = models.CharField(max_length=50, default="", verbose_name="市")
    province_code = models.CharField(max_length=30, default="", verbose_name="省份code")

    class Meta:
        db_table = "cities"  # 更改表名
        verbose_name = "市"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.city

class Areas(models.Model):
    """
    区县
    """
    area_code = models.CharField(max_length=30, default="", verbose_name="区县code")
    area = models.CharField(max_length=50, default="", verbose_name="区县")
    city_code = models.CharField(max_length=30, default="", verbose_name="市code")

    class Meta:
        db_table = "areas"  # 更改表名
        verbose_name = "区县"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.area

class UserAddress(models.Model):
    """
    用户收货地址
    """
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name="用户" )
    provinces = models.ForeignKey(Provinces, on_delete=models.CASCADE, verbose_name="省")
    city = models.ForeignKey(Cities, on_delete=models.CASCADE, verbose_name="市")
    area = models.ForeignKey(Areas, on_delete=models.CASCADE, verbose_name="区县")
    address = models.CharField(max_length=100, default="", verbose_name="详细地址")
    signername = models.CharField(max_length=100, default="", verbose_name="签收人")
    post = models.CharField(max_length=6, default="", verbose_name="邮编")
    mobile = models.CharField(max_length=11, default="", verbose_name="手机")
    tel = models.CharField(max_length=11, default="", verbose_name="电话")
    flag = models.CharField(max_length=2, default="1", verbose_name="是否默认地址")
    addtime = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "收货地址"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.address
