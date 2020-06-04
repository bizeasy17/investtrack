# Generated by Django 3.0.2 on 2020-05-21 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0016_auto_20200521_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockstrategytestlog',
            name='cp_marked_dt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='临界点标记时间？'),
        ),
        migrations.AddField(
            model_name='stockstrategytestlog',
            name='cp_update_dt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='临界点更新时间？'),
        ),
        migrations.AddField(
            model_name='stockstrategytestlog',
            name='exppct_mark_dt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='预期涨幅标记时间？'),
        ),
        migrations.AddField(
            model_name='stockstrategytestlog',
            name='exppct_mark_update_dt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='预期涨幅更新时间？'),
        ),
        migrations.AddField(
            model_name='stockstrategytestlog',
            name='hist_download_dt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='下载时间？'),
        ),
        migrations.AddField(
            model_name='stockstrategytestlog',
            name='hist_update_dt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='下载更新时间？'),
        ),
        migrations.AddField(
            model_name='stockstrategytestlog',
            name='lhpct_mark_dt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='高低点标记时间？'),
        ),
        migrations.AddField(
            model_name='stockstrategytestlog',
            name='lhpct_update_dt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='高低点更新时间？'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('60', '60分钟'), ('mm', '月线'), ('wk', '周线'), ('15', '15分钟'), ('30', '30分钟'), ('dd', '日线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]
