from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class User(models.Model):
    user = models.OneToOneField(User)
    phone = models.IntegerField()
    sex = models.BooleanField()
    head_img = models.ImageField(upload_to="avatar/",default="avatar/default.jpg")

    def __str__(self):
        return self.username

class Post(models.Model):
    author = models.ForeignKey(User)
    content = models.TextField()
    title = models.CharField(max_length=128)
    summary = models.CharField(max_length=256, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    categery = models.ForeignKey('Category')

    def __str(self):
        return self.title

class Comment(models.Model):
    comment_content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Category(models.Model):
    name = models.CharField(max_length=64)
