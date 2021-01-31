# Generated by Django 3.0.2 on 2021-01-30 01:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_useractiontrace_userquerytrace'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBackTestTrace',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新时间')),
                ('ts_code', models.CharField(blank=True, max_length=255, verbose_name='股票代码')),
                ('strategy_code', models.CharField(blank=True, max_length=255, verbose_name='策略代码')),
                ('btest_type', models.CharField(blank=True, max_length=255, verbose_name='回测类型')),
                ('btest_param', models.CharField(blank=True, max_length=255, verbose_name='回测参数')),
                ('request_url', models.CharField(blank=True, max_length=255, verbose_name='请求的url')),
                ('ip_addr', models.CharField(blank=True, max_length=50, null=True, verbose_name='访问ip')),
                ('uid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户id')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserBackTestFilterTrace',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新时间')),
                ('ts_code', models.CharField(blank=True, max_length=255, verbose_name='股票代码')),
                ('filter_category', models.CharField(blank=True, max_length=255, verbose_name='过滤器类别')),
                ('filter_name', models.CharField(blank=True, max_length=255, verbose_name='过滤器名称')),
                ('filter_val', models.CharField(blank=True, max_length=255, verbose_name='过滤器值')),
                ('backtest_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.UserBackTestTrace', verbose_name='回测id')),
                ('uid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户id')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
