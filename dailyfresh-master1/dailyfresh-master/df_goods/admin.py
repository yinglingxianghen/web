from django.contrib import admin
from df_goods.models import *


# Register your models here.


class GoodsAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'goods_name', 'goods_sub_title', 'goods_price', 'transit_price',
                    'goods_unite', 'goods_info', 'goods_image', 'goods_stock', 'goods_status'
                    ]

admin.site.register(Goods, GoodsAdmin)
