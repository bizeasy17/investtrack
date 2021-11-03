# Generated by Django 3.0.2 on 2021-10-31 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0034_auto_20211030_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='city_pinyin',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='城市拼音'),
        ),
        migrations.AlterUniqueTogether(
            name='city',
            unique_together={('name', 'province')},
        ),
        migrations.AlterUniqueTogether(
            name='province',
            unique_together={('name', 'country')},
        ),
    ]
