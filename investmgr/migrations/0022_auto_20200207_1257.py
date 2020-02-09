# Generated by Django 3.0.2 on 2020-02-07 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investmgr', '0021_auto_20200206_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='positions',
            name='profit_ratio',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='利润率'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('60', '60分钟'), ('dd', '日线'), ('30', '30分钟'), ('15', '15分钟'), ('wk', '周线'), ('mm', '月线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]