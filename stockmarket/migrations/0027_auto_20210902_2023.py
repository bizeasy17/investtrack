# Generated by Django 3.0.2 on 2021-09-02 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0026_auto_20210327_0813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companymanagers',
            name='begin_date',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='上任日期'),
        ),
        migrations.AlterField(
            model_name='companymanagers',
            name='end_date',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='离任日期'),
        ),
    ]