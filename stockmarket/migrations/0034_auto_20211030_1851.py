# Generated by Django 3.0.2 on 2021-10-30 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stockmarket', '0033_auto_20211030_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='city_pinyin',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='城市拼音'),
        ),
        migrations.AddField(
            model_name='companybasic',
            name='chengshi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_city', to='stockmarket.City'),
        ),
        migrations.AddField(
            model_name='companybasic',
            name='shengfen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_province', to='stockmarket.Province'),
        ),
        migrations.AddField(
            model_name='province',
            name='province_pinyin',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='省份拼音'),
        ),
        migrations.AddField(
            model_name='stocknamecodemap',
            name='province',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='province', to='stockmarket.Province'),
        ),
    ]
