#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
# Create your models here.


class BBS_User(models.Model):
    SEX_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=11,
                             error_messages={
                                 'phone_err': '手机号码格式有误',
                             },
                             validators=[
                                 RegexValidator(regex='1[3578][0-9]{9}', message='手机号码格式有误',
                                                code='phone_err')
                             ])
    sex = models.CharField(max_length=10,choices=SEX_CHOICES)
    head_img = models.ImageField(upload_to="avatar/",default="avatar/default.jpg")

    def __str__(self):
        return self.user.username

class Post(models.Model):
    author = models.ForeignKey(BBS_User)
    content = models.TextField()
    title = models.CharField(max_length=128)
    summary = models.CharField(max_length=256, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    category = models.ForeignKey('Category')

    def __str__(self):
        return self.title

class Comment(models.Model):
    comment_content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(BBS_User)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey("self",related_name="p_commment",null=True,blank=True)


    def __str__(self):
        return self.comment_content

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name
