# Generated by Django 3.0.2 on 2020-02-02 08:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investmgr', '0014_auto_20200130_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('mm', '月线'), ('30', '30分钟'), ('60', '60分钟'), ('dd', '日线'), ('wk', '周线'), ('15', '15分钟')], default='60', max_length=2, verbose_name='应用周期'),
        ),
        migrations.CreateModel(
            name='StockFollowing',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('is_following', models.BooleanField(default=True, verbose_name='是否关注')),
                ('stock_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investmgr.StockNameCodeMap', verbose_name='股票代码')),
                ('trader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='持仓人')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
