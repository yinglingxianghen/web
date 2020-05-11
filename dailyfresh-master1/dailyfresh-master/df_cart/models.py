from django.db import models
from db.base_model import BaseModel
from db.base_manager import BaseManager
from df_goods.models import Goods
from django.db.models import Sum  # 导入sum聚合类


# Create your models here.

class CartManager(BaseManager):
    def get_one_cart_info(self, passport_id, goods_id):
        # 查询一条购物车信息
        cart_info = self.get_one_object(passport_id=passport_id, goods_id=goods_id)
        return cart_info

    def add_one_cart_info(self, passport_id, goods_id, goods_count):
        # 满足条件时将数据插到数据库
        print('add_one_cart_info:{}'.format(passport_id))
        cart_info = self.get_one_cart_info(passport_id=passport_id, goods_id=goods_id)
        goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
        print('cart_info:{}'.format(cart_info))
        if cart_info:
            # 商品已经添加过，更新商品数量
            total_count = cart_info.goods_count + goods_count
            print('total_count:{}'.format(total_count))
            print('goods.goods_stock:{}'.format(goods.goods_stock))
            if total_count <= goods.goods_stock:
                cart_info.goods_count = total_count
                cart_info.save()
                return True
            else:
                # 库存不足
                return False
        else:
            # 商品没有添加过
            print('egoods_count:{}'.format(goods_count))
            print('egoods.goods_stock:{}'.format(goods.goods_stock))
            if goods_count <= goods.goods_stock:
                print('ebefore')
                self.create_one_object(passport_id=passport_id, goods_id=goods_id, goods_count=goods_count)
                print('eafter')
                return True
            else:
                return False

    def get_cart_count_by_passport(self, passport_id):
        '''根据passport_id查询用户购物车中商品的总数'''
        # select sum(goods_count) from s_cart where passport_id=passport_id
        res_dict = self.filter(passport_id=passport_id).aggregate(Sum('goods_count')) # {'goods_count__sum':结果}
        # {'goods_count__sum':None}
        if res_dict['goods_count__sum'] is None:
            res = 0
        else:
            res = res_dict['goods_count__sum']
        return res


class Cart(BaseModel):
    passport = models.ForeignKey('df_user.Passport',
                                 verbose_name='账户名称')
    goods = models.ForeignKey('df_goods.Goods',
                              verbose_name='商品名称')
    goods_count = models.IntegerField(default=1,
                                      verbose_name='商品数目')
    objects = CartManager()

    class Meta:
        db_table = 's_cart'
