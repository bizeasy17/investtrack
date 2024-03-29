# Generated by Django 3.0.2 on 2020-05-20 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0014_auto_20200518_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='bstrategyonpcttest',
            name='b_130_pct_max',
            field=models.FloatField(blank=True, default=-1, null=True, verbose_name='+13%最大周期'),
        ),
        migrations.AddField(
            model_name='bstrategyonpcttest',
            name='b_130_pct_mean',
            field=models.FloatField(blank=True, default=-1, null=True, verbose_name='+130%平均周期'),
        ),
        migrations.AddField(
            model_name='bstrategyonpcttest',
            name='b_130_pct_min',
            field=models.FloatField(blank=True, default=-1, null=True, verbose_name='+130%最小周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategystat',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('60', '60分钟'), ('dd', '日线'), ('15', '15分钟'), ('wk', '周线'), ('30', '30分钟'), ('mm', '月线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]
