# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-30 11:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('production_manage', '0008_auto_20171030_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='databaseinfo',
            name='grid',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='db_info', to='production_manage.Grid'),
            preserve_default=False,
        ),
    ]
