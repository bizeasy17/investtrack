# Generated by Django 3.0.2 on 2020-05-08 22:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('analysis', '0004_auto_20200508_2040'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradeStrategyStat',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('applied_period', models.CharField(blank=True, choices=[('dd', '日线'), ('60', '60分钟'), ('15', '15分钟'), ('30', '30分钟'), ('wk', '周线'), ('mm', '月线')], default='60', max_length=2, verbose_name='应用周期')),
                ('name', models.CharField(max_length=30, verbose_name='策略名')),
                ('count', models.IntegerField(default=0, verbose_name='引用数量')),
                ('success_count', models.IntegerField(default=0, verbose_name='成功次数')),
                ('fail_count', models.IntegerField(default=0, verbose_name='失败次数')),
                ('success_rate', models.IntegerField(default=0, verbose_name='成功率')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
                ('parent_strategy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='analysis.TradeStrategyStat', verbose_name='父级策略')),
            ],
            options={
                'verbose_name': '交易策略统计',
                'verbose_name_plural': '交易策略统计',
                'ordering': ['name'],
            },
        ),
    ]