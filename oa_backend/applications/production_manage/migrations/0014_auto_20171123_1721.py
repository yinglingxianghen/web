# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-23 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production_manage', '0013_delete_deployway'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='ser_id',
            field=models.CharField(max_length=100),
        ),
    ]
