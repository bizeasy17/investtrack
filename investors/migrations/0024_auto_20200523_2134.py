# Generated by Django 3.0.2 on 2020-05-23 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0023_auto_20200521_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('dd', '日线'), ('60', '60分钟'), ('mm', '月线'), ('wk', '周线'), ('30', '30分钟'), ('15', '15分钟')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]