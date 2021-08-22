# Generated by Django 3.0.2 on 2021-08-22 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0083_auto_20201001_1951'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockfollowing',
            name='area',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='所在地域'),
        ),
        migrations.AddField(
            model_name='stockfollowing',
            name='fullname',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='股票全称'),
        ),
        migrations.AddField(
            model_name='stockfollowing',
            name='industry',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='所属行业'),
        ),
        migrations.AddField(
            model_name='stockfollowing',
            name='ts_code',
            field=models.CharField(blank=True, max_length=50, verbose_name='TS代码'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('W', '周线'), ('D', '日线'), ('60', '60分钟'), ('30', '30分钟'), ('M', '月线')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='category',
            field=models.CharField(blank=True, choices=[('H', '持仓'), ('S', '卖'), ('B', '买')], max_length=50, null=True, verbose_name='策略分类'),
        ),
    ]
