# Generated by Django 3.0.2 on 2020-05-21 07:11

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0022_auto_20200521_1511'),
        ('analysis', '0015_auto_20200520_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('dd', '日线'), ('mm', '月线'), ('15', '15分钟'), ('30', '30分钟'), ('60', '60分钟'), ('wk', '周线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
        migrations.CreateModel(
            name='StockStrategyTestLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('ts_code', models.CharField(db_index=True, max_length=15, verbose_name='TS代码')),
                ('hist_downloaded', models.BooleanField(default=False, verbose_name='交易已下载？')),
                ('critical_point_marked', models.BooleanField(default=False, verbose_name='临界点已标记？')),
                ('low_high_pct_marked', models.BooleanField(default=False, verbose_name='高低点涨幅已标记？')),
                ('exp_pct_marked', models.BooleanField(default=False, verbose_name='预期涨幅已标记？')),
                ('strategy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='investors.TradeStrategy', verbose_name='测试策略')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]