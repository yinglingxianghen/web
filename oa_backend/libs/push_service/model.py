from django.db import models
class abc(models.Model):
    name = models.CharField(max_length=32)
    age = models.IntegerField()
