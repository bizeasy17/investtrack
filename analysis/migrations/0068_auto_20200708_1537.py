# Generated by Django 3.0.7 on 2020-07-08 07:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0067_auto_20200704_0714'),
    ]

    operations = [
        migrations.CreateModel(
            name='StrategyOnDownPctTest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('strategy_code', models.CharField(blank=True, db_index=True, max_length=25, null=True, verbose_name='策略代码')),
                ('ts_code', models.CharField(max_length=15, verbose_name='股票代码')),
                ('down_10pct_min', models.FloatField(blank=True, null=True, verbose_name='-10%最小周期')),
                ('down_10pct_max', models.FloatField(blank=True, null=True, verbose_name='-10%最大周期')),
                ('down_10pct_mean', models.FloatField(blank=True, null=True, verbose_name='-10%平均周期')),
                ('down_20pct_min', models.FloatField(blank=True, null=True, verbose_name='-20%最小周期')),
                ('down_20pct_max', models.FloatField(blank=True, null=True, verbose_name='-20%最大周期')),
                ('down_20pct_mean', models.FloatField(blank=True, null=True, verbose_name='-20%平均周期')),
                ('down_30pct_min', models.FloatField(blank=True, null=True, verbose_name='-30%最小周期')),
                ('down_30pct_max', models.FloatField(blank=True, null=True, verbose_name='-30%最大周期')),
                ('down_30pct_mean', models.FloatField(blank=True, null=True, verbose_name='-30%平均周期')),
                ('down_50pct_min', models.FloatField(blank=True, null=True, verbose_name='-50%最小周期')),
                ('down_50pct_max', models.FloatField(blank=True, null=True, verbose_name='-50%最大周期')),
                ('down_50pct_mean', models.FloatField(blank=True, null=True, verbose_name='-50%平均周期')),
                ('down_80pct_min', models.FloatField(blank=True, null=True, verbose_name='-80%最小周期')),
                ('down_80pct_max', models.FloatField(blank=True, null=True, verbose_name='-80%最大周期')),
                ('down_80pct_mean', models.FloatField(blank=True, null=True, verbose_name='-80%平均周期')),
                ('test_period', models.CharField(default='D', max_length=5, verbose_name='测试周期')),
            ],
            options={
                'verbose_name': '跌幅天数统计',
                'verbose_name_plural': '跌幅天数统计',
                'ordering': ['ts_code'],
            },
        ),
        migrations.CreateModel(
            name='StrategyOnFixedDownPctTest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('strategy_code', models.CharField(blank=True, db_index=True, max_length=25, null=True, verbose_name='策略代码')),
                ('ts_code', models.CharField(max_length=15, verbose_name='股票代码')),
                ('trade_date', models.DateField(verbose_name='交易日')),
                ('pct10_period', models.FloatField(blank=True, null=True, verbose_name='-10%最小周期')),
                ('pct20_period', models.FloatField(blank=True, null=True, verbose_name='-20%最小周期')),
                ('pct30_period', models.FloatField(blank=True, null=True, verbose_name='-30%最小周期')),
                ('pct50_period', models.FloatField(blank=True, null=True, verbose_name='-50%最小周期')),
                ('pct80_period', models.FloatField(blank=True, null=True, verbose_name='-80%最小周期')),
                ('test_freq', models.CharField(default='D', max_length=5, verbose_name='测试周期')),
            ],
            options={
                'verbose_name': '跌幅天数',
                'verbose_name_plural': '跌幅天数',
                'ordering': ['ts_code'],
            },
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('UPD_CP', '更新临界点'), ('MARK_CP', '标记临界点'), ('PERIOD_TEST', '标记高低点涨幅'), ('PERIOD_UPD', '更新高低点涨幅'), ('EXP_PCT_TEST', '标记预期涨幅'), ('EXP_PCT_UPD', '更新预期涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易'), ('DOWNLOAD', '下载历史交易')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('60', '60分钟'), ('30', '30分钟'), ('W', '周线'), ('D', '日线'), ('M', '月线')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
