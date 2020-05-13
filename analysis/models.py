import random
import string
from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import date, datetime, timedelta
import decimal

import tushare as ts
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Sum
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from investors.models import TradeStrategy
# Create your models here.


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(_('创建时间'), default=now)
    last_mod_time = models.DateTimeField(_('最后更新时间'), default=now)

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


class StockHistoryDaily(BaseModel):
    '''
    ts_code	str	股票代码
    trade_date	str	交易日期
    open	float	开盘价
    high	float	最高价
    low	float	最低价
    close	float	收盘价
    pre_close	float	昨收价
    change	float	涨跌额
    pct_chg	float	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
    vol	float	成交量 （手）
    amount	float	成交额 （千元）
    '''

    ts_code = models.CharField(
        _('TS代码'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日'), max_length=6, blank=False, null=False)  # symbol, e.g. 20200505
    # new fields
    open = models.FloatField(
        _('开盘价'), blank=True, null=True)
    high = models.FloatField(
        _('最高价'), blank=True, null=True)
    low = models.FloatField(
        _('最低价'), blank=True, null=True)
    pre_close = models.FloatField(
        _('前日收盘价'), blank=True, null=True)
    close = models.FloatField(_('收盘价'), blank=True, null=True)
    change = models.FloatField(
        _('价格变化'), blank=True, null=True)
    pct_chg = models.FloatField(
        _('价格变化%'), blank=True, null=True)
    vol = models.FloatField(
        _('交易量'), blank=True, null=True)
    amount = models.FloatField(
        _('金额'), blank=True, null=True)
    chg4 = models.FloatField(
        _('与4日前变化'), blank=True, null=True)
    jiuzhuan_count_b = models.FloatField(
        _('九转序列B'),  blank=False, null=False, default=-1)
    jiuzhuan_count_s = models.FloatField(
        _('九转序列S'),  blank=False, null=False, default=-1)

    def __str__(self):
        return self.ts_code

    # def save(self, *args, **kwargs):
    #     self.stock_code = self.stock_code + '.' + self.market
    #     super.save(*args, **kwargs)

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('股票代码表')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

# class StockStatDaily(BaseModel):
#     '''
#     ts_code	str	股票代码
#     trade_date	str	交易日期
#     open	float	开盘价
#     high	float	最高价
#     low	float	最低价
#     close	float	收盘价
#     pre_close	float	昨收价
#     change	float	涨跌额
#     pct_chg	float	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
#     vol	float	成交量 （手）
#     amount	float	成交额 （千元）
#     '''
#     ts_code = models.CharField(
#         _('TS代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
#     trade_date = models.DateField(
#         _('交易日'), max_length=6, blank=False, null=False)  # symbol, e.g. 20200505
#     # new fields
#     open = models.FloatField(
#         _('开盘价'), blank=True, null=True)
#     high = models.FloatField(
#         _('最高价'), blank=True, null=True)
#     low = models.FloatField(
#         _('最低价'), blank=True, null=True)
#     pre_close = models.FloatField(
#         _('前日收盘价'), blank=True, null=True)
#     close = models.FloatField(_('收盘价'), blank=True, null=True)
#     change = models.FloatField(
#         _('价格变化'), blank=True, null=True)
#     pct_chg = models.FloatField(
#         _('价格变化%'), blank=True, null=True)
#     vol = models.FloatField(
#         _('交易量'), blank=True, null=True)
#     amount = models.FloatField(
#         _('金额'), blank=True, null=True)
#     chg4 = models.FloatField(
#         _('与4日前变化'), blank=True, null=True)
#     jiuzhuan_count_b = models.FloatField(
#         _('九转序列B'),  blank=False, null=False, default=-1, db_index=True)
#     jiuzhuan_count_s = models.FloatField(
#         _('九转序列S'),  blank=False, null=False, default=-1, db_index=True)

#     def __str__(self):
#         return self.ts_code


class BStrategyTestResultOnDays(BaseModel):
    '''
    ts_code	str	股票代码
    trade_date	str	交易日期
    open	float	开盘价
    high	float	最高价
    low	float	最低价
    close	float	收盘价
    pre_close	float	昨收价
    change	float	涨跌额
    pct_chg	float	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
    vol	float	成交量 （手）
    amount	float	成交额 （千元）
    '''
    ts_code = models.CharField(
        _('TS代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日'), blank=False, null=False)  # symbol, e.g. 20200505
    test_period = models.IntegerField(
        _('测试周期长度'), blank=True, null=False, default=10)
    # new fields
    open = models.FloatField(
        _('开盘价'), blank=True, null=True)
    high = models.FloatField(
        _('最高价'), blank=True, null=True)
    low = models.FloatField(
        _('最低价'), blank=True, null=True)
    pre_close = models.FloatField(
        _('前日收盘价'), blank=True, null=True)
    close = models.FloatField(_('收盘价'), blank=True, null=True)
    change = models.FloatField(
        _('价格变化'), blank=True, null=True)
    pct_chg = models.FloatField(
        _('涨幅%'), blank=True, null=True)
    vol = models.FloatField(
        _('交易量'), blank=True, null=True)
    amount = models.FloatField(
        _('金额'), blank=True, null=True)
    stage_low = models.BooleanField(
        _('低点?'), blank=True, null=True, default=False)
    stage_low_pct = models.FloatField(
        _('低点/买点%?'), blank=True, null=True, default=False)
    stage_high = models.BooleanField(
        _('高点?'), blank=True, null=True, default=False)
    stage_high_pct = models.FloatField(
        _('高点/买点%?'), blank=True, null=True, default=False)
    tnx_point = models.BooleanField(
        _('b点?'), blank=True, null=True, default=False)
    test_strategy = models.ForeignKey(TradeStrategy, verbose_name=_('测试策略'), blank=False, null=False,
                                      on_delete=models.CASCADE)

    def __str__(self):
        return self.ts_code

# class StrategyOnPctTest(BaseModel):
#     PERIOD_CHOICE = {
#         ('M', _('月线')),
#         ('W', _('周线')),
#         ('D', _('日线')),
#         ('60', _('60分钟')),
#         ('30', _('30分钟')),
#         ('15', _('15分钟')),
#     }
#     name = models.CharField(_('策略名'), max_length=30)
#     applied_period = models.CharField(
#         _('应用周期'), choices=PERIOD_CHOICE, max_length=2, blank=True, null=False, default='60')
#     creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
#                                 on_delete=models.CASCADE)
#     ts_code = models.CharField(
#         _('股票代码'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
#     b_10_min_pct_days = models.FloatField(
#         _('+10%最小天数'), blank=True, null=True, default=-1) 
#     b_10_pct_max_days = models.FloatField(
#         _('+10%最大天数'), blank=True, null=True, default=-1) 
#     b_10_pct_mean_days = models.FloatField(
#         _('+10%平均天数'), blank=True, null=True, default=-1) 
#     b_20_pct_min_days = models.FloatField(
#         _('+20%最小天数'), blank=True, null=True, default=-1)
#     b_20_pct_min_days = models.FloatField(
#         _('+20%最大天数'), blank=True, null=True, default=-1)
#     b_20_pct_min_days = models.FloatField(
#         _('+20%最小天数'), blank=True, null=True, default=-1)
#     b_30_pct_min_days = models.FloatField(
#         _('+30%最小天数'), blank=True, null=True, default=-1)
#     b_30_pct_max_days = models.FloatField(
#         _('+30%最大天数'), blank=True, null=True, default=-1)
#     b_50_pct_min_days = models.FloatField(
#         _('+50%最小天数'), blank=True, null=True, default=-1)
#     b_50_pct_max_days = models.FloatField(
#         _('+50%最大天数'), blank=True, null=True, default=-1)
#     b_50_pct_mean_days = models.FloatField(
#         _('+50%平均天数'), blank=True, null=True, default=-1)
#     b_80_pct_min_days = models.FloatField(
#         _('+80%最小天数'), blank=True, null=True, default=-1)
#     b_80_pct_max_days = models.FloatField(
#         _('+80%最大天数'), blank=True, null=True, default=-1)
#     b_80_pct_mean_days = models.FloatField(
#         _('+80%平均天数'), blank=True, null=True, default=-1)
#     b_100_pct_min_days = models.FloatField(
#         _('+100%最小天数'), blank=True, null=True, default=-1)
#     b_100_pct_max_days = models.FloatField(
#         _('+100%最大天数'), blank=True, null=True, default=-1)
#     b_100_pct_mean_days = models.FloatField(
#         _('+100%平均天数'), blank=True, null=True, default=-1)

# class StrategyOnDaysTest(BaseModel):
#     PERIOD_CHOICE = {
#         ('M', _('月线')),
#         ('W', _('周线')),
#         ('D', _('日线')),
#         ('60', _('60分钟')),
#         ('30', _('30分钟')),
#         ('15', _('15分钟')),
#     }
#     DURATION_CHOICE = {
#         ('10', _('10')),
#         ('20', _('20')),
#         ('30', _('30')),
#         ('50', _('50')),
#         ('80', _('80')),
#         ('130', _('130')),
#     }
#     name = models.CharField(_('策略名'), max_length=30)
#     applied_period = models.CharField(
#         _('应用周期'), choices=PERIOD_CHOICE, max_length=2, blank=True, null=False, default='D')
#     duration = models.CharField(
#         _('分析期间'), choices=DURATION_CHOICE, max_length=2, blank=True, null=False, default='20')
#     creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
#                                 on_delete=models.CASCADE)
#     ts_code = models.CharField(
#         _('股票代码'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
#     b_max_increase = models.FloatField(
#         _('+最大涨幅'), blank=True, null=True)
#     b_max_increase_date = models.DateField(
#         _('+最大涨幅日期'), blank=True, null=True)
#     b_max_drop = models.FloatField(
#         _('+最大跌幅'), blank=True, null=True)
#     b_max_drop_date = models.DateField(
#         _('+最大跌幅日期'), blank=True, null=True)
#     b_mean_increase = models.FloatField(
#         _('+平均涨幅'), blank=True, null=True)
#     b_mean_drop = models.FloatField(
#         _('+平均跌幅'), blank=True, null=True)
#     s_max_increase = models.FloatField(
#         _('-最大涨幅'), blank=True, null=True)
#     s_max_increase_date = models.DateField(
#         _('-最大涨幅日期'), blank=True, null=True)
#     s_max_drop = models.FloatField(
#         _('-最大跌幅'), blank=True, null=True)
#     s_max_drop_date = models.DateField(
#         _('-最大跌幅日期'), blank=True, null=True)

class TradeStrategyStat(BaseModel):
    PERIOD_CHOICE = {
        ('mm', _('月线')),
        ('wk', _('周线')),
        ('dd', _('日线')),
        ('60', _('60分钟')),
        ('30', _('30分钟')),
        ('15', _('15分钟')),
    }
    applied_period = models.CharField(
        _('应用周期'), choices=PERIOD_CHOICE, max_length=2, blank=True, null=False, default='60')
    name = models.CharField(_('策略名'), max_length=30)
    parent_strategy = models.ForeignKey(
        'self', verbose_name=_('父级策略'), blank=True, null=True, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
                                on_delete=models.CASCADE)
    count = models.IntegerField(
        _('引用数量'), blank=False, null=False, default=0)
    success_count = models.IntegerField(
        _('成功次数'), blank=False, null=False, default=0)
    fail_count = models.IntegerField(
        _('失败次数'), blank=False, null=False, default=0)
    success_rate = models.IntegerField(
        _('成功率'), blank=False, null=False, default=0)

    class Meta:
        ordering = ['name']
        verbose_name = _('交易策略统计')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_strategy_tree(self):
        """
        递归获得策略目录的父级
        :return:
        """
        strategies = []

        def parse(strategy):
            strategies.append(strategy)
            if strategy.parent_strategy:
                parse(strategy.parent_strategy)

        parse(self)
        return strategies
