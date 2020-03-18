# Generated by Django 3.0.2 on 2020-03-18 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investmgr', '0044_auto_20200315_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockpositionsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('d', '日'), ('w', '周'), ('m', '月')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradeprofitsnapshot',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('d', '日'), ('w', '周'), ('m', '月')], default='d', max_length=1, verbose_name='收益周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('mm', '月线'), ('30', '30分钟'), ('15', '15分钟'), ('wk', '周线'), ('60', '60分钟'), ('dd', '日线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]
