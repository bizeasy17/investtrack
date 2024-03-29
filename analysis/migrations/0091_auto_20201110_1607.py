# Generated by Django 3.0.7 on 2020-11-10 08:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0090_auto_20201108_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysiseventlog',
            name='created_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='analysiseventlog',
            name='last_mod_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间'),
        ),
        migrations.AlterField(
            model_name='analysiseventlog',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('EXP_PCT_TEST', '标记预期涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易'), ('PERIOD_TEST', '标记高低点涨幅'), ('PERIOD_UPD', '更新高低点涨幅'), ('DOWNLOAD', '下载历史交易'), ('EXP_PCT_UPD', '更新预期涨幅'), ('UPD_CP', '更新临界点'), ('MARK_CP', '标记临界点')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('30', '30分钟'), ('M', '月线'), ('60', '60分钟'), ('W', '周线'), ('D', '日线'), ('15', '15分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
