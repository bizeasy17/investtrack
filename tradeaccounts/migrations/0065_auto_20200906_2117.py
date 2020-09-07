# Generated by Django 3.0.2 on 2020-09-06 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeaccounts', '0064_auto_20200906_0956'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stockpositionsnapshot',
            options={'get_latest_by': 'id', 'ordering': ['-snap_date'], 'verbose_name': '股票收益快照', 'verbose_name_plural': '股票收益快照'},
        ),
        migrations.AddField(
            model_name='stockpositionsnapshot',
            name='p_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='持仓编号'),
        ),
        migrations.AlterField(
            model_name='stockpositionsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('m', '月'), ('d', '日'), ('w', '周')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradeaccountsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('m', '月'), ('d', '日'), ('w', '周')], default='d', max_length=1, verbose_name='收益周期'),
        ),
    ]
