# -*- coding:utf-8 -*-
from django.contrib import admin
from .models import *
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'name',
                    'slug',
                    'parent',
                    'status',
                    'created',
                    'updated']
    list_filter = ['name', 'status', 'created']


admin.site.register(Category, CategoryAdmin)

class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'name',
                    'phone',
                    'linkman',
                    'desc',
                    'kind',
                    'brands',
                    'image',
                    'status',
                    'created']

    list_filter = ['name', 'status', 'kind']

admin.site.register(Supplier, SupplierAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'name',
                    'slug',
                    'category',
                    'productno',
                    'image',
                    'price',
                    'saleprice',
                    'stock',
                    'available',
                    'supplier']
    list_filter = ['name', 'category', 'supplier']


    class Media:
        css = {"all": ("/static/ueditor/themes/default/css/ueditor.css",)}
        js = ("/static/ueditor/ueditor.config.js", "/static/ueditor/ueditor.all.min.js",)

admin.site.register(Product, ProductAdmin)


class SaleProductsAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'title',
                    'protduct',
                    'status',
                    'marketprice',
                    'price',
                    'startdatetime',
                     'enddatetime',
                    'stock_total',
                    'remain_qty',
                    'desc']
    list_filter = ['title', 'status', 'protduct', 'startdatetime', 'enddatetime']

    class Media:
        css = { "all": ("/static/ueditor/themes/default/css/ueditor.css",) }
        js = ("/static/ueditor/ueditor.config.js", "/static/ueditor/ueditor.all.min.js",)
admin.site.register(SaleProducts, SaleProductsAdmin)
