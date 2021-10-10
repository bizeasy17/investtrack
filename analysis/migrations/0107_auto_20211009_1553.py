# Generated by Django 3.0.2 on 2021-10-09 07:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0106_auto_20210925_1204'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockHistoryDailyArc',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('ts_code', models.CharField(db_index=True, max_length=15, verbose_name='TS代码')),
                ('trade_date', models.DateField(max_length=6, verbose_name='交易日')),
                ('open', models.FloatField(blank=True, null=True, verbose_name='开盘价')),
                ('high', models.FloatField(blank=True, null=True, verbose_name='最高价')),
                ('low', models.FloatField(blank=True, null=True, verbose_name='最低价')),
                ('pre_close', models.FloatField(blank=True, null=True, verbose_name='前日收盘价')),
                ('close', models.FloatField(blank=True, null=True, verbose_name='收盘价')),
                ('change', models.FloatField(blank=True, null=True, verbose_name='价格变化')),
                ('pct_chg', models.FloatField(blank=True, null=True, verbose_name='价格变化%')),
                ('vol', models.FloatField(blank=True, null=True, verbose_name='交易量')),
                ('amount', models.FloatField(blank=True, null=True, verbose_name='金额')),
                ('chg4', models.FloatField(blank=True, null=True, verbose_name='与4日前变化')),
                ('jiuzhuan_count_b', models.FloatField(blank=True, null=True, verbose_name='九转序列B')),
                ('jiuzhuan_count_s', models.FloatField(blank=True, null=True, verbose_name='九转序列S')),
                ('ma25', models.FloatField(blank=True, null=True, verbose_name='MA25')),
                ('ma25_slope', models.FloatField(blank=True, null=True, verbose_name='MA25斜率')),
                ('ma60', models.FloatField(blank=True, null=True, verbose_name='MA60')),
                ('ma60_slope', models.FloatField(blank=True, null=True, verbose_name='MA60斜率')),
                ('ma200', models.FloatField(blank=True, null=True, verbose_name='MA200')),
                ('ma200_slope', models.FloatField(blank=True, null=True, verbose_name='MA200斜率')),
                ('slope', models.FloatField(blank=True, null=True, verbose_name='斜率')),
                ('freq', models.CharField(default='D', max_length=5, verbose_name='周期')),
            ],
            options={
                'verbose_name': '股票代码表',
                'verbose_name_plural': '股票代码表',
                'ordering': ['-last_mod_time'],
                'get_latest_by': 'id',
            },
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='di_min',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='dibu_b',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='diepo_s',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ding_max',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='dingbu_s',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='dingdi_count',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='is_dingdi_end',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='m_ding',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma200_diepo',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma200_tupo',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma200_yali',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma200_zhicheng',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_diepo',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_tupo',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_yali',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_zhicheng',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma60_diepo',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma60_tupo',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma60_yali',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma60_zhicheng',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='tupo_b',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='w_di',
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('UPD_CP', '更新临界点'), ('EXP_PCT_TEST', '标记预期涨幅'), ('EXP_PCT_UPD', '更新预期涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易'), ('DOWNLOAD', '下载历史交易'), ('MARK_CP', '标记临界点'), ('PERIOD_UPD', '更新高低点涨幅'), ('PERIOD_TEST', '标记高低点涨幅')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterUniqueTogether(
            name='industrybasicquantilestat',
            unique_together={('industry', 'basic_type', 'quantile', 'snap_date')},
        ),
    ]
