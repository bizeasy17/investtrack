# Generated by Django 3.0.2 on 2021-11-13 08:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0036_auto_20211031_0936'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyBasicFilter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('last_mod_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后更新时间')),
                ('ts_code', models.CharField(db_index=True, max_length=50, verbose_name='TS代码')),
                ('trade_date', models.DateField(blank=True, null=True, verbose_name='交易日期')),
                ('turnover_rate', models.IntegerField(blank=True, null=True, verbose_name='换手率')),
                ('turnover_rate_f', models.IntegerField(blank=True, null=True, verbose_name='换手率(自由流通)')),
                ('volume_ratio', models.IntegerField(blank=True, null=True, verbose_name='量比')),
                ('pe', models.IntegerField(blank=True, null=True, verbose_name='市盈率')),
                ('pe_ttm', models.IntegerField(blank=True, null=True, verbose_name='市盈率TTM')),
                ('pb', models.IntegerField(blank=True, null=True, verbose_name='市净率')),
                ('ps', models.IntegerField(blank=True, null=True, verbose_name='市销率')),
                ('ps_ttm', models.IntegerField(blank=True, null=True, verbose_name='市销率TTM')),
                ('dv_ratio', models.IntegerField(blank=True, null=True, verbose_name='股息')),
                ('dv_ttm', models.IntegerField(blank=True, null=True, verbose_name='股息率TTM')),
                ('total_share', models.IntegerField(blank=True, null=True, verbose_name='总股本')),
                ('float_share', models.IntegerField(blank=True, null=True, verbose_name='流通股本')),
                ('free_share', models.IntegerField(blank=True, null=True, verbose_name='自由流通股本')),
                ('total_mv', models.IntegerField(blank=True, null=True, verbose_name='总市值')),
                ('circ_mv', models.IntegerField(blank=True, null=True, verbose_name='流通市值')),
                ('company', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='basic_filter', to='stockmarket.StockNameCodeMap')),
            ],
            options={
                'verbose_name': '公司基本面过滤器',
                'verbose_name_plural': '公司基本面过滤器',
                'ordering': ['-ts_code'],
                'get_latest_by': 'id',
            },
        ),
    ]
