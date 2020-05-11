from django.shortcuts import render
from django.core.paginator import Paginator
from df_goods.models import Goods, Image
from df_goods.enums import *


# Create your views here.

def home_list_page(request):
    fruits = Goods.objects.get_goods_by_type(goods_type_id=FRUIT, limit=4)
    fruits_new = Goods.objects.get_goods_by_type(goods_type_id=FRUIT, limit=3, sort='new')

    seafood = Goods.objects.get_goods_by_type(goods_type_id=SEAFOOD, limit=4)
    seafood_new = Goods.objects.get_goods_by_type(goods_type_id=SEAFOOD, limit=3, sort='new')

    meats = Goods.objects.get_goods_by_type(goods_type_id=MEAT, limit=4)
    meats_new = Goods.objects.get_goods_by_type(goods_type_id=MEAT, limit=3, sort='new')

    eggs = Goods.objects.get_goods_by_type(goods_type_id=EGGS, limit=4)
    eggs_new = Goods.objects.get_goods_by_type(goods_type_id=EGGS, limit=3, sort='new')

    vegetables = Goods.objects.get_goods_by_type(goods_type_id=VEGETABLES, limit=4)
    vegetables_new = Goods.objects.get_goods_by_type(goods_type_id=VEGETABLES, limit=3, sort='new')

    frozen = Goods.objects.get_goods_by_type(goods_type_id=FROZEN, limit=4)
    frozen_new = Goods.objects.get_goods_by_type(goods_type_id=FROZEN, limit=3, sort='new')

    # # 组织上下文数据
    print(fruits)
    context = {'fruits': fruits, 'fruits_new': fruits_new,
               'seafood': seafood, 'seafood_new': seafood_new,
               'meats': meats, 'meats_new': meats_new,
               'eggs': eggs, 'eggs_new': eggs_new,
               'vegetables': vegetables, 'vegetables_new': vegetables_new,
               'frozen': frozen, 'frozen_new': frozen_new}
    return render(request, 'df_goods/index3.html',
                  context
                  )


# def goods_detail(request, goods_id):
#     goods = Goods.objects.get_goods_by_id(goods_id=goods_id)
#     images = Image.objects.get_image_by_goods_id(goods_id=goods_id)
#     goods = Goods.objects_logic.get_goods_by_id(goods_id=goods_id)
#     return render(request,
#                   'df_goods/detail.html',
#                   {'goods':goods})

def goods_detail(request, goods_id):
    '''显示商品的详情页面'''
    # 1.根据商品id查询商品信息，包含商品的详情图片信息 goods.img_url
    goods = Goods.objects_logic.get_goods_by_id(goods_id=goods_id)
    images = Image.objects.get_image_by_goods_id(goods_id=goods_id)
    # 2.查询新品信息
    goods_new = Goods.objects.get_goods_by_type(goods_type_id=goods.goods_type_id, limit=2, sort='new')
    # 3.获取商品类型标题
    type_title = GOODS_TYPE[goods.goods_type_id]
    # 3.使用模板文件detail.html
    # print('goos_detail'+goods.img_url)
    return render(request, 'df_goods/detail.html', {'goods': goods,
                                                    'goods_new': goods_new,
                                                    'type_title': type_title})


def goods_list(request, goods_type_id, pindex):
    # 获取查询方式
    sort = request.GET.get('sort', 'default')
    # 按照ID进行查询
    goods_li = Goods.objects.get_goods_by_type(goods_type_id=goods_type_id, sort=sort)
    # 查询新品
    goods_new = Goods.objects.get_goods_by_type(goods_type_id=goods_type_id, limit=2, sort='new')
    # 进行分页,一条每页
    paginator = Paginator(goods_li, 10)

    pindex = int(pindex)
    # 取得第pindex页的内容
    goods_li = paginator.page(pindex)
    num_pages = paginator.num_pages  # 获取总页数
    if num_pages < 5:
        pages = range(1, num_pages + 1)
    elif pindex <= 3:
        pages = range(1, 6)
    elif num_pages - pindex <= 2:
        pages = range(num_pages - 4, num_pages + 1)
    else:
        pages = range(pindex - 2, pindex + 3)

    return render(request, 'df_goods/list.html', {'goods_li': goods_li,
                                                  'goods_new': goods_new,
                                                  'type_id': goods_type_id,
                                                  'type_title': GOODS_TYPE[int(goods_type_id)],
                                                  'sort': sort,
                                                  'pages': pages})
