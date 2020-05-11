# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
#import weasyprint
# import pdfkit
from .models import Order, OrderItem
from shop.models import Product
# from .forms import OrderCreateForm
# from .tasks import order_created
from cart.models import Cart
from account.models import UserAddress
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from coupons.models import CouponRedemption
import datetime
from shop.recommender import Recommender
from django.db import transaction

'''
乐观锁创建订单
我们通过django事务atomic装饰、乐观锁创建订单，并在视图函数内部设置savepoint来完成创建订单过程中数据库的一些事务操作来解决下单并发问题。
业务逻辑：
    1、在向订单信息表df_order_info添加订单信息时，设置savepoint并记录sid
    # 设置事务保存点
    sid = transaction.savepoint()
    添加信息若出错，则直接直接回滚至savepoint，并返回{'status': 7, 'errmsg': '下单失败'}
    2、向订单商品表中来查询数据
     product = Product.objects.get(id=item['product'])
    若商品不存在，则直接回滚至savepoint，并返回 msg = '商品信息错误'
    若库存不足，则直接回滚至savepoint，并返回 msg = '商品库存不足'
    3、记录此时的库存量、然后修改库存量和销售量
    在更新操作时以乐观锁的方式更新库存量和销售量
    # update方法返回数字，代表更新的行数
    num=Product.objects.filter(id=item['product'], stock=orgin_stock).update(stock=new_stock, sales=new_sale_num)
   
    4、创建订单成功后删除购物车相关数据，并返回msg ='订单创建成功'
'''
@ transaction.atomic
def order_create(request):
    # cart = Cart(request)
    ids = request.GET.get('product_ids',request.POST.get('product_ids'))
    ids_list = ids.split(',')
    cart = Cart.objects.get_cart_list(request.user,ids_list)
    #求指定商品购物车的总价
    cart_amount = Cart.objects.get_cart_amount(request.user,ids_list)
    useraddress = UserAddress.objects.filter(user=request.user).order_by('-flag')
    # 取优惠券，1、只对本课程有效的，2、全部课程有效的
    couponlist = []
    couponlist = CouponRedemption.objects.filter(status='1', user=request.user).filter(coupon__is_active=1). \
        filter(coupon__type=1).filter(coupon__expiration_date__gt=datetime.datetime.now()).select_related()

    if request.method == 'POST':
        prov = request.POST.get('prov')
        address = request.POST.get('address')
        signername = request.POST.get('signername')
        mobile = request.POST.get('mobile')
        coupan_id = request.POST.get('coupan_id', 0)
        coupan_amount = request.POST.get('coupan_amount',0)
        amount = float(request.POST.get('amount',0))
        trans_price = float(request.POST.get('trans_price',0))
        yun_fei = float(request.POST.get('yun_fei',0))
        total_price =float(cart_amount)

        coupan=[]
        if coupan_amount == '':
            coupan_amount=0
        else :
            coupan_amount =float(coupan_amount)
            coupan = CouponRedemption.objects.get(id=coupan_id)
            if coupan.preamount != coupan_amount :
                msg = '金额不对，请检查'
                return render(request, 'orders/order/create.html', locals())
        realamount=total_price-coupan_amount+yun_fei
        re_product = []

        # 设置事务保存点
        sid = transaction.savepoint()
        try:
            #页面传入价格与计算价格比较
            if realamount == amount :
                # 向order中添加一条记录
                order=Order.objects.create(user=request.user,first_name=signername,status='2',city=prov,address=address,mobile=mobile,
                                     coupon = coupan,amount=realamount,discount=coupan_amount,trans_price=trans_price)
                #对每一个商品扣减库存和保存到订单明细表中
                for item in cart:
                    # 根据id获取商品的信息
                    try:
                        product = Product.objects.get(id=item.products.id)
                    except Product.DoesNotExist:
                        # 回滚事务到sid保存点
                        transaction.savepoint_rollback(sid)
                        msg = '商品信息错误'
                        return render(request, 'orders/order/create.html', locals())

                    # 判断商品的库存
                    if int(item.products_count) > product.stock:
                        # 回滚事务到sid保存点
                        transaction.savepoint_rollback(sid)
                        msg = '商品库存不足'
                        return render(request, 'orders/order/create.html', locals())
                    # 减少商品库存，增加销量
                    orgin_stock = product.stock
                    new_stock = orgin_stock - int(item.products_count)
                    new_sale_num = product.sale_num + int(item.products_count)

                    # update from Product
                    # set stock=<new_stock>, sale_num=<new_sale_num>
                    # where id=<product_id> and stock=<orgin_stock>
                    # update方法返回数字，代表更新的行数
                    num = Product.objects.filter(id=item.products.id, stock=orgin_stock).update(stock=new_stock, sale_num=new_sale_num)
                    #更新成功，num>=1,如无更新 num=0
                    if num == 0:
                        flag = 'fail'
                        # 回滚事务到sid保存点
                        transaction.savepoint_rollback(sid)
                        # 下单失败
                        msg = '下单失败'
                        return render(request, 'orders/order/create.html', locals())


                    # 订单中包含几个商品需要向order_detail中添加几条记录
                    order_detail=OrderItem.objects.create(order=order,
                                             product=item.products,
                                             price=item.products.saleprice,
                                             quantity=item.products_count)
                    #构造推荐商品列表
                    re_product.append(item.products)
                    flag = 'success'

                #商品扣减库存和保存到订单明细表成功后，将进入支付页面的相关数据处理
                #对购买商品时行评分，以便推荐
                r = Recommender()
                pro_bought = r.products_bought(re_product)
                # clear the cart
                Cart.objects.remove(request.user,ids_list)
                # launch asynchronous task
                #order_created.delay(order.id)
                # set the order in the session
                request.session['order_id'] = order.id
                # redirect to the payment
                #return redirect(reverse('payment:paychoice'))
                order_id = order.id
                return render(request, 'pay/pay.html', locals())
            else:
                msg = '金额不对，请检查'
        except Exception as e:
            # 回滚事务到sid保存点
            transaction.savepoint_rollback(sid)
            msg = '下单失败'

    return render(request, 'orders/create.html', locals())


