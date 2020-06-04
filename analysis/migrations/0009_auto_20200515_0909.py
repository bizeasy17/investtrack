# Generated by Django 3.0.2 on 2020-05-15 01:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0008_auto_20200514_2028'),
    ]

    operations = [
        migrations.CreateModel(
            name='BStrategyOnPctTest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('name', models.CharField(max_length=30, verbose_name='策略名')),
                ('ts_code', models.CharField(max_length=15, verbose_name='股票代码')),
                ('b_10_pct_min', models.FloatField(blank=True, default=-1, null=True, verbose_name='+10%最小周期')),
                ('b_10_pct_max', models.FloatField(blank=True, default=-1, null=True, verbose_name='+10%最大周期')),
                ('b_10_pct_mean', models.FloatField(blank=True, default=-1, null=True, verbose_name='+10%平均周期')),
                ('b_20_pct_min', models.FloatField(blank=True, default=-1, null=True, verbose_name='+20%最小周期')),
                ('b_20_pct_max', models.FloatField(blank=True, default=-1, null=True, verbose_name='+20%最大周期')),
                ('b_20_pct_mean', models.FloatField(blank=True, default=-1, null=True, verbose_name='+20%平均周期')),
                ('b_30_pct_min', models.FloatField(blank=True, default=-1, null=True, verbose_name='+30%最小周期')),
                ('b_30_pct_max', models.FloatField(blank=True, default=-1, null=True, verbose_name='+30%最大周期')),
                ('b_30_pct_mean', models.FloatField(blank=True, default=-1, null=True, verbose_name='+30%平均周期')),
                ('b_50_pct_min', models.FloatField(blank=True, default=-1, null=True, verbose_name='+50%最小周期')),
                ('b_50_pct_max', models.FloatField(blank=True, default=-1, null=True, verbose_name='+50%最大周期')),
                ('b_50_pct_mean', models.FloatField(blank=True, default=-1, null=True, verbose_name='+50%平均周期')),
                ('b_80_pct_min', models.FloatField(blank=True, default=-1, null=True, verbose_name='+80%最小周期')),
                ('b_80_pct_max', models.FloatField(blank=True, default=-1, null=True, verbose_name='+80%最大周期')),
                ('b_80_pct_mean', models.FloatField(blank=True, default=-1, null=True, verbose_name='+80%平均周期')),
                ('b_100_pct_min', models.FloatField(blank=True, default=-1, null=True, verbose_name='+100%最小周期')),
                ('b_100_pct_max', models.FloatField(blank=True, default=-1, null=True, verbose_name='+100%最大周期')),
                ('b_100_pct_mean', models.FloatField(blank=True, default=-1, null=True, verbose_name='+100%平均周期')),
                ('test_period', models.CharField(default='D', max_length=5, verbose_name='测试周期')),
            ],
            options={
                'verbose_name': '达到固定涨幅周期测试',
                'verbose_name_plural': '达到固定涨幅周期测试',
                'ordering': ['ts_code'],
            },
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('60', '60分钟'), ('mm', '月线'), ('dd', '日线'), ('30', '30分钟'), ('wk', '周线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]