# Generated by Django 3.0.2 on 2020-05-27 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeaccounts', '0027_auto_20200525_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeaccountsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('w', '周'), ('d', '日'), ('m', '月')], default='d', max_length=1, verbose_name='收益周期'),
        ),
    ]
