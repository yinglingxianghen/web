from django.db import models
from django.urls import reverse
#from parler.models import TranslatableModel, TranslatedFields
from DjangoUeditor.models import UEditorField
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    STATUS_CHOICE=(('1', u'正常'),
            ('0', u'冻结'),)

    name = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'名称')
    slug = models.SlugField(max_length=200, default='',db_index=True, unique=True,verbose_name=u'标签')
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True, related_name='up_category',verbose_name=u'上级分类')
    created = models.DateTimeField(auto_now_add=True,null=True,blank=True,verbose_name=u'创建')
    updated = models.DateTimeField(auto_now=True,null=True,blank=True)
    status = models.CharField(max_length=1, default=1, db_index=True,choices=STATUS_CHOICE,verbose_name=u'状态')

    class Meta:
        # ordering = ('name',)
        verbose_name = u'分类表'
        verbose_name_plural = u'分类表'

    def __str__(self):
        return self.name

class Saleproperty(models.Model):
    pname=models.CharField(max_length=200,null=True,blank=True)
    desc=models.CharField(max_length=800, null=True,blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE, null=True,blank=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = '分类销售属性表'
        verbose_name_plural = '分类销售属性表'

    def __str__(self):
        return self.pname

class Categoryproperty(models.Model):
    displayname=models.CharField(max_length=200,null=True,blank=True)
    desc=models.CharField(max_length=800, null=True,blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE, null=True,blank=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = '分类扩展属性表'
        verbose_name_plural = '分类扩展属性表'

    def __str__(self):
        return self.displayname

class Categorypropertyvalue(models.Model):
    valuename=models.CharField(max_length=200,null=True,blank=True)
    desc=models.CharField(max_length=800, null=True,blank=True)
    categoryproperty = models.ForeignKey(Categoryproperty,on_delete=models.CASCADE, null=True,blank=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = '分类扩展属性值表'
        verbose_name_plural = '分类扩展属性值表'

    def __str__(self):
        return self.valuename

class Supplier(models.Model):
    STATUS_CHOICE = (('1', u'正常'),
            ('0', u'冻结'),)
    KIND_CHOICE = (('1', u'手机通讯'),
            ('2', u'电脑数码'),
            ('3', u'家用电器'),
            ('4', u'服饰鞋包'),
            ('5', u'厨房卫浴'),
            ('6', u'家居家装'),
                     )
    name = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'名称')
    phone=models.CharField(max_length=50, null=True,blank=True,verbose_name=u'电话')
    linkman=models.CharField(max_length=200, null=True,blank=True,verbose_name=u'联系人')
    desc=models.CharField(max_length=800,null=True,blank=True,verbose_name=u'介绍')
    kind=models.CharField(max_length=2,default=1, db_index=True,choices=KIND_CHOICE,verbose_name=u'类别')
    brands=models.CharField(max_length=50, null=True,blank=True,verbose_name=u'品牌')
    image = models.ImageField(upload_to='supplier/', blank=True,verbose_name=u'图片')
    styimg = models.ImageField(upload_to='supplier/', blank=True,verbose_name=u'主款图片')
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updated = models.DateTimeField(auto_now=True, null=True,blank=True)
    status = models.CharField(max_length=1, default=1, db_index=True,choices=STATUS_CHOICE,verbose_name=u'状态')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        # ordering = ('name',)
        verbose_name = '供应商'
        verbose_name_plural = 'suppliers'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('productbysuplier', args=[self.id])

class Store(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'名称')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name=u'电话')
    mobile = models.CharField(max_length=20, null=True, blank=True, verbose_name=u'手机')
    linkman = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'联系人')
    desc = models.CharField(max_length=800, null=True, blank=True, verbose_name=u'介绍')
    address = models.CharField(max_length=800, null=True, blank=True, verbose_name=u'地址')
    supplier = models.ManyToManyField(Supplier)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    status = models.CharField(max_length=1, default=1, db_index=True,  verbose_name=u'状态')
    appid =  models.CharField(max_length=200, null=True, blank=True, verbose_name=u'appid')
    remark = models.CharField(max_length=800, null=True, blank=True, verbose_name=u'备注')
    class Meta:
        # ordering = ('name',)
        verbose_name = '店主'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICE = ((1, u'上架'),
                     (0, u'下架'),)
    name = models.CharField(max_length=200, verbose_name=u'名称')
    slug = models.SlugField(max_length=200,null=True,blank=True, db_index=True,verbose_name=u'标签')
    description = UEditorField(u'内容', height=400, width=600, default='', imagePath="upload/",
                                toolbars='mini', filePath='upload/', blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,verbose_name=u'分类')
    saleproperty = models.ForeignKey(Saleproperty, on_delete=models.CASCADE,null=True,blank=True,verbose_name=u'销售标识')
    productno = models.CharField(max_length=200,null=True,blank=True, db_index=True,verbose_name=u'编号')
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True,verbose_name=u'小图')
    largeimage = models.ImageField(upload_to='products/%Y/%m/%d', blank=True,verbose_name=u'大图')
    price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name=u'原价')
    saleprice = models.DecimalField(max_digits=10,null=True,blank=True, decimal_places=2,verbose_name=u'销售价')
    stock = models.PositiveIntegerField(verbose_name=u'库存')
    available = models.BooleanField(default=True,verbose_name=u'有效')
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updated = models.DateTimeField(auto_now=True, null=True,blank=True)
    supplier =  models.ForeignKey(Supplier,on_delete=models.CASCADE, null=True,blank=True,verbose_name=u'供应商')
    remark =  models.CharField(max_length=400,null=True,blank=True, verbose_name=u'简要介绍')
    viewnum = models.IntegerField(default=0, verbose_name=u'浏览数')
    salenum = models.IntegerField(default=0, verbose_name=u'销售数')
    commentnum = models.DecimalField(max_digits = 5,decimal_places = 2,verbose_name=u'好评')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True, verbose_name=u'店主')
    status = models.IntegerField(default=1, choices=STATUS_CHOICE, verbose_name=u'状态')
    unit = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'单位')
    spec = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'规格')
    sale_num = models.DecimalField(max_digits = 5,decimal_places = 2,default=0, verbose_name=u'销售量')
    class Meta:
        ordering = ('-created',)
        verbose_name = '商品'
        # index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('product_detail', args=[self.id, self.slug])


