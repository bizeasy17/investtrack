# Generated by Django 3.0.2 on 2020-06-28 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeaccounts', '0062_auto_20200627_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeaccountsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('d', '日'), ('w', '周'), ('m', '月')], default='d', max_length=1, verbose_name='收益周期'),
        ),
    ]