# Generated by Django 3.0.2 on 2020-02-04 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investmgr', '0017_auto_20200203_2104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stocknamecodemap',
            name='is_valid',
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('30', '30分钟'), ('wk', '周线'), ('60', '60分钟'), ('dd', '日线'), ('15', '15分钟'), ('mm', '月线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]
