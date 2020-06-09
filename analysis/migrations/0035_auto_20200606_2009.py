# Generated by Django 3.0.2 on 2020-06-06 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0034_auto_20200604_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('EXP_PCT_TEST', '标记预期涨幅'), ('MARK_CP', '标记临界点'), ('UPD_CP', '更新临界点'), ('UPD_DOWNLOAD', '更新下载历史交易'), ('EXP_PCT_UPD', '更新预期涨幅'), ('PERIOD_TEST', '标记高低点涨幅'), ('PERIOD_UPD', '更新高低点涨幅'), ('DOWNLOAD', '下载历史交易')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('30', '30分钟'), ('mm', '月线'), ('15', '15分钟'), ('dd', '日线'), ('wk', '周线'), ('60', '60分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
