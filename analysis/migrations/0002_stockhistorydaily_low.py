# Generated by Django 3.0.2 on 2020-05-07 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockhistorydaily',
            name='low',
            field=models.FloatField(blank=True, null=True, verbose_name='最低价'),
        ),
    ]