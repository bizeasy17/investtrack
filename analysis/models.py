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
from stockmarket.models import StockNameCodeMap, CompanyBasic
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


class AnalysisEventLog(BaseModel):
    analysis_code = models.CharField(
        _('测试策略'), max_length=25, blank=True, null=True)
    event_type = models.CharField(
        _('日志类型'), max_length=50, blank=False, null=False)  # e.g. 000001.SZ
    # 用于新下载的交易记录的标记start
    exec_date = models.DateField(
        _('执行日期'),  blank=False, null=False)
    status = models.IntegerField(
        _('状态'),  blank=False, null=False, default=0)  # 0 - in progress, 1 - done, 2 - with exception,
    freq = models.CharField(
        _('k线频率'), max_length=5, blank=False, null=False, default='D')
    exception_tscode = models.CharField(
        _('日志类型'), max_length=30000, blank=True, null=True)  # e.g. 000001.SZ

    def __str__(self):
        return self.event_type


class StockIndexHistory(BaseModel):
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
        _('九转序列B'),  blank=True, null=True)
    jiuzhuan_count_s = models.FloatField(
        _('九转序列S'),  blank=True, null=True)
    ma25 = models.FloatField(
        _('MA25'),  blank=True, null=True)
    ma25_slope = models.FloatField(
        _('MA25斜率'),  blank=True, null=True)
    ma60 = models.FloatField(
        _('MA60'),  blank=True, null=True)
    ma60_slope = models.FloatField(
        _('MA60斜率'),  blank=True, null=True)
    ma200 = models.FloatField(
        _('MA200'),  blank=True, null=True)
    ma200_slope = models.FloatField(
        _('MA200斜率'),  blank=True, null=True)
    slope = models.FloatField(
        _('斜率'), blank=True, null=True)
    dingdi_count = models.IntegerField(
        _('顶底序列'),  blank=True, null=True)
    dibu_b = models.IntegerField(
        _('底部B?'),  blank=True, null=True)
    di_min = models.IntegerField(
        _('底部最低价?'),  blank=True, null=True)
    w_di = models.IntegerField(
        _('W底部?'),  blank=True, null=True)
    dingbu_s = models.IntegerField(
        _('顶部S?'),  blank=True, null=True)
    ding_max = models.IntegerField(
        _('顶部最高价?'),  blank=True, null=True)
    m_ding = models.IntegerField(
        _('M顶部?'),  blank=True, null=True)
    is_dingdi_end = models.IntegerField(
        _('顶底结束点?'),  blank=True, null=True)
    tupo_b = models.IntegerField(
        _('突破压力位B?'),  blank=True, null=True)
    diepo_s = models.IntegerField(
        _('跌破支撑位S?'),  blank=True, null=True)
    # MA25
    ma25_zhicheng = models.IntegerField(
        _('MA25均线支撑'),  blank=True, null=True)
    ma25_tupo = models.IntegerField(
        _('MA25均线突破'),  blank=True, null=True)
    ma25_diepo = models.IntegerField(
        _('MA25均线跌破'),  blank=True, null=True)
    ma25_yali = models.IntegerField(
        _('MA25压力'),  blank=True, null=True)
    # MA60
    ma60_zhicheng = models.IntegerField(
        _('MA60均线支撑B?'),  blank=True, null=True)
    ma60_tupo = models.IntegerField(
        _('MA60均线突破B?'),  blank=True, null=True)
    ma60_diepo = models.IntegerField(
        _('MA60均线跌破S?'),  blank=True, null=True)
    ma60_yali = models.IntegerField(
        _('MA60压力S?'),  blank=True, null=True)
    # MA200
    ma200_zhicheng = models.IntegerField(
        _('MA200均线支撑B?'),  blank=True, null=True)
    ma200_tupo = models.IntegerField(
        _('MA200均线突破B?'),  blank=True, null=True)
    ma200_diepo = models.IntegerField(
        _('MA200均线跌破S?'),  blank=True, null=True)
    ma200_yali = models.IntegerField(
        _('MA200压力S?'),  blank=True, null=True)

    freq = models.CharField(
        _('周期'), max_length=5, blank=False, null=False, default='D')  # e.g. 000001.SZ

    def __str__(self):
        return self.ts_code

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('股票代码表')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class StockStrategyTestLog(BaseModel):
    '''
    ts_code	str	股票代码
    trade_date	str	交易日期
    策略测试状态
    1. 获得股票交易历史
    2. 应用策略分析所有历史交易记录
    3. 标记临界点（买，卖，加仓，减仓，平仓）
    4. 测试策略
    5. 记录策略测试结果
        - 方法1：给定测试周期，标记周期内最高最低点的涨幅%
        - 方法2：无输入值，测试达到涨幅10%。。。，130%需要的最大，最小和平均天数
    '''
    EVENT_TYPE = {
        ('DOWNLOAD', _('下载历史交易')),
        ('UPD_DOWNLOAD', _('更新下载历史交易')),
        ('MARK_CP', _('标记临界点')),
        ('UPD_CP', _('更新临界点')),
        ('PERIOD_TEST', _('标记高低点涨幅')),
        ('PERIOD_UPD', _('更新高低点涨幅')),
        ('EXP_PCT_TEST', _('标记预期涨幅')),
        ('EXP_PCT_UPD', _('更新预期涨幅')),
    }

    ts_code = models.CharField(
        _('TS代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    analysis_code = models.CharField(
        _('测试策略'), max_length=25, blank=True, null=True)
    event_type = models.CharField(
        _('日志类型'), choices=EVENT_TYPE, max_length=50, blank=False, null=False)  # e.g. 000001.SZ
    # 用于新下载的交易记录的标记start
    start_date = models.DateField(
        _('开始日期'),  blank=True, null=True)
    end_date = models.DateField(
        _('结束日期'),  blank=True, null=True)
    # 用于新下载的交易记录的标记end
    is_done = models.BooleanField(
        _('已完成'),  blank=False, null=False, default=False)
    freq = models.CharField(
        _('测试频率'), max_length=5, blank=False, null=False, default='D')

    def __str__(self):
        return self.ts_code

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
        _('TS代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
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
        _('九转序列B'),  blank=True, null=True)
    jiuzhuan_count_s = models.FloatField(
        _('九转序列S'),  blank=True, null=True)
    ma25 = models.FloatField(
        _('MA25'),  blank=True, null=True)
    ma25_slope = models.FloatField(
        _('MA25斜率'),  blank=True, null=True)
    ma60 = models.FloatField(
        _('MA60'),  blank=True, null=True)
    ma60_slope = models.FloatField(
        _('MA60斜率'),  blank=True, null=True)
    ma200 = models.FloatField(
        _('MA200'),  blank=True, null=True)
    ma200_slope = models.FloatField(
        _('MA200斜率'),  blank=True, null=True)
    slope = models.FloatField(
        _('斜率'), blank=True, null=True)
    dingdi_count = models.IntegerField(
        _('顶底序列'),  blank=True, null=True)
    dibu_b = models.IntegerField(
        _('底部B?'),  blank=True, null=True)
    di_min = models.IntegerField(
        _('底部最低价?'),  blank=True, null=True)
    w_di = models.IntegerField(
        _('W底部?'),  blank=True, null=True)
    dingbu_s = models.IntegerField(
        _('顶部S?'),  blank=True, null=True)
    ding_max = models.IntegerField(
        _('顶部最高价?'),  blank=True, null=True)
    m_ding = models.IntegerField(
        _('M顶部?'),  blank=True, null=True)
    is_dingdi_end = models.IntegerField(
        _('顶底结束点?'),  blank=True, null=True)
    tupo_b = models.IntegerField(
        _('突破压力位B?'),  blank=True, null=True)
    diepo_s = models.IntegerField(
        _('跌破支撑位S?'),  blank=True, null=True)
    # ma25_zhicheng_b = models.IntegerField(
    #     _('MA25均线支撑B?'),  blank=True, null=True)
    ma25_zhicheng = models.IntegerField(
        _('MA25均线支撑'),  blank=True, null=True)
    # ma25_tupo_b = models.IntegerField(
    #     _('MA25均线突破B?'),  blank=True, null=True)
    ma25_tupo = models.IntegerField(
        _('MA25均线突破'),  blank=True, null=True)
    # ma25_diepo_s = models.IntegerField(
    #     _('MA25均线跌破S?'),  blank=True, null=True)
    ma25_diepo = models.IntegerField(
        _('MA25均线跌破'),  blank=True, null=True)
    # ma25_yali_s = models.IntegerField(
    #     _('MA25压力S?'),  blank=True, null=True)
    ma25_yali = models.IntegerField(
        _('MA25压力'),  blank=True, null=True)
    # MA60
    ma60_zhicheng = models.IntegerField(
        _('MA60均线支撑B?'),  blank=True, null=True)
    ma60_tupo = models.IntegerField(
        _('MA60均线突破B?'),  blank=True, null=True)
    ma60_diepo = models.IntegerField(
        _('MA60均线跌破S?'),  blank=True, null=True)
    ma60_yali = models.IntegerField(
        _('MA60压力S?'),  blank=True, null=True)
    # MA200
    ma200_zhicheng = models.IntegerField(
        _('MA200均线支撑B?'),  blank=True, null=True)
    ma200_tupo = models.IntegerField(
        _('MA200均线突破B?'),  blank=True, null=True)
    ma200_diepo = models.IntegerField(
        _('MA200均线跌破S?'),  blank=True, null=True)
    ma200_yali = models.IntegerField(
        _('MA200压力S?'),  blank=True, null=True)

    freq = models.CharField(
        _('周期'), max_length=5, blank=False, null=False, default='D')  # e.g. 000001.SZ

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
