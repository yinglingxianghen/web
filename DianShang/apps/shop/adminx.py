# -*- coding:utf-8 -*-
import xadmin
#from django.contrib import admin
from xadmin import views
from xadmin import widgets
from xadmin.widgets import AdminTextareaWidget
from xadmin.util import unquote, vendor

from xadmin.layout import Main, Side, Row, AppendedText, Field, Div, Reset, PrependedText, FormHelper, Layout, Fieldset, TabHolder, Container, Column, Col, Hidden, Submit, Tab, HTML

from django import forms
from .models import Category, Saleproperty,Categoryproperty,Categorypropertyvalue,Product,Productproperty,Recommend,Supplier,BrowseHistory,Ad

from  DjangoUeditor.forms import UEditorField
from django.db.models import TextField
from DjangoUeditor.models import UEditorField

from  DjangoUeditor.widgets import UEditorWidget
from django.forms import Media

class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True
xadmin.site.register(views.BaseAdminView, BaseSetting)


class GlobalSetting(object):

    menu_style = 'default'#'accordion'
    # 设置base_site.html的Title
    site_title = '在线商城后台管理系统'
     # 设置base_site.html的Footer
    site_footer = '可锐尤软件'
    def get_site_menu(self):
        return (
        {'title': '商品管理', 'perm': self.get_model_perm(Product, 'change'), 'menus': (
            {'title': '商品管理', 'url': self.get_model_url(Product, 'changelist')},
            {'title': '商品分类', 'url': self.get_model_url(Category, 'changelist')},
            {'title': '供应商', 'url': self.get_model_url(Supplier, 'changelist')},
            {'title': '新品推荐', 'url': self.get_model_url(Recommend, 'changelist')},
                )},
          )
xadmin.site.register(views.CommAdminView, GlobalSetting)


class CategorypropertyvalueAdmin(object):
     list_display = ['valuename', 'desc']

xadmin.site.register(Categorypropertyvalue, CategorypropertyvalueAdmin)


class SalepropertyInline(object):
    model = Saleproperty
#
class CategorypropertyInline(object):
    model = Categoryproperty

class CategorypropertyvalueInline(object):
    model = Categorypropertyvalue


class CategorypropertyAdmin(object):
    list_display = ['displayname', 'desc']
    inlines = [CategorypropertyvalueInline]


xadmin.site.register(Categoryproperty, CategorypropertyAdmin)

class CategoryAdmin(object):
    list_display = ['name', 'slug',  'parent',  'status']
    #inlines = [CategorypropertyInline]
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

    def queryset(self):
        qs = super(CategoryAdmin, self).queryset().order_by('-parent','id')
        return qs

xadmin.site.register(Category, CategoryAdmin)

class SalepropertyAdmin(object):
    list_display = ['pname', 'desc']

    def get_prepopulated_fields(self, request, obj=None):
       return {'slug': ('pname',)}

xadmin.site.register(Saleproperty, SalepropertyAdmin)
# #给产品详情加富文本编辑框
class ProductForm(forms.ModelForm):
   # description = UEditorField("描述",  width=800, height=600)
    description = forms.CharField(label="内容",
                             widget=UEditorWidget(attrs={'width':'800','height':'400','toolbars':'mini',}))


    class Meta:
        forms.model=Product
       # js =  ('/static/ueditor/editor_config.js','/static/ueditor/editor_all_min.js',)


    def get_media(self):
        return super(ProductForm, self).get_media() + vendor('select.js', 'select.css',
                                                                                      'xadmin.widget.select.js')
#
class ProductAdmin(object):
#     # 指定要显示的字段
     list_display = ['name','productno', 'slug', 'category', 'price', 'saleprice','image','largeimage','stock', 'available', 'created', 'updated']
#     # 指定列表过滤器，右边将会出现一个快捷的日期过滤选项， #以方便开发人员快速地定位到想要的数据，同样你也可以指定非日期型类型的字段
     list_filter = ['available', 'created', 'updated', 'category']
#     # 指定要搜索的字段，将会出现一个搜索框让管理员搜索关键词
     search_fields = ('name',)
#     # 在列表中指定可编辑的字段
     list_editable = ['price', 'stock', 'available']
     date_hierarchy = 'created'  # 日期型字段进行层次划分。
     ordering = ('-category', 'name')  # 对出生日期降序排列，对年级升序
     #inlines = [ProductsizeInline,ProductcolorInline]
     form = ProductForm

     form_layout = (
        Div(
            Div(
                Row('name', 'productno', 'slug'), #一行显示三个字段
                Row('category', 'supplier', 'available'),
                Row('price', 'saleprice', 'stock'),
                Row('image', 'largeimage', ),

                # Field('status_teacher', readonly=True)),
                # Row(Field('username', wrapper_class='f-col31'), Field('address', wrapper_class='f-col32')),

            ),
            Div(
                Row('description'),

            ),
            # Field('id', type='hidden'),
            # Row('totalscore', 'remainscore', 'birthday'),
            css_class='row'
        ),
     )

#
xadmin.site.register(Product, ProductAdmin)


class SupplierAdmin(object):
     list_display = ['name', 'desc', 'phone', 'linkman', 'kind', 'brands', 'created', 'updated', 'status']
     list_editable = ['name', 'desc', 'phone', 'linkman', 'kind', 'brands',]
     form_layout = (
         Div(
            Row('name','kind', 'brands'
                     ),
            Row('phone', 'linkman', 'status'
                     ),
            Row('image'
                 ),
         ),
         Div(
             Div(Field('desc',style="width:500px;height:200px;",)
             ),
         ),
    )
xadmin.site.register(Supplier, SupplierAdmin)


class DynamicChoiceField(forms.ChoiceField):
    def clean(self, value):
        return value
class RecommendForm(forms.Form):

     STATUS_CHOICES = (
         ('1', '推荐'),
         ('0', '取消'),
     )
     #supplier = forms.ChoiceField(choices=Supplier.objects.filter(kind=1, status=1).values_list('id', 'name'))
     supplier = forms.ChoiceField()
     product = forms.ChoiceField()
     expiredate = forms.DateInput()
     desc = forms.CharField(widget=AdminTextareaWidget)
     status = forms.ChoiceField(choices=STATUS_CHOICES)


     def media(self):
         # media.add_js([self.static('xadmin/js/filterproduct.js')])
         #media = super(RecommendForm, self).get_media()
         media = Media()
         media.add_js(['js/filterporduct.js'])
         return  media
         #
         # media.add_js(['xadmin/js/filterproduct.js'])

class ProductpropertyAdmin(object):
    list_display = ['name', 'product', 'categoryproperty', 'categorypropertyvalue']

xadmin.site.register(Productproperty, ProductpropertyAdmin)

class RecommendAdmin(object):
    list_display = ['supplier', 'desc', 'product', 'expiredate', 'created', 'updated', 'status']
    list_editable = ['desc', 'status']

    form = RecommendForm



xadmin.site.register(Recommend, RecommendAdmin)

class BrowseHistoryAdmin(object):
    list_display = ['products', 'users']

xadmin.site.register(BrowseHistory, BrowseHistoryAdmin)

class AdAdmin(object):
    list_display = ['title', 'image', 'callback_url', 'date_publish', 'location', 'is_display']
    list_editable = ['title', 'image', 'callback_url', 'date_publish', 'location', 'is_display']
xadmin.site.register(Ad, AdAdmin)