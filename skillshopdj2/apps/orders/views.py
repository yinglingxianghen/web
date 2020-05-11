# -*- coding: utf-8 -*-
""" 
@version: v1.0 
@author: andy 
@license: Apache Licence  
@contact: 93226042@qq.com 
@site:  
@software: PyCharm 
@file: views.py 
@time: 2018/2/5 21:57 
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from seckill.models import SaleProducts
from seckill.cache_manage import getcache,setcache,get_keylist,exists,init_stock
import datetime

def orderlist(request):
    userid=request.user.id
    orderlist=OrderItem.objects.filter(order__user_id=userid)
    return render(request, 'orders/orderlist.html', locals())

def seckillproduct_list(request):
    # 取当天时间的
    todays = datetime.date.today()
    nextday = todays + datetime.timedelta(days=1)

    # product_list = SaleProducts.objects.filter(status='1').filter(startdatetime__gt=todays,
    #                                                               startdatetime__lt=nextday).order_by('startdatetime')
    product_ids = []
    stock_list = []
    stock_key = 'stock_*'
    keylist = get_keylist(stock_key)

    for key in keylist:
        stock_qty = getcache(key)
        productid = int(key[6:])
        stock_list.append({'id': productid, 'stock_qty': stock_qty})
        product_ids.append(productid)
    product_list = SaleProducts.objects.filter(id__in=product_ids)

    # for pro in products:
    #     product_list.append({'id':pro.id,'title':pro.title,'price':pro.price,'stock_total':pro.stock_total,
    #                 'startdatetime':pro.startdatetime,'enddatetime':pro.enddatetime,'status':pro.status,'stock_qty':stock_qty})
    print(stock_list)

    return render(request, 'orders/monitor.html', locals())


#初始化库存
@login_required
def initstock(request):
    # 取当天时间的
    todays = datetime.date.today()
    nextday = todays + datetime.timedelta(days=1)
    product_list = SaleProducts.objects.filter(status='1').filter(startdatetime__gt=todays,
                                                                 startdatetime__lt=nextday).order_by('startdatetime')

    for pro in product_list:
        product_id = pro.id
        key_stock = 'stock_{}'.format(product_id)
        stock_qty = exists(key_stock)
        # 初始化库存
        if stock_qty is None:
            init_stock(key_stock, pro.stock_total)

    return redirect(reverse('seckillproduct_list'))  # 跳转到列表界面

@login_required
def endseckill(request):
    productid=request.GET.get('productid')
    key_stock = 'stock_{}'.format(productid)
    #缓存中库存设为0
    setcache(key_stock,60*10,0)

    #redirect(seckillproduct_list(request))
    return redirect(reverse('seckillproduct_list'))  # 跳转到列表界面
