# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-11 09:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('log_manage', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='operatelog',
            name='username',
        ),
        migrations.AddField(
            model_name='operatelog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='operatelog',
            name='action',
            field=models.IntegerField(choices=[(1, '新增'), (2, '删除'), (3, '修改'), (500, '其他')], null=True),
        ),
    ]
