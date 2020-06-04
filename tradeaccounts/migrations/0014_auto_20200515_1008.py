# Generated by Django 3.0.2 on 2020-05-15 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeaccounts', '0013_auto_20200515_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeaccountsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('d', '日'), ('m', '月'), ('w', '周')], default='d', max_length=1, verbose_name='收益周期'),
        ),
    ]