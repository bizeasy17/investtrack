# Generated by Django 3.0.7 on 2020-09-22 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0084_auto_20200921_1918'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma200',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma60',
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma200_slope',
            field=models.FloatField(blank=True, null=True, verbose_name='MA200斜率'),
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma25_diepo_v2',
            field=models.IntegerField(blank=True, null=True, verbose_name='MA25均线跌破V2'),
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma25_slope',
            field=models.FloatField(blank=True, null=True, verbose_name='MA25斜率'),
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma25_tupo_v2',
            field=models.IntegerField(blank=True, null=True, verbose_name='MA25均线突破V2'),
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma25_yali_v2',
            field=models.IntegerField(blank=True, null=True, verbose_name='MA25压力v2'),
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma25_zhicheng_v2',
            field=models.IntegerField(blank=True, null=True, verbose_name='MA25均线支撑V2'),
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma60_slope',
            field=models.FloatField(blank=True, null=True, verbose_name='MA60斜率'),
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('DOWNLOAD', '下载历史交易'), ('UPD_DOWNLOAD', '更新下载历史交易'), ('PERIOD_UPD', '更新高低点涨幅'), ('EXP_PCT_UPD', '更新预期涨幅'), ('PERIOD_TEST', '标记高低点涨幅'), ('EXP_PCT_TEST', '标记预期涨幅'), ('MARK_CP', '标记临界点'), ('UPD_CP', '更新临界点')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('D', '日线'), ('W', '周线'), ('M', '月线'), ('30', '30分钟'), ('60', '60分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
