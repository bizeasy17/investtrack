# Generated by Django 3.0.2 on 2021-10-17 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0029_auto_20210919_1111'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyDailyBasicExt',
            fields=[
                ('companydailybasic_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='stockmarket.CompanyDailyBasic')),
                ('stock_name', models.CharField(max_length=50, verbose_name='股票名称')),
                ('chg_pct', models.FloatField(verbose_name='涨跌幅')),
                ('vol', models.FloatField(verbose_name='成交量')),
                ('amount', models.FloatField(verbose_name='成交额')),
                ('jiuzhuan_b', models.IntegerField(verbose_name='九转买')),
                ('jiuzhuan_s', models.IntegerField(verbose_name='九转卖')),
                ('industry', models.CharField(max_length=50, verbose_name='所属行业')),
            ],
            options={
                'verbose_name': '股票基本面',
                'verbose_name_plural': '股票基本面',
                'ordering': ['ts_code'],
            },
            bases=('stockmarket.companydailybasic',),
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry', models.CharField(max_length=50, verbose_name='行业')),
                ('stock_count', models.IntegerField(verbose_name='股票数')),
                ('snap_date', models.DateField(verbose_name='统计日期')),
                ('pe_10pct', models.FloatField(verbose_name='PE低位')),
                ('pe_50pct', models.FloatField(verbose_name='PE中位')),
                ('pe_90pct', models.FloatField(verbose_name='PE高位')),
                ('pb_10pct', models.FloatField(verbose_name='PB低位')),
                ('pb_50pct', models.FloatField(verbose_name='PB中位')),
                ('pb_90pct', models.FloatField(verbose_name='PB高位')),
                ('ps_10pct', models.FloatField(verbose_name='PS低位')),
                ('ps_50pct', models.FloatField(verbose_name='PS中位')),
                ('ps_90pct', models.FloatField(verbose_name='PS高位')),
            ],
            options={
                'verbose_name': '行业',
                'verbose_name_plural': '行业',
                'ordering': ['industry'],
            },
        ),
    ]