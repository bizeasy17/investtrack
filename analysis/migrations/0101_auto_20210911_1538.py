# Generated by Django 3.0.2 on 2021-09-11 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0100_auto_20210908_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockquantilestat',
            name='quatile',
            field=models.FloatField(blank=True, null=True, verbose_name='分位数'),
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('PERIOD_TEST', '标记高低点涨幅'), ('UPD_CP', '更新临界点'), ('EXP_PCT_UPD', '更新预期涨幅'), ('DOWNLOAD', '下载历史交易'), ('EXP_PCT_TEST', '标记预期涨幅'), ('PERIOD_UPD', '更新高低点涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易'), ('MARK_CP', '标记临界点')], max_length=50, verbose_name='日志类型'),
        ),
    ]