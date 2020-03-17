# Generated by Django 3.0.2 on 2020-03-13 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investmgr', '0041_auto_20200314_0747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeaccount',
            name='service_charge',
            field=models.DecimalField(decimal_places=10, default=0.0005, max_digits=10, verbose_name='交易手续费'),
        ),
        migrations.AlterField(
            model_name='tradeprofitsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('m', '月'), ('d', '日'), ('w', '周')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('mm', '月线'), ('30', '30分钟'), ('60', '60分钟'), ('dd', '日线'), ('wk', '周线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]