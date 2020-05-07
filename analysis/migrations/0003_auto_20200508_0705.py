# Generated by Django 3.0.2 on 2020-05-07 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0002_stockhistorydaily_low'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockhistorydaily',
            name='jiuzhuan_count_s',
            field=models.FloatField(default=-1, verbose_name='九转序列S'),
        ),
        migrations.AlterField(
            model_name='stockhistorydaily',
            name='jiuzhuan_count',
            field=models.FloatField(default=-1, verbose_name='九转序列B'),
        ),
    ]