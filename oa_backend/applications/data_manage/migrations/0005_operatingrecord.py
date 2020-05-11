# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-23 03:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_manage', '0004_auto_20171114_1417'),
    ]

    operations = [
        migrations.CreateModel(
            name='OperatingRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry', models.CharField(help_text='所属行业', max_length=60)),
                ('deploy_way', models.SmallIntegerField(choices=[(1, '标准版'), (2, 'VIP版'), (3, 'VPC版本'), (4, '企业版')], help_text='部署方式')),
                ('cli_version', models.SmallIntegerField(choices=[(1, 'B2B'), (2, 'B2C'), (3, '不限')], help_text='客户版本')),
                ('created_at', models.DateTimeField(auto_now=True, help_text='创建时间')),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='更新时间')),
                ('date', models.DateField(help_text='记录时间')),
                ('action', models.SmallIntegerField(choices=[(1, '新增客户'), (2, '续费客户'), (3, '新增产品'), (4, '上线客户'), (5, '下线客户')], help_text='操作行为')),
                ('num', models.IntegerField(default=0, help_text='统计数量')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
