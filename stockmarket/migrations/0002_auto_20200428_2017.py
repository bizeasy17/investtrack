# Generated by Django 3.0.2 on 2020-04-28 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocknamecodemap',
            name='delist_date',
            field=models.DateField(blank=True, null=True, verbose_name='退市日期'),
        ),
        migrations.AlterField(
            model_name='stocknamecodemap',
            name='list_date',
            field=models.DateField(blank=True, null=True, verbose_name='上市日期'),
        ),
    ]
