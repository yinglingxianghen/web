# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import *

admin.site.register(Order)
admin.site.register(OrderItem)
