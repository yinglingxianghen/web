# -*- coding: utf-8 -*-
import xadmin
# #from django.contrib import admin
# from xadmin import views
# from xadmin import widgets
# from xadmin.widgets import AdminTextareaWidget
# from xadmin.util import unquote, vendor
# from xadmin.views.base import inclusion_tag
# from xadmin.plugins.multiselect import SelectMultipleTransfer
# from xadmin.util import unquote
# from xadmin.views.detail import ResultField, ShowField, DetailAdminUtil
# from xadmin.sites import site
# from xadmin.views import csrf_protect_m, CreateAdminView, ListAdminView, UpdateAdminView, DetailAdminView, CommAdminView, ModelAdminView, ModelFormAdminView,BaseAdminPlugin
# from xadmin.plugins.inline import Inline, GenericInlineModelAdmin
# from xadmin.layout import Main, Side, Row, AppendedText, Field, Div, Reset, PrependedText, FormHelper, Layout, Fieldset, TabHolder, Container, Column, Col, Hidden, Submit, Tab, HTML

from .models import Coupon ,CouponRedemption



class CouponRedemptionAdmin(object):
    list_display = ['order', 'user',  'coupon',  'usedate','getdate','status','percentage_discount']

xadmin.site.register(CouponRedemption, CouponRedemptionAdmin)

class CouponRedemptionInline(object):
    model = CouponRedemption

class CouponAdmin(object):
    list_display = ['code','description', 'product_id',  'percentage_discount',  'preamount','is_active','expiration_date','type','maxnum','created_at']
    inlines = [CouponRedemptionInline]


xadmin.site.register(Coupon, CouponAdmin)