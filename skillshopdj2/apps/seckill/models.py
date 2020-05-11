# -*- coding:utf-8 -*-
from django.db import models
from django.urls import reverse
import django.utils.timezone as timezone
from datetime import datetime,timedelta
#from parler.models import TranslatableModel, TranslatedFields
from DjangoUeditor.models import UEditorField
#类别
class Category(models.Model):
    STATUS_CHOICE=(('1', u'正常'),
            ('0', u'冻结'),)
    name = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'名称')
    slug = models.SlugField(max_length=200, default='',db_index=True, unique=True,verbose_name=u'标签')
    parent = models.ForeignKey('self',default=0,null=True,blank=True, on_delete='',related_name='child',verbose_name=u'上级分类')
    created = models.DateTimeField(auto_now_add=True,null=True,blank=True,verbose_name=u'创建')
    updated = models.DateTimeField(auto_now=True,null=True,blank=True)
    status = models.CharField(max_length=1, default=1, db_index=True,choices=STATUS_CHOICE,verbose_name=u'状态')

    class Meta:
        # ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('seckill:product_list_by_category', args=[self.slug])


#合作方
class Supplier(models.Model):
    STATUS_CHOICE = (('1', u'正常'),
            ('0', u'冻结'),)
    KIND_CHOICE = (('1', u'供货商'),
            ('1', u'物流公司'),
            ('2', u'其他'),
                     )
    name = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'名称')
    phone=models.CharField(max_length=50, null=True,blank=True,verbose_name=u'电话')
    linkman=models.CharField(max_length=200, null=True,blank=True,verbose_name=u'联系人')
    desc=models.CharField(max_length=800,null=True,blank=True,verbose_name=u'介绍')
    kind=models.CharField(max_length=2,default=1, db_index=True,choices=KIND_CHOICE,verbose_name=u'类别')
    brands=models.CharField(max_length=50, null=True,blank=True,verbose_name=u'品牌')
    image = models.ImageField(upload_to='supplier/', blank=True,verbose_name=u'图片')
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updated = models.DateTimeField(auto_now=True, null=True,blank=True)
    status = models.CharField(max_length=1, default=1, db_index=True,choices=STATUS_CHOICE,verbose_name=u'状态')
    class Meta:
        # ordering = ('name',)
        verbose_name = 'supplier'
        verbose_name_plural = 'suppliers'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('seckill:product_list_by_supplier', args=[self.slug])

#商品
class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True,unique=True,verbose_name=u'名称')
    slug = models.SlugField(max_length=200,null=True,blank=True, db_index=True,verbose_name=u'标签')
    description = UEditorField(u'内容', height=400, width=600, default='', imagePath="upload/",
                                toolbars='mini', filePath='upload/', blank=True)
    category = models.ForeignKey(Category,on_delete='')
    productno = models.CharField(max_length=200,null=True,blank=True, db_index=True,verbose_name=u'编号')
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True,verbose_name=u'小图')
    largeimage = models.ImageField(upload_to='products/%Y/%m/%d', blank=True,verbose_name=u'大图')
    price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name=u'原价')
    saleprice = models.DecimalField(max_digits=10,null=True,blank=True, decimal_places=2,verbose_name=u'销售价')
    stock = models.PositiveIntegerField(verbose_name=u'库存')
    available = models.BooleanField(default=True,verbose_name=u'有效')
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updated = models.DateTimeField(auto_now=True, null=True,blank=True)
    supplier =  models.ForeignKey(Supplier, null=True,blank=True,on_delete='',verbose_name=u'供应商')
    remark =  models.CharField(max_length=400,null=True,blank=True, verbose_name=u'简要介绍')

    class Meta:
        ordering = ('-created',)
        # index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('seckill:product_detail', args=[self.id, self.slug])



#秒杀商品
class SaleProducts(models.Model):
    STATUS_CHOICE = (('1', u'正常'),
                     ('0', u'冻结'),
                     ('2', u'过期'),)
    Defaultenddatetime=datetime.now()+timedelta(hours=1)
    title= models.CharField(max_length=200,null=True,blank=True, verbose_name=u'标题')
    protduct= models.ForeignKey(Product, null=True,blank=True,on_delete='', verbose_name=u'商品')
    status= models.CharField(max_length=1,null=True,blank=True,choices=STATUS_CHOICE, verbose_name=u'状态')
    marketprice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=u'市场价')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=u'秒杀价')
    startdatetime = models.DateTimeField(default=datetime.now(), verbose_name=u'开始时间' )
    enddatetime  = models.DateTimeField(default=Defaultenddatetime, verbose_name=u'结束时间')
    stock_total = models.IntegerField(default=0, verbose_name=u'总库存')
    remain_qty = models.IntegerField(default=0, verbose_name=u'可销售数')
    desc =  UEditorField(u'内容', height=400, width=600, default='', imagePath="upload/",
                                toolbars='mini', filePath='upload/', blank=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name=u'小图')

    def __str__(self):
        return self.title
#验证码库
class Ziku(models.Model):
    qustion = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'问题')
    answer = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'答案')