# Generated by Django 3.0.7 on 2020-06-29 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0063_auto_20200629_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma200',
            field=models.FloatField(blank=True, null=True, verbose_name='MA200'),
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('DOWNLOAD', '下载历史交易'), ('PERIOD_UPD', '更新高低点涨幅'), ('EXP_PCT_TEST', '标记预期涨幅'), ('EXP_PCT_UPD', '更新预期涨幅'), ('MARK_CP', '标记临界点'), ('UPD_CP', '更新临界点'), ('PERIOD_TEST', '标记高低点涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('60', '60分钟'), ('30', '30分钟'), ('W', '周线'), ('M', '月线'), ('D', '日线'), ('15', '15分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
