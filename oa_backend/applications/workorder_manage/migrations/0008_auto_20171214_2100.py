# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-14 13:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorder_manage', '0007_auto_20171204_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationinfo',
            name='impl_cslt',
            field=models.CharField(max_length=254),
        ),
        migrations.AlterField(
            model_name='stationinfo',
            name='oper_cslt',
            field=models.CharField(max_length=254),
        ),
        migrations.AlterField(
            model_name='stationinfo',
            name='oper_supt',
            field=models.CharField(max_length=254),
        ),
        migrations.AlterField(
            model_name='stationinfo',
            name='pre_sales',
            field=models.CharField(max_length=254),
        ),
        migrations.AlterField(
            model_name='stationinfo',
            name='sales',
            field=models.CharField(max_length=254),
        ),
    ]
