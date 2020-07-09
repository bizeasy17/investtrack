# Generated by Django 3.0.7 on 2020-07-09 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0068_auto_20200708_1537'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bstrategytestresultondays',
            name='last_mod_time',
        ),
        migrations.RemoveField(
            model_name='bstrategytestresultondays',
            name='stage_high',
        ),
        migrations.RemoveField(
            model_name='bstrategytestresultondays',
            name='stage_low',
        ),
        migrations.RemoveField(
            model_name='bstrategytestresultondays',
            name='tnx_point',
        ),
        migrations.AddField(
            model_name='bstrategytestresultondays',
            name='stage_high_date',
            field=models.DateField(blank=True, null=True, verbose_name='高点日期'),
        ),
        migrations.AddField(
            model_name='bstrategytestresultondays',
            name='stage_low_date',
            field=models.DateField(blank=True, null=True, verbose_name='低点日期'),
        ),
        migrations.AlterField(
            model_name='bstrategytestresultondays',
            name='stage_high_pct',
            field=models.FloatField(blank=True, null=True, verbose_name='高点/买点%?'),
        ),
        migrations.AlterField(
            model_name='bstrategytestresultondays',
            name='stage_low_pct',
            field=models.FloatField(blank=True, null=True, verbose_name='低点/买点%?'),
        ),
        migrations.AlterField(
            model_name='bstrategytestresultondays',
            name='strategy_code',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='策略代码'),
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('EXP_PCT_UPD', '更新预期涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易'), ('UPD_CP', '更新临界点'), ('PERIOD_TEST', '标记高低点涨幅'), ('DOWNLOAD', '下载历史交易'), ('MARK_CP', '标记临界点'), ('PERIOD_UPD', '更新高低点涨幅'), ('EXP_PCT_TEST', '标记预期涨幅')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('D', '日线'), ('60', '60分钟'), ('W', '周线'), ('15', '15分钟'), ('M', '月线'), ('30', '30分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
