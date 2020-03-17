# Generated by Django 3.0.2 on 2020-03-13 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investmgr', '0040_auto_20200309_2213'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tradeaccount',
            old_name='trade_fee',
            new_name='service_charge',
        ),
        migrations.AlterField(
            model_name='tradeprofitsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('d', '日'), ('w', '周'), ('m', '月')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('30', '30分钟'), ('15', '15分钟'), ('mm', '月线'), ('dd', '日线'), ('60', '60分钟'), ('wk', '周线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]