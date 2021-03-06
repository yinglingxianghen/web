# Generated by Django 2.0.3 on 2019-01-28 07:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, null=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=50, null=True, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='e-mail')),
                ('mobile', models.CharField(blank=True, max_length=11, null=True, verbose_name='电话')),
                ('remark', models.CharField(blank=True, max_length=1024, null=True, verbose_name='备注')),
                ('address', models.CharField(max_length=250, null=True, verbose_name='address')),
                ('postal_code', models.CharField(max_length=20, null=True, verbose_name='postal code')),
                ('status', models.CharField(default='1', max_length=2)),
                ('city', models.CharField(max_length=100, null=True, verbose_name='city')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('paid', models.BooleanField(default=False)),
                ('pay_type', models.IntegerField(choices=[(4, '货到付款'), (2, '微信支付'), (3, '支付宝'), (1, '银联支付')], default=1, verbose_name='状态')),
                ('trans_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='运费')),
                ('pay_no', models.CharField(default='', max_length=128, verbose_name='支付编号')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8)),
                ('coupon', models.CharField(blank=True, max_length=20, null=True)),
                ('discount', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='orders.Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='shop.Product')),
            ],
        ),
    ]
