# Generated by Django 3.0.2 on 2021-09-25 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0105_auto_20210925_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='industrybasicquantilestat',
            name='quantile_val',
            field=models.FloatField(blank=True, null=True, verbose_name='分位值'),
        ),
        migrations.AlterField(
            model_name='industrybasicquantilestat',
            name='industry',
            field=models.CharField(db_index=True, max_length=25, verbose_name='行业'),
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('UPD_DOWNLOAD', '更新下载历史交易'), ('PERIOD_TEST', '标记高低点涨幅'), ('DOWNLOAD', '下载历史交易'), ('MARK_CP', '标记临界点'), ('EXP_PCT_UPD', '更新预期涨幅'), ('PERIOD_UPD', '更新高低点涨幅'), ('UPD_CP', '更新临界点'), ('EXP_PCT_TEST', '标记预期涨幅')], max_length=50, verbose_name='日志类型'),
        ),
    ]