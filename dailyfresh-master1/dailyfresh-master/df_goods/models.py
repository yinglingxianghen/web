from django.db import models
from db.base_model import BaseModel
from db.base_manager import BaseManager
from tinymce.models import HTMLField
from df_goods.enums import *
# Create your models here.


class GoodsLogicManager(BaseManager):
    def get_goods_by_id(self, goods_id):
        # 根据商品ID查询商品信息
        goods = self.get_one_object(id=goods_id)
        # images是Image类型或查询集
        images = Image.objects.get_image_by_goods_id(goods_id=goods_id)
        # img_url给goods对象添加属性
        goods.img_url = images.img_url
        print(goods.img_url)
        return goods


class GoodsManager(BaseManager):
    '''商品模型管理器类'''
    def get_goods_by_id_with_image(self, goods_id):
        '''根据商品的id查询商品信息，并查询其详情图片'''
        # 根据商品id查询出其详情图片
        goods = self.get_goods_by_id(goods_id=goods_id)

        # 此处images是Image类型或者QuerySet类型
        images = Image.objects.get_image_by_goods_id(goods_id=goods_id)

        # 给goods增加一个对象属性img_url, 记录商品详情图片
        goods.img_url = images.img_url
        # 返回goods
        return goods

    def get_goods_by_id(self, goods_id):
        '''根据商品id查询商品信息'''
        # 根据商品的id查询商品信息
        goods = self.get_one_object(id=goods_id)
        return goods

    def get_goods_by_type(self,
                          goods_type_id,
                          limit=None,
                          sort='default'):
        order_by = ('-pk',)  # 从大到小排列
        if sort == 'new':
            print('-------------------time--------------------')
            order_by = ('-create_time',)
        elif sort == 'price':
            order_by = ('goods_price',)  # 从小到大排列
        elif sort == 'hot':
            order_by = ('-goods_sales',)
        goods_li = self.get_object_list(filters={'goods_type_id': goods_type_id},
                                        order_by=order_by)
        if limit:
            goods_li = goods_li[:limit]
        return goods_li


# Create your models here.
class Goods(BaseModel):
    goods_type_choice = (
        (FRUIT, GOODS_TYPE[FRUIT]),  # 元组中第一元素是val, 第二个元素显示的信息
        (SEAFOOD, GOODS_TYPE[SEAFOOD]),
        (MEAT, GOODS_TYPE[MEAT]),
        (EGGS, GOODS_TYPE[EGGS]),
        (VEGETABLES, GOODS_TYPE[VEGETABLES]),
        (FROZEN, GOODS_TYPE[FROZEN])
    )

    goods_status_choice = (
        (ONLINE, GOODS_STATUS[ONLINE]),
        (OFFLINE, GOODS_STATUS[OFFLINE]),
    )
    goods_type_id = models.SmallIntegerField(choices=goods_type_choice,
                                             default=FRUIT,
                                             verbose_name='商品类型')
    goods_name = models.CharField(max_length=20,
                                  verbose_name='商品名称')
    goods_sub_title = models.CharField(max_length=128,
                                       verbose_name='商品副标题')
    goods_price = models.DecimalField(max_digits=10,
                                      decimal_places=2,
                                      verbose_name='商品价格')
    transit_price = models.DecimalField(max_digits=10,
                                        decimal_places=2,
                                        verbose_name='商品运费')
    goods_unite = models.CharField(max_length=20,
                                   verbose_name='商品单位')
    goods_info = HTMLField(verbose_name='商品描述')
    goods_image = models.ImageField(upload_to='goods',
                                    verbose_name='商品图片')
    goods_stock = models.IntegerField(default=0,
                                      verbose_name='商品库存')
    goods_sales = models.IntegerField(default=0,
                                      verbose_name='商品销量')
    # 1:上线商品 2:下线商品
    goods_status = models.SmallIntegerField(choices=goods_status_choice,
                                            default=ONLINE,
                                            verbose_name='商品状态')

    objects = GoodsManager()
    objects_logic = GoodsLogicManager()  # 查询商品信息，需要详情图片时通过该

    class Meta:
        db_table = 's_goods'

class ImageManager(BaseManager):
    def get_image_by_goods_id(self, goods_id):
        images = self.get_object_list(filters={'goods_id':goods_id}) # 返回值是一个查询集
        if images.exists():
            # 查询集中有图片数据
            # 取出images查询集中的第一个元素，重新赋值给images
            # 此时images对象的类型为Image
            images = images[0]
            # print('image'+images)
        else:
            # 查询集中没有图片
            # 此时images的类型为QuerySet,给images增加一个属性img_url,防止出错
            images.img_url = ''
        # 返回images,返回的类型可能是Image或这QuerySet,但都有img_url属性
        return images


class Image(BaseModel):
    goods = models.ForeignKey('Goods',
                              verbose_name='所属商品')
    img_url = models.ImageField(upload_to='goods',
                                verbose_name='图片路径')

    objects = ImageManager()

    class Meta:
        db_table = 's_goods_image'
