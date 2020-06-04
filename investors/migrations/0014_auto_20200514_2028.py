# Generated by Django 3.0.2 on 2020-05-14 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0013_auto_20200514_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('30', '30分钟'), ('60', '60分钟'), ('dd', '日线'), ('mm', '月线'), ('wk', '周线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]
