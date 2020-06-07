# Generated by Django 3.0.2 on 2020-06-07 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0051_auto_20200607_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('D', '日线'), ('M', '月线'), ('W', '周线'), ('60', '60分钟'), ('15', '15分钟'), ('30', '30分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='category',
            field=models.CharField(blank=True, choices=[('sell_stock', '卖'), ('buy_stock', '买'), ('hold_stock', '持仓')], max_length=50, null=True, verbose_name='策略分类'),
        ),
    ]
