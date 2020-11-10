# Generated by Django 3.0.2 on 2020-11-08 08:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('analysis', '0089_auto_20201013_1801'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisEventLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_code', models.CharField(blank=True, max_length=25, null=True, verbose_name='测试策略')),
                ('event_type', models.CharField(max_length=50, verbose_name='日志类型')),
                ('exec_date', models.DateField(verbose_name='执行日期')),
                ('status', models.IntegerField(default=0, verbose_name='状态')),
                ('freq', models.CharField(default='D', max_length=5, verbose_name='k线频率')),
                ('exception_tscode', models.CharField(blank=True, max_length=30000, null=True, verbose_name='日志类型')),
            ],
        ),
        migrations.CreateModel(
            name='PickedStocksMeetStrategy',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('strategy_code', models.CharField(db_index=True, max_length=25, verbose_name='策略代码')),
                ('ts_code', models.CharField(db_index=True, max_length=15, verbose_name='股票代码')),
                ('stock_name', models.CharField(max_length=15, verbose_name='股票名称')),
                ('trade_date', models.DateField(verbose_name='交易日')),
                ('test_freq', models.CharField(default='D', max_length=5, verbose_name='K线周期')),
                ('done_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='操作者')),
            ],
            options={
                'verbose_name': '选股结果',
                'verbose_name_plural': '选股结果',
                'ordering': ['ts_code'],
            },
        ),
        migrations.DeleteModel(
            name='MarkCriticalPointTask',
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('UPD_CP', '更新临界点'), ('EXP_PCT_UPD', '更新预期涨幅'), ('PERIOD_UPD', '更新高低点涨幅'), ('DOWNLOAD', '下载历史交易'), ('MARK_CP', '标记临界点'), ('PERIOD_TEST', '标记高低点涨幅'), ('EXP_PCT_TEST', '标记预期涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('W', '周线'), ('60', '60分钟'), ('M', '月线'), ('D', '日线'), ('30', '30分钟'), ('15', '15分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]