# Generated by Django 3.0.7 on 2021-03-20 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0024_auto_20210313_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companybasic',
            name='business_scope',
            field=models.CharField(blank=True, max_length=5000, null=True, verbose_name='经营范围'),
        ),
        migrations.AlterField(
            model_name='companybasic',
            name='main_business',
            field=models.CharField(blank=True, max_length=5000, null=True, verbose_name='主营业务'),
        ),
    ]
