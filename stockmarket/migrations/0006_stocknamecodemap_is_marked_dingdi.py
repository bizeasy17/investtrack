# Generated by Django 3.0.7 on 2020-06-17 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0005_auto_20200525_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocknamecodemap',
            name='is_marked_dingdi',
            field=models.BooleanField(default=False, verbose_name='是否标注顶底'),
        ),
    ]
