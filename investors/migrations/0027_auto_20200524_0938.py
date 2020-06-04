# Generated by Django 3.0.2 on 2020-05-24 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0026_auto_20200524_0933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tradestrategy',
            name='is_sys',
        ),
        migrations.AddField(
            model_name='tradestrategy',
            name='is_manual',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='手工创建？'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('30', '30分钟'), ('dd', '日线'), ('mm', '月线'), ('60', '60分钟'), ('wk', '周线')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
    ]
