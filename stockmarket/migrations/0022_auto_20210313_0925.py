# Generated by Django 3.0.7 on 2021-03-13 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0021_auto_20210313_0811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companybasic',
            name='introduction',
            field=models.CharField(blank=True, max_length=5000, null=True, verbose_name='介绍'),
        ),
    ]