'''
悲观锁创建订单
我们通过django事务atomic装饰、悲观锁创建订单，
它指的是对数据被外界（包括本系统当前的其他事务，以及来自外部系统的事务处理）修改持保守态度，
因此，在整个数据处理过程中，将数据处于锁定状态。
悲观锁的实现，往往依靠数据库提供的锁机制（也只有数据库层提供的锁机制才能真正保证数据访问的排他性，
否则，即使在本系统中实现了加锁机制，也无法保证外部系统不会修改数据）。
并在视图函数内部设置savepoint来完成创建订单过程中数据库的一些事务操作来解决下单并发问题。
业务逻辑：
    1、在向订单信息表df_order_info添加订单信息时，设置savepoint并记录sid
    # 设置事务保存点
    sid = transaction.savepoint()
    添加信息若出错，则直接直接回滚至savepoint，并返回{'status': 7, 'errmsg': '下单失败'}
    2、通过悲观锁的方式来向订单商品表中来查询并修改数据
     updateproduct = Product.objects.select_for_update().get(id=item['product'])
    若商品不存在，则直接回滚至savepoint，并返回 msg = '商品信息错误'
    若库存不足，则直接回滚至savepoint，并返回 msg = '商品库存不足'
    3、记录此时的库存量、然后修改库存量和销售量
    在更新操作时以乐观锁的方式更新库存量和销售量
    # update方法返回数字，代表更新的行数    
    if updateproduct:
        updateproduct.stock=new_stock
        updateproduct.sales=new_sale_num
        updateproduct.save()    

    5、创建订单成功后删除购物车相关数据，并返回msg ='订单创建成功'
'''


