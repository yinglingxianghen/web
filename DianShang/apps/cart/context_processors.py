# -*- coding:utf-8 -*-
# from .cart import Cart
from .models import Cart

def cart(request):
    if request.user.id:
        carts = Cart.objects.get_cart_list(user=request.user)
        # return { 'cart': Cart(request) }
    else:
        carts=[]
    return { 'cart': carts }

