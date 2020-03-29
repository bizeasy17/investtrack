# Generated by Django 3.0.2 on 2020-03-28 08:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investmgr', '0049_auto_20200328_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockfollowing',
            name='stock_code',
            field=models.CharField(max_length=50, verbose_name='股票代码'),
        ),
        migrations.AlterField(
            model_name='stockpositionsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('m', '月'), ('d', '日'), ('w', '周')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradeprofitsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('m', '月'), ('d', '日'), ('w', '周')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('30', '30分钟'), ('15', '15分钟'), ('60', '60分钟'), ('mm', '月线'), ('wk', '周线'), ('dd', '日线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
        migrations.AlterUniqueTogether(
            name='stockfollowing',
            unique_together={('stock_code', 'trader')},
        ),
    ]
