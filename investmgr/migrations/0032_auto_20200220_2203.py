# Generated by Django 3.0.2 on 2020-02-20 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investmgr', '0031_auto_20200220_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeprofitsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('w', '周'), ('m', '月'), ('d', '日')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='traderec',
            name='sold_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='卖出时间'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('dd', '日线'), ('wk', '周线'), ('mm', '月线'), ('15', '15分钟'), ('60', '60分钟'), ('30', '30分钟')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]
