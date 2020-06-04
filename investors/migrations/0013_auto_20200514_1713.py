# Generated by Django 3.0.2 on 2020-05-14 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0012_auto_20200513_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradestrategy',
            name='code',
            field=models.CharField(default='jz_b', max_length=10, verbose_name='策略代码'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('30', '30分钟'), ('wk', '周线'), ('60', '60分钟'), ('15', '15分钟'), ('dd', '日线'), ('mm', '月线')], default='60', max_length=2, verbose_name='应用周期'),
        ),
    ]