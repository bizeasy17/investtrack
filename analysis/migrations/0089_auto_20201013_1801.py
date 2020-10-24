# Generated by Django 3.0.7 on 2020-10-13 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0088_auto_20201011_1539'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockhistorydaily',
            old_name='ma200_diepo_v1',
            new_name='ma200_diepo',
        ),
        migrations.RenameField(
            model_name='stockhistorydaily',
            old_name='ma200_tupo_v1',
            new_name='ma200_tupo',
        ),
        migrations.RenameField(
            model_name='stockhistorydaily',
            old_name='ma200_yali_v1',
            new_name='ma200_yali',
        ),
        migrations.RenameField(
            model_name='stockhistorydaily',
            old_name='ma200_zhicheng_v1',
            new_name='ma200_zhicheng',
        ),
        migrations.RenameField(
            model_name='stockhistorydaily',
            old_name='ma60_diepo_v1',
            new_name='ma60_diepo',
        ),
        migrations.RenameField(
            model_name='stockhistorydaily',
            old_name='ma60_tupo_v1',
            new_name='ma60_tupo',
        ),
        migrations.RenameField(
            model_name='stockhistorydaily',
            old_name='ma60_yali_v1',
            new_name='ma60_yali',
        ),
        migrations.RenameField(
            model_name='stockhistorydaily',
            old_name='ma60_zhicheng_v1',
            new_name='ma60_zhicheng',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_diepo_s',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_diepo_v2',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_tupo_b',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_tupo_v2',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_yali_s',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_yali_v2',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_zhicheng_b',
        ),
        migrations.RemoveField(
            model_name='stockhistorydaily',
            name='ma25_zhicheng_v2',
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma25_diepo',
            field=models.IntegerField(blank=True, null=True, verbose_name='MA25均线跌破'),
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma25_tupo',
            field=models.IntegerField(blank=True, null=True, verbose_name='MA25均线突破'),
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma25_yali',
            field=models.IntegerField(blank=True, null=True, verbose_name='MA25压力'),
        ),
        migrations.AddField(
            model_name='stockhistorydaily',
            name='ma25_zhicheng',
            field=models.IntegerField(blank=True, null=True, verbose_name='MA25均线支撑'),
        ),
        migrations.AlterField(
            model_name='stockstrategytestlog',
            name='event_type',
            field=models.CharField(choices=[('EXP_PCT_UPD', '更新预期涨幅'), ('UPD_DOWNLOAD', '更新下载历史交易'), ('PERIOD_UPD', '更新高低点涨幅'), ('UPD_CP', '更新临界点'), ('EXP_PCT_TEST', '标记预期涨幅'), ('PERIOD_TEST', '标记高低点涨幅'), ('DOWNLOAD', '下载历史交易'), ('MARK_CP', '标记临界点')], max_length=50, verbose_name='日志类型'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('D', '日线'), ('M', '月线'), ('W', '周线'), ('30', '30分钟'), ('60', '60分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]