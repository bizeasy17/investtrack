# Generated by Django 3.0.2 on 2021-01-10 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0013_stocknamecodemap_last_analyze_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocknamecodemap',
            name='stock_name_pinyin',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='股票名称拼音'),
        ),
    ]
