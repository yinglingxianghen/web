# coding:utf-8
from django.db import models
from django.contrib import admin

class Comment(models.Model):
    commentid = models.IntegerField(primary_key=True)
    pid = models.BigIntegerField()
    cid = models.BigIntegerField()
    avatar = models.CharField(max_length=512, blank=True, null=True)
    uname = models.CharField(max_length=512, blank=True, null=True)
    created_at = models.CharField(max_length=128)
    content = models.TextField(blank=True, null=True)
    like_counts = models.IntegerField()
    reply = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'comments'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('commentid', 'pid', 'cid', 'uname', 'created_at', 'content', 'like_counts', 'reply')
    empty_value_display = '-'

admin.site.register(Comment, CommentAdmin)