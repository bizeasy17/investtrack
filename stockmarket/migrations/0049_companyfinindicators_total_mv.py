# Generated by Django 3.2.10 on 2022-03-05 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0048_rename_price_companyfinindicators_close'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyfinindicators',
            name='total_mv',
            field=models.FloatField(blank=True, null=True, verbose_name='总市值'),
        ),
    ]