# Generated by Django 3.0.7 on 2020-06-25 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0006_stocknamecodemap_is_marked_dingdi'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocknamecodemap',
            name='is_marked_wm',
            field=models.BooleanField(blank=True, null=True, verbose_name='是否标注Wd底/M顶？'),
        ),
    ]
