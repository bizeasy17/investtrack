# Generated by Django 3.0.2 on 2020-05-07 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tradeaccounts', '0005_auto_20200605_0814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeaccountsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('d', '日'), ('m', '月'), ('w', '周')], default='d', max_length=1, verbose_name='收益周期'),
        ),
    ]
