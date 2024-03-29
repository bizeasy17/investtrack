# Generated by Django 3.0.2 on 2020-11-21 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0091_auto_20201110_1607'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pickedstocksmeetstrategy',
            name='stock_name',
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('UPD_CP', '更新临界点'), ('EXP_PCT_UPD', '更新预期涨幅'), ('PERIOD_TEST', '标记高低点涨幅'), ('EXP_PCT_TEST', '标记预期涨幅'), ('PERIOD_UPD', '更新高低点涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易'), ('MARK_CP', '标记临界点'), ('DOWNLOAD', '下载历史交易')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('D', '日线'), ('15', '15分钟'), ('M', '月线'), ('W', '周线'), ('30', '30分钟'), ('60', '60分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