class Productproperty(models.Model):
    name=models.CharField(max_length=200,null=True,blank=True)

    product = models.ForeignKey(Product,on_delete=models.CASCADE, null=True,blank=True)
    categoryproperty = models.ForeignKey(Categoryproperty, on_delete=models.CASCADE, null=True, blank=True)
    categorypropertyvalue = models.ForeignKey(Categorypropertyvalue, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = '商品扩展属性'
        verbose_name_plural = '商品扩展属性'

    def __str__(self):
        return str(self.id)

class Productpic(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'商品')
    picurl = models.ImageField(upload_to='product/%Y/%m/%d', blank=True, verbose_name=u'图片')
    remark = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'备注')

#新品推荐
class Recommend(models.Model):
    STATUS_CHOICE = (('1', u'正常'),
                     ('0', u'冻结'),)
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE,verbose_name=u'供应商')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,verbose_name=u'商品')
    expiredate = models.DateTimeField(auto_now_add=True,null=True,blank=True,verbose_name=u'有效期')
    updated = models.DateTimeField(auto_now=True, null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    desc = models.CharField(max_length=800,null=True,blank=True,verbose_name=u'描述')
    status = models.CharField(max_length=1,default=1, db_index=True,choices=STATUS_CHOICE,verbose_name=u'状态')

    class Meta:
        # ordering = ('name',)
        verbose_name = '新品推荐'
        verbose_name_plural = '新品推荐'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_list_by_recommend', args=[self.slug])


class BrowseHistory(models.Model):
    """
    历史浏览商品模型类
    """
    products = models.ForeignKey(Product, on_delete=models.CASCADE,verbose_name="所述商品")
    users = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name="所属用户")


class Ad(models.Model):
    title = models.CharField(max_length=50, verbose_name=u'广告标题')
    description = models.CharField(max_length=200, verbose_name=u'广告描述')
    image = models.ImageField(upload_to='ad/%Y/%m', verbose_name=u'图片路径')
    callback_url = models.URLField(null=True, blank=True, verbose_name=u'回调url')
    date_publish = models.DateTimeField(auto_now_add=True, verbose_name=u'发布时间')
    index = models.IntegerField(default=999, verbose_name=u'排列顺序(从小到大)')
    location = models.CharField(max_length=50, verbose_name=u'广告位置')  # a1,a2,a3,b1,b2,b3,c1,c2,c3,c4,d1,d2,....
    is_display = models.BooleanField(default=False, verbose_name=u'是否显示')
    bgcolor = models.CharField(max_length=20, verbose_name=u'背景色')
    class Meta:
        verbose_name = u'广告'
        verbose_name_plural = verbose_name
        ordering = ['index', 'id']

    def __unicode__(self):
        return self.title