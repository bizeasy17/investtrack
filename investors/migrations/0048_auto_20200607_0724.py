# Generated by Django 3.0.2 on 2020-06-06 23:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0047_auto_20200607_0720'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradestrategy',
            name='ana_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='investors.StrategyAnalysisCode', verbose_name='分析代码'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('15', '15分钟'), ('wk', '周线'), ('30', '30分钟'), ('mm', '月线'), ('60', '60分钟'), ('dd', '日线')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='code',
            field=models.CharField(blank=True, choices=[('tupo_b', '突破阻力位'), ('diepo_s', '跌破支撑位'), ('jiuzhuan_s', '九转序列卖点'), ('jiuzhuan_b', '九转序列买点'), ('shuangdi_b', '双底买点'), ('shuangtou_s', '双头卖点'), ('ma25_b', 'MA25支撑位')], max_length=50, null=True, verbose_name='策略代码'),
        ),
    ]
