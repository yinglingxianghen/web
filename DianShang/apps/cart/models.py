from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
from decimal import Decimal
from django.conf import settings
from coupons.models import Coupon

# Create your models here.

class CartManager(models.Manager):
    """
    购物车模型管理类
    """
    def get_cart_by_id(self, user, products):
        """
        根据用户id和商品id查询用户购物车中的信息
        :param user_id: 用户id
        :param products_id: 商品id
        :return: Cart
        """
        return self.get(user=user, products=products)

    def get_cart_list(self, user, products_id_list=None):
        """
        通过用户id返回购物车详情， 并包括商品名称 商品价格 商品单位 商品图片
        :param user_id: 用户id
        :param products_id_list: 商品id列表
        :return: 购物车详情QuerySet
        """
        if products_id_list:
            return self.filter(user=user,products_id__in=products_id_list)
        return self.filter(user=user)

    def get_cart_amount(self, user, products_id_list=None):
        """
        求指定商品购物车的总价
        :param user:
        :param products_id_list:
        :return:
        """
        amount=0
        cart_list= self.filter(user=user,products_id__in=products_id_list)
        for cart in cart_list:
            amount += cart.products_count*cart.products.saleprice
        return amount

    def add(self, user, products, quantity=1):
        """
        Add a product to the cart or update its quantity.
        """
        try:
            cart = self.get(user__id=user.id, products__id=products.id)
            if cart:
                cart.products_count = cart.products_count + int(quantity)
                cart.save()
        except Exception:
            self.create(user=user, products=products, products_count=quantity)


    def remove(self,user, products):
        """
        Remove a product from the cart.
        """
        self.filter(user=user, products_id__in=products).delete()

    def get_cart_count(self, user):
        """
        根据用户id和商品id查询用户购物车中的信息
        :param user_id: 用户id
        :param products_id: 商品id
        :return: Cart
        """
        cart_count = self.filter(user=user).count()
        if cart_count == None:
           cart_count=0
        return cart_count



class Cart(models.Model):
    """
    购物车模型类
    """
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name="所属用户")
    products = models.ForeignKey(Product,on_delete=models.CASCADE, verbose_name="商品")
    products_count = models.IntegerField(verbose_name="商品数目")

    objects = CartManager()


    def get_total_price(self):
        total_price = self.products.saleprice * self.products_count
        return total_price