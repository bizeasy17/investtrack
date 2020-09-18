# Generated by Django 3.0.7 on 2020-09-11 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeaccounts', '0069_auto_20200911_0830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockpositionsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('m', '月'), ('w', '周'), ('d', '日')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradeaccountsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('m', '月'), ('w', '周'), ('d', '日')], default='d', max_length=1, verbose_name='收益周期'),
        ),
    ]
