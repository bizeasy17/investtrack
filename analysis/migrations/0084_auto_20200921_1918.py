# Generated by Django 3.0.7 on 2020-09-21 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0083_auto_20200921_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('PERIOD_UPD', '更新高低点涨幅'), ('DOWNLOAD', '下载历史交易'), ('UPD_CP', '更新临界点'), ('EXP_PCT_UPD', '更新预期涨幅'), ('MARK_CP', '标记临界点'), ('EXP_PCT_TEST', '标记预期涨幅'), ('PERIOD_TEST', '标记高低点涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='strategytargetpcttestranking',
            name='ranking',
            field=models.IntegerField(blank=True, null=True, verbose_name='排名'),
        ),
        migrations.AlterField(
            model_name='strategyupdowntestranking',
            name='ranking',
            field=models.IntegerField(blank=True, null=True, verbose_name='排名'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('30', '30分钟'), ('W', '周线'), ('D', '日线'), ('M', '月线'), ('60', '60分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
