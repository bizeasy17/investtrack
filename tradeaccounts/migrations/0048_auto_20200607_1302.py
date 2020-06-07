# Generated by Django 3.0.2 on 2020-06-07 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeaccounts', '0047_auto_20200607_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeaccountsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('w', '周'), ('m', '月'), ('d', '日')], default='d', max_length=1, verbose_name='收益周期'),
        ),
    ]
