# Generated by Django 3.0.2 on 2020-04-20 13:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TradeStrategy',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('applied_period', models.CharField(blank=True, choices=[('15', '15分钟'), ('wk', '周线'), ('dd', '日线'), ('30', '30分钟'), ('mm', '月线'), ('60', '60分钟')], default='60', max_length=2, verbose_name='应用周期')),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='策略名')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
                ('parent_strategy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='investors.TradeStrategy', verbose_name='父级策略')),
            ],
            options={
                'verbose_name': '交易策略',
                'verbose_name_plural': '交易策略',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StockFollowing',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('stock_code', models.CharField(max_length=50, verbose_name='股票代码')),
                ('stock_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='股票名称')),
                ('is_following', models.BooleanField(default=True, verbose_name='是否关注')),
                ('trader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='持仓人')),
            ],
            options={
                'verbose_name': '自选股票',
                'verbose_name_plural': '自选股票',
                'ordering': ['-last_mod_time'],
                'get_latest_by': 'id',
                'unique_together': {('stock_code', 'trader')},
            },
        ),
    ]
