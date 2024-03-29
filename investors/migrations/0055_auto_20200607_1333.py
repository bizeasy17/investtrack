# Generated by Django 3.0.2 on 2020-06-07 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0054_auto_20200607_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('W', '周线'), ('15', '15分钟'), ('M', '月线'), ('D', '日线'), ('60', '60分钟'), ('30', '30分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='category',
            field=models.CharField(blank=True, choices=[('H', '持仓'), ('S', '卖'), ('B', '买')], max_length=50, null=True, verbose_name='策略分类'),
        ),
    ]
