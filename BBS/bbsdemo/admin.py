from django.contrib import admin
from .models import *
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'category')
    list_filter = ('created_date',)
    search_fields = ('author',)


admin.site.register(BBS_User)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Category)
