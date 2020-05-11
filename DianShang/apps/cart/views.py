# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from shop.models import Product
from .models import Cart
from coupons.models import CouponRedemption
from shop.recommender import Recommender
import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from shop.json_request import JsonResponse
from django.contrib.auth.models import User


@login_required
@csrf_protect
def cart_add(request):
    # cart = Cart(request)
    product_id = request.GET.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    quantity = request.POST.get('quantity')
    update_quantity = request.POST.get('update')
    user=User.objects.get(id=request.user.id)
    if quantity == None:
        quantity = 1
    # form = CartAddProductForm(request.POST)
    # if form.is_valid():
    #     cd = form.cleaned_data
    # cart.add(product=product,quantity=quantity,update_quantity=update_quantity)
    Cart.objects.add(user=user,products=product, quantity=quantity)
    return redirect('cart_detail')

@login_required
@csrf_protect
def cart_remove(request):
    product_id = request.GET.get('product_id')
    # cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    user = User.objects.get(id=request.user.id)
    # cart.remove(product)
    Cart.objects.remove(user, product_id)
    #重定向到显示购物车页面
    return redirect('cart_detail')

@login_required
@csrf_protect
def cart_delete(request):
    id = request.GET.get('id')
    Cart.objects.filter(id=id).delete()
    # 重定向到显示购物车页面
    return redirect('cart_detail')

@login_required
def cart_detail(request):

    user = User.objects.get(id=request.user.id)
    cart_products =Cart.objects.get_cart_list(user=user)

    # 取优惠券，1、只对本课程有效的，2、全部课程有效的
    couponlist = []
    couponlist = CouponRedemption.objects.filter(status='1', user=request.user).filter(coupon__is_active=1). \
        filter(coupon__type=1).filter(coupon__expiration_date__gt=datetime.datetime.now()).select_related()

    if cart_products:
        r = Recommender()
        recommended_products = r.suggest_products_for(cart_products, 5)

    return render(request, 'cart/detail.html', locals())

# @login_required
def cart_add_ajax(request):
    try:
        var_data = request.POST.get('var_data')
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        quantity = request.POST.get('quantity')
        user = User.objects.get(id=request.user.id)

        Cart.objects.add(user=user, products=product, quantity=quantity)
        flag=201
        msg="succuss"
    except Exception as e:
        flag = 301
        msg = "fail"
    return JsonResponse({"flag": flag,"msg": msg})
    # return HttpResponse(flag)
