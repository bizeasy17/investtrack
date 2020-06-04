# Generated by Django 3.0.2 on 2020-06-02 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investors', '0040_auto_20200601_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradestrategy',
            name='applied_period',
            field=models.CharField(blank=True, choices=[('60', '60分钟'), ('mm', '月线'), ('30', '30分钟'), ('15', '15分钟'), ('dd', '日线'), ('wk', '周线')], default='60', max_length=2, null=True, verbose_name='应用周期'),
        ),
        migrations.AlterField(
            model_name='tradestrategy',
            name='code',
            field=models.CharField(choices=[('break_through', '突破阻力位'), ('fall_below', '跌破支撑位'), ('take_profit', '止盈'), ('shuangdi_b', '双底买点'), ('shuangtou_s', '双头卖点'), ('sell', '卖出'), ('add_positions', '加仓'), ('jiuzhuan_s', '九转序列卖点'), ('jiuzhuan_b', '九转序列买点'), ('stop_loss', '止损'), ('buy', '买入')], default='buy', max_length=50, verbose_name='策略代码'),
        ),
    ]
