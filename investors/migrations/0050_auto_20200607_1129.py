# Generated by Django 3.0.2 on 2020-06-07 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0049_auto_20200607_0732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('60', '60分钟'), ('15', '15分钟'), ('W', '周线'), ('M', '月线'), ('30', '30分钟'), ('D', '日线')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
