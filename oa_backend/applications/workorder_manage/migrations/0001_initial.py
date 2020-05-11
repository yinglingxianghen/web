# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-10 08:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('production_manage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountConf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=50)),
                ('set_pwd', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='AreaInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atitle', models.CharField(max_length=50)),
                ('aPArea', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='workorder_manage.AreaInfo')),
            ],
            options={
                'permissions': (('view_areainfo', 'Can see available area info'),),
            },
        ),
        migrations.CreateModel(
            name='CompanyAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.CharField(max_length=100)),
                ('city', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='city', to='workorder_manage.AreaInfo')),
                ('province', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='province', to='workorder_manage.AreaInfo')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_type', models.IntegerField(choices=[(1, '试用客户'), (2, '正式客户'), (3, '市场渠道客户'), (4, '商务渠道客户'), (5, '自用站点')])),
                ('company_name', models.CharField(max_length=50)),
                ('company_email', models.CharField(max_length=50)),
                ('GSZZ', models.CharField(max_length=50)),
                ('customer_type', models.BooleanField(choices=[(False, '新客户'), (True, '老客户')], default=False)),
                ('service_area', models.CharField(max_length=128)),
                ('company_address', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_info', to='workorder_manage.CompanyAddress')),
            ],
            options={
                'verbose_name': '公司信息',
                'verbose_name_plural': '公司信息',
            },
        ),
        migrations.CreateModel(
            name='CompanyUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_url', models.CharField(max_length=50)),
                ('company_info', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_url', to='workorder_manage.CompanyInfo')),
            ],
        ),
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('linkman', models.CharField(max_length=50)),
                ('link_phone', models.CharField(max_length=30)),
                ('link_email', models.CharField(max_length=50)),
                ('link_qq', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry', models.CharField(max_length=60, unique=True)),
            ],
            options={
                'permissions': (('view_industry', 'Can see available industry'),),
            },
        ),
        migrations.CreateModel(
            name='OpenStationManage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('online_status', models.BooleanField(choices=[(False, '下线'), (True, '上线')], default=False)),
                ('company_info', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='open_station', to='workorder_manage.CompanyInfo')),
                ('func_list', models.ManyToManyField(db_constraint=False, related_name='station', to='production_manage.SingleSelection')),
            ],
            options={
                'verbose_name': '开站管理',
                'verbose_name_plural': '开站管理',
                'permissions': (('view_openstationmanage', 'Can see available open station manage'),),
            },
        ),
        migrations.CreateModel(
            name='StationInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_id', models.CharField(max_length=20, unique=True)),
                ('deploy_way', models.IntegerField(choices=[(1, '标准版'), (2, 'VIP版'), (3, 'VPC版本'), (4, '企业版')])),
                ('validity_days', models.IntegerField()),
                ('cli_version', models.IntegerField(choices=[(1, 'B2B'), (2, 'B2C'), (3, '不限')])),
                ('open_station_time', models.DateField()),
                ('close_station_time', models.DateField()),
                ('sales', models.CharField(max_length=20)),
                ('pre_sales', models.CharField(max_length=20)),
                ('oper_cslt', models.CharField(max_length=20)),
                ('impl_cslt', models.CharField(max_length=20)),
                ('oper_supt', models.CharField(max_length=20)),
                ('grid', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='station_info', to='production_manage.Grid')),
                ('pact_products', models.ManyToManyField(db_constraint=False, related_name='station_info', to='production_manage.Product')),
            ],
            options={
                'verbose_name': '站点信息',
                'verbose_name_plural': '站点信息',
            },
        ),
        migrations.AddField(
            model_name='openstationmanage',
            name='station_info',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='open_station', to='workorder_manage.StationInfo'),
        ),
        migrations.AddField(
            model_name='contactinfo',
            name='station',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='link_info', to='workorder_manage.OpenStationManage'),
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='industry',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_info', to='workorder_manage.Industry'),
        ),
        migrations.AddField(
            model_name='accountconf',
            name='station',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='account_conf', to='workorder_manage.OpenStationManage'),
        ),
    ]
