# Generated by Django 3.0.2 on 2021-10-31 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0035_auto_20211031_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='province',
            name='province_pinyin',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='省份拼音'),
        ),
    ]