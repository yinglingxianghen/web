from django.contrib import admin
from df_user.models import *
# Register your models here.


class PassportAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'password', 'email', 'is_delete']


class AdressAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'recipient_name', 'recipient_addr', 'recipient_phone', 'zip_code', 'passport_id'
                    ]

admin.site.register(Passport, PassportAdmin)
admin.site.register(Address, AdressAdmin)
