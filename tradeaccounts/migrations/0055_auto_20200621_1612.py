# Generated by Django 3.0.7 on 2020-06-21 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeaccounts', '0054_auto_20200621_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeaccountsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('w', '周'), ('m', '月'), ('d', '日')], default='d', max_length=1, verbose_name='收益周期'),
        ),
    ]
