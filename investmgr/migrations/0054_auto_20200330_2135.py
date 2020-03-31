# Generated by Django 3.0.2 on 2020-03-30 13:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investmgr', '0053_auto_20200329_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockpositionsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('m', '月'), ('w', '周'), ('d', '日')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradeaccount',
            name='account_name',
            field=models.CharField(max_length=50, verbose_name='账户名称'),
        ),
        migrations.AlterField(
            model_name='tradeprofitsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('m', '月'), ('w', '周'), ('d', '日')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('wk', '周线'), ('dd', '日线'), ('30', '30分钟'), ('mm', '月线'), ('60', '60分钟')], default='60', max_length=2, verbose_name='应用周期'),
        ),
        migrations.AlterUniqueTogether(
            name='tradeaccount',
            unique_together={('account_name', 'trader')},
        ),
    ]
