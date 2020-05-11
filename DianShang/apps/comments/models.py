from django.db import models
from shop.models import Product
from orders.models import Order
from django.contrib.auth.models import User
from django.db.models import Count

class TagManager(models.Manager):
    # 1、读取标签及此标簦文章数
    def tag_articlennum_list(self):
        tag_commentsnum_list = self.annotate(commentsnum=Count('comments')).order_by('-commentsnum')
        # tags=[]
        # tags = {t.name: t.num_post for t in alltags}
        return tag_commentsnum_list


# tag（标签）
class Tag(models.Model):
    name = models.CharField(max_length=30, verbose_name=u'标签名称')

    objects = TagManager()

    class Meta:
        verbose_name = u'标签'
        verbose_name_plural = verbose_name
        ordering = ('-id',)
    def __str__(self):
        return self.name


# 评价模型
class Comments(models.Model):
    content = models.TextField(verbose_name=u'评价内容')
    date_publish = models.DateTimeField(auto_now_add=True, verbose_name=u'发布时间')
    user = models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'用户')
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'邮箱')
    product = models.ForeignKey(Product,on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'文章')
    order = models.ForeignKey(Order,on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'订单')
    tag =  models.ManyToManyField(Tag, blank=True, null=True, verbose_name=u'标签')
    pid = models.ForeignKey('self',on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'父级评价')
    is_display = models.BooleanField(default=True, verbose_name=u'是否显示')
    is_showname = models.BooleanField(default=True, verbose_name=u'是否匿名')
    #1、好评、0、中评、-1、差评
    is_good = models.IntegerField(default=1, verbose_name=u'是否好评')
    star_count = models.IntegerField(default=5, verbose_name=u'商品质量星数')
    service_count = models.IntegerField(default=5, verbose_name=u'服务星数')
    kuaiti_count = models.IntegerField(default=5, verbose_name=u'快递星数')



    class Meta:
        verbose_name = u'评价'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)

class Commentspic(models.Model):
    comment = models.ForeignKey(Comments,on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'评价')
    picurl = models.ImageField(upload_to='comment/%Y/%m/%d', blank=True,verbose_name=u'图片')
    remark = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'备注')