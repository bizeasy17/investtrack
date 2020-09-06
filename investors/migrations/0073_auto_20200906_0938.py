# Generated by Django 3.0.2 on 2020-09-06 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0072_auto_20200709_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('W', '周线'), ('30', '30分钟'), ('15', '15分钟'), ('M', '月线'), ('60', '60分钟'), ('D', '日线')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