@transaction.atomic
def order_createbybg(request):
    ids = request.GET.get('product_ids', request.POST.get('product_ids'))
    ids_list = ids.split(',')
    cart = Cart.objects.get_cart_list(request.user, ids_list)
    # 求指定商品购物车的总价
    cart_amount = Cart.objects.get_cart_amount(request.user, ids_list)
    useraddress = UserAddress.objects.filter(user=request.user).order_by('-flag')
    # 取优惠券，1、只对本课程有效的，2、全部课程有效的
    couponlist = []
    couponlist = CouponRedemption.objects.filter(status='1', user=request.user).filter(coupon__is_active=1). \
        filter(coupon__type=1).filter(coupon__expiration_date__gt=datetime.datetime.now()).select_related()

    if request.method == 'POST':
        prov = request.POST.get('prov')
        address = request.POST.get('address')
        signername = request.POST.get('signername')
        mobile = request.POST.get('mobile')
        coupan_amount = request.POST.get('coupan_amount', 0)
        amount = float(request.POST.get('amount', 0))
        trans_price = float(request.POST.get('trans_price', 0))
        yun_fei = float(request.POST.get('yun_fei', 0))
        total_price = float(cart.get_total_price())

        if coupan_amount == '':
            coupan_amount = 0
        else:
            coupan_amount = float(coupan_amount)

        realamount = total_price - coupan_amount + yun_fei
        re_product = []

        # 设置事务保存点
        sid = transaction.savepoint()
        try:
            # 页面传入价格与计算价格比较
            if realamount == amount:
                # 向order中添加一条记录
                order = Order.objects.create(user=request.user, first_name=signername, status='2', city=prov,
                                             address=address, mobile=mobile,
                                             coupon=cart.coupon, amount=realamount, discount=coupan_amount,
                                             trans_price=trans_price)
                # 对每一个商品扣减库存和保存到订单明细表中
                for item in cart:
                    # 更新库存时可能数据被锁定而更新失败，如失败，重新更新，给三次机会
                    for i in range(3):
                        # 根据id获取商品的信息
                        try:
                            updateproduct = Product.objects.select_for_update().get(id=item.products.id)
                        except Product.DoesNotExist:
                            # 回滚事务到sid保存点
                            transaction.savepoint_rollback(sid)
                            msg = '商品信息错误'
                            return render(request, 'orders/order/create.html', locals())

                        # 判断商品的库存
                        if int(item['quantity']) > updateproduct.stock:
                            # 回滚事务到sid保存点
                            transaction.savepoint_rollback(sid)
                            msg = '商品库存不足'
                            return render(request, 'orders/order/create.html', locals())
                        # 减少商品库存，增加销量
                        orgin_stock = updateproduct.stock
                        new_stock = orgin_stock - int(item['quantity'])
                        new_sale_num = updateproduct.sale_num + int(item['quantity'])

                        # update from Product
                        # set stock=<new_stock>, sale_num=<new_sale_num>
                        # where id=<product_id> and stock=<orgin_stock>
                        # update方法返回数字，代表更新的行数
                        if updateproduct:
                            updateproduct.stock = new_stock
                            updateproduct.sales = new_sale_num
                            updateproduct.save()

                            # 订单中包含几个商品需要向order_detail中添加几条记录
                            order_detail = OrderItem.objects.create(order=order,
                                                                    product=item.products,
                                                                    price=item.products.saleprice,
                                                                    quantity=item.products_count)
                            # 构造推荐商品列表
                            re_product.append(item.products)

                # 商品扣减库存和保存到订单明细表成功后，将进入支付页面的相关数据处理
                # 对购买商品时行评分，以便推荐
                r = Recommender()
                pro_bought = r.products_bought(re_product)
                # clear the cart
                cart.remove(request.user, item.products)
                # launch asynchronous task
                # order_created.delay(order.id)
                # set the order in the session
                request.session['order_id'] = order.id
                # redirect to the payment
                # return redirect(reverse('payment:paychoice'))
                order_id = order.id
                return render(request, 'pay/pay.html', locals())
            else:
                msg = '金额不对，请检查'
        except Exception as e:
            # 回滚事务到sid保存点
            transaction.savepoint_rollback(sid)
            msg = '下单失败'

    return render(request, 'orders/order/create.html', locals())