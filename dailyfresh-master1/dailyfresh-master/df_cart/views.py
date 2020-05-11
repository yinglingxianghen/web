from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from utils.decorators import login_requird
from df_cart.models import Cart


# Create your views here.


@require_GET
@login_requird
def cart_add(request):
    # 取得商品ID和商品数量
    goods_id = request.GET.get('goods_id')
    goods_count = request.GET.get('goods_count')
    passport_id = request.session.get('passport_id')
    print('cart_add:{}'.format(passport_id))
    # 将passport_id, goods_id, goods_count 添加到数据库
    res = Cart.objects.add_one_cart_info(passport_id=passport_id,
                                         goods_id=goods_id,
                                         goods_count=int(goods_count))
    print(res)
    if res:
        # 添加成功
        return JsonResponse({'res': 1})
    else:
        # 添加失败
        return JsonResponse({'res': 0})


@require_GET
@login_requird
def cart_count(request):
    '''获取用户购物车中商品的总数'''
    # 1.获取登录账户的id
    passport_id = request.session.get('passport_id')
    # 2.根据passport_id查询用户购物车商品总数
    res = Cart.objects.get_cart_count_by_passport(passport_id=passport_id)
    # 3.返回json数据
    return JsonResponse({'res': res})
