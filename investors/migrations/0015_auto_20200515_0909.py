# Generated by Django 3.0.2 on 2020-05-15 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0014_auto_20200514_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('60', '60分钟'), ('mm', '月线'), ('dd', '日线'), ('30', '30分钟'), ('wk', '周线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]