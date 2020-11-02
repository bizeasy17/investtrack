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


class BaseModel1(models.Model):
    id = models.AutoField(primary_key=True)
    created_date = models.DateField(_('创建日期'), default=now)
    last_mod_date = models.DateField(_('最后更新日期'), default=now)

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


class MarkCriticalPointTask(models.Model):
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
    # hist_downloaded = models.BooleanField(
    #     _('交易已下载？'),  blank=False, null=False, default=False)
    # hist_download_dt = models.DateTimeField(
    #     _('下载时间？'),  blank=True, null=True, default=now)
    # hist_update_dt = models.DateTimeField(
    #     _('下载更新时间？'),  blank=True, null=True, default=now)
    # critical_point_marked = models.BooleanField(
    #     _('临界点已标记？'),  blank=False, null=False, default=False)
    # cp_marked_dt = models.DateTimeField(
    #     _('临界点标记时间？'),  blank=True, null=True)
    # cp_update_dt = models.DateTimeField(
    #     _('临界点更新时间？'),  blank=True, null=True)
    # low_high_pct_marked = models.BooleanField(
    #     _('高低点涨幅已标记？'),  blank=False, null=False, default=False)
    # lhpct_mark_dt = models.DateTimeField(
    #     _('高低点标记时间？'),  blank=True, null=True)
    # lhpct_update_dt = models.DateTimeField(
    #     _('高低点更新时间？'),  blank=True, null=True)
    # exp_pct_marked = models.BooleanField(
    #     _('预期涨幅已标记？'),  blank=False, null=False, default=False)
    # exppct_mark_dt = models.DateTimeField(
    #     _('预期涨幅标记时间？'),  blank=True, null=True)
    # exppct_mark_update_dt = models.DateTimeField(
    #     _('预期涨幅更新时间？'),  blank=True, null=True)

    def __str__(self):
        return self.ts_code


class StrategyTestLowHigh(models.Model):
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
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(_('创建时间'), default=now)
    ts_code = models.CharField(
        _('TS代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日'), blank=False, null=False)  # symbol, e.g. 20200505
    test_period = models.IntegerField(
        _('测试周期长度'), blank=True, null=False, default=10)
    stage_low_date = models.DateField(
        _('低点日期'), blank=True, null=True)
    stage_low_pct = models.FloatField(
        _('低点/买点%?'), blank=True, null=True)
    stage_high_date = models.DateField(
        _('高点日期'), blank=True, null=True)
    stage_high_pct = models.FloatField(
        _('高点/买点%?'), blank=True, null=True)
    # test_strategy = models.ForeignKey(TradeStrategy, verbose_name=_('测试策略'), blank=False, null=False,
    #                                   on_delete=models.CASCADE)
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True)

    def __str__(self):
        return self.ts_code

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('交易策略日线测试')
        verbose_name_plural = verbose_name


class BStrategyOnPctTest(BaseModel):
    # test_strategy = models.ForeignKey(TradeStrategy, verbose_name=_('测试策略'), blank=False, null=False,
    #                                   on_delete=models.CASCADE)
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True, db_index=True)

    ts_code = models.CharField(
        _('股票代码'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
    b_10_pct_min = models.FloatField(
        _('+10%最小周期'), blank=True, null=True, default=-1)
    b_10_pct_max = models.FloatField(
        _('+10%最大周期'), blank=True, null=True, default=-1)
    b_10_pct_mean = models.FloatField(
        _('+10%平均周期'), blank=True, null=True, default=-1)
    b_20_pct_min = models.FloatField(
        _('+20%最小周期'), blank=True, null=True, default=-1)
    b_20_pct_max = models.FloatField(
        _('+20%最大周期'), blank=True, null=True, default=-1)
    b_20_pct_mean = models.FloatField(
        _('+20%平均周期'), blank=True, null=True, default=-1)
    b_30_pct_min = models.FloatField(
        _('+30%最小周期'), blank=True, null=True, default=-1)
    b_30_pct_max = models.FloatField(
        _('+30%最大周期'), blank=True, null=True, default=-1)
    b_30_pct_mean = models.FloatField(
        _('+30%平均周期'), blank=True, null=True, default=-1)
    b_50_pct_min = models.FloatField(
        _('+50%最小周期'), blank=True, null=True, default=-1)
    b_50_pct_max = models.FloatField(
        _('+50%最大周期'), blank=True, null=True, default=-1)
    b_50_pct_mean = models.FloatField(
        _('+50%平均周期'), blank=True, null=True, default=-1)
    b_80_pct_min = models.FloatField(
        _('+80%最小周期'), blank=True, null=True, default=-1)
    b_80_pct_max = models.FloatField(
        _('+80%最大周期'), blank=True, null=True, default=-1)
    b_80_pct_mean = models.FloatField(
        _('+80%平均周期'), blank=True, null=True, default=-1)
    b_100_pct_min = models.FloatField(
        _('+100%最小周期'), blank=True, null=True, default=-1)
    b_100_pct_max = models.FloatField(
        _('+100%最大周期'), blank=True, null=True, default=-1)
    b_100_pct_mean = models.FloatField(
        _('+100%平均周期'), blank=True, null=True, default=-1)
    b_130_pct_min = models.FloatField(
        _('+130%最小周期'), blank=True, null=True, default=-1)
    b_130_pct_max = models.FloatField(
        _('+13%最大周期'), blank=True, null=True, default=-1)
    b_130_pct_mean = models.FloatField(
        _('+130%平均周期'), blank=True, null=True, default=-1)
    test_period = models.CharField(
        _('测试周期'), max_length=5, blank=False, null=False, default='D')

    def __str__(self):
        return self.ts_code

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('达到固定涨幅周期')
        verbose_name_plural = verbose_name


class BStrategyOnFixedPctTest(BaseModel):
    # test_strategy = models.ForeignKey(TradeStrategy, verbose_name=_('测试策略'), blank=False, null=False,
    #                                   on_delete=models.CASCADE)
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True, db_index=True)

    ts_code = models.CharField(
        _('股票代码'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日'), blank=False, null=False)  # symbol, e.g. 20200505
    # new fields
    # open = models.FloatField(
    #     _('开盘价'), blank=True, null=True)
    # high = models.FloatField(
    #     _('最高价'), blank=True, null=True)
    # low = models.FloatField(
    #     _('最低价'), blank=True, null=True)
    # pre_close = models.FloatField(
    #     _('前日收盘价'), blank=True, null=True)
    # close = models.FloatField(_('收盘价'), blank=True, null=True)
    # change = models.FloatField(
    #     _('价格变化'), blank=True, null=True)
    # pct_chg = models.FloatField(
    #     _('涨幅%'), blank=True, null=True)
    # vol = models.FloatField(
    #     _('交易量'), blank=True, null=True)
    # amount = models.FloatField(
    #     _('金额'), blank=True, null=True)
    pct10_period = models.FloatField(
        _('+10%最小周期'), blank=True, null=True, default=-1)
    pct20_period = models.FloatField(
        _('+20%最小周期'), blank=True, null=True, default=-1)
    pct30_period = models.FloatField(
        _('+30%最小周期'), blank=True, null=True, default=-1)
    pct50_period = models.FloatField(
        _('+50%最小周期'), blank=True, null=True, default=-1)
    pct80_period = models.FloatField(
        _('+80%最小周期'), blank=True, null=True, default=-1)
    pct100_period = models.FloatField(
        _('+100%最小周期'), blank=True, null=True, default=-1)
    pct130_period = models.FloatField(
        _('+130%最小周期'), blank=True, null=True, default=-1)
    test_freq = models.CharField(
        _('测试周期'), max_length=5, blank=False, null=False, default='D')

    def __str__(self):
        return self.ts_code

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('达到固定涨幅周期')
        verbose_name_plural = verbose_name


class StrategyUpDownTestQuantiles(BaseModel):
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True, db_index=True)
    test_type = models.CharField(
        _('测试类型'), max_length=25, blank=True, null=True)
    ts_code = models.CharField(
        _('股票代码'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
    stock_name = models.CharField(
        _('股票名称'), max_length=15, blank=True, null=True)  # e.g. 000001.SZ
    qt_10pct = models.FloatField(
        _('10%分位数'), blank=True, null=True,)
    qt_25pct = models.FloatField(
        _('25%分位数'), blank=True, null=True,)
    qt_50pct = models.FloatField(
        _('50%分位数'), blank=True, null=True,)
    qt_75pct = models.FloatField(
        _('75%分位数'), blank=True, null=True,)
    qt_90pct = models.FloatField(
        _('90%分位数'), blank=True, null=True,)
    mean_val = models.FloatField(
        _('平均数'), blank=True, null=True,)
    min_val = models.FloatField(
        _('最小值'), blank=True, null=True,)
    max_val = models.FloatField(
        _('最大值'), blank=True, null=True,)
    test_period = models.IntegerField(
        _('测试周期'), blank=False, null=False)
    # ranking = models.IntegerField(
    #     _('排名'), blank=True, null=True, db_index=True)
    test_freq = models.CharField(
        _('K线周期'), max_length=5, blank=False, null=False, default='D')

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('涨跌四分位统计')
        verbose_name_plural = verbose_name


class StrategyTargetPctTestQuantiles(BaseModel):
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True, db_index=True)
    ts_code = models.CharField(
        _('股票代码'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
    stock_name = models.CharField(
        _('股票名称'), max_length=15, blank=True, null=True)  # e.g. 000001.SZ
    qt_10pct = models.FloatField(
        _('10%分位数'), blank=True, null=True,)
    qt_25pct = models.FloatField(
        _('25%分位数'), blank=True, null=True,)
    qt_50pct = models.FloatField(
        _('50%分位数'), blank=True, null=True,)
    qt_75pct = models.FloatField(
        _('75%分位数'), blank=True, null=True,)
    qt_90pct = models.FloatField(
        _('90%分位数'), blank=True, null=True,)
    mean_val = models.FloatField(
        _('平均数'), blank=True, null=True,)
    min_val = models.FloatField(
        _('最小值'), blank=True, null=True,)
    max_val = models.FloatField(
        _('最大值'), blank=True, null=True,)
    target_pct = models.CharField(
        _('目标涨幅'), max_length=25, blank=False, null=False, )
    # ranking = models.IntegerField(
    #     _('排名'), blank=True, null=True, db_index=True)
    test_freq = models.CharField(
        _('K线周期'), max_length=5, blank=False, null=False, default='D')

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('目标涨幅四分位统计')
        verbose_name_plural = verbose_name


class StrategyUpDownTestRanking(BaseModel):
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True, db_index=True)
    test_type = models.CharField(
        _('测试类型'), max_length=25, blank=True, null=True)
    ts_code = models.CharField(
        _('股票代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    stock_name = models.CharField(
        _('股票名称'), max_length=15, blank=True, null=True)  # e.g. 000001.SZ
    qt_pct = models.CharField(
        _('分位数'), max_length=15, blank=False, null=False,)
    qt_pct_val = models.FloatField(
        _('四分位值'), blank=False, null=False,)
    test_period = models.IntegerField(
        _('测试周期'), blank=False, null=False)
    ranking = models.IntegerField(
        _('排名'), blank=True, null=True)
    test_freq = models.CharField(
        _('K线周期'), max_length=5, blank=False, null=False, default='D')

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('涨跌四分位统计')
        verbose_name_plural = verbose_name


class StrategyTargetPctTestRanking(BaseModel):
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True, db_index=True)
    ts_code = models.CharField(
        _('股票代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    stock_name = models.CharField(
        _('股票名称'), max_length=15, blank=True, null=True)  # e.g. 000001.SZ
    qt_pct = models.CharField(
        _('分位数'), max_length=15, blank=False, null=False,)
    qt_pct_val = models.FloatField(
        _('四分位值'), blank=False, null=False,)
    target_pct = models.CharField(
        _('目标涨幅'), max_length=25, blank=False, null=False)
    ranking = models.IntegerField(
        _('排名'), blank=True, null=True)
    test_freq = models.CharField(
        _('K线周期'), max_length=5, blank=False, null=False, default='D')

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('涨跌四分位统计')
        verbose_name_plural = verbose_name


class StrategyOnDownPctTest(BaseModel):
    # test_strategy = models.ForeignKey(TradeStrategy, verbose_name=_('测试策略'), blank=False, null=False,
    #                                   on_delete=models.CASCADE)
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True, db_index=True)

    ts_code = models.CharField(
        _('股票代码'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
    down_10pct_min = models.FloatField(
        _('-10%最小周期'), blank=True, null=True)
    down_10pct_max = models.FloatField(
        _('-10%最大周期'), blank=True, null=True)
    down_10pct_mean = models.FloatField(
        _('-10%平均周期'), blank=True, null=True)
    down_20pct_min = models.FloatField(
        _('-20%最小周期'), blank=True, null=True)
    down_20pct_max = models.FloatField(
        _('-20%最大周期'), blank=True, null=True)
    down_20pct_mean = models.FloatField(
        _('-20%平均周期'), blank=True, null=True)
    down_30pct_min = models.FloatField(
        _('-30%最小周期'), blank=True, null=True)
    down_30pct_max = models.FloatField(
        _('-30%最大周期'), blank=True, null=True)
    down_30pct_mean = models.FloatField(
        _('-30%平均周期'), blank=True, null=True)
    down_50pct_min = models.FloatField(
        _('-50%最小周期'), blank=True, null=True)
    down_50pct_max = models.FloatField(
        _('-50%最大周期'), blank=True, null=True)
    down_50pct_mean = models.FloatField(
        _('-50%平均周期'), blank=True, null=True)
    down_80pct_min = models.FloatField(
        _('-80%最小周期'), blank=True, null=True)
    down_80pct_max = models.FloatField(
        _('-80%最大周期'), blank=True, null=True)
    down_80pct_mean = models.FloatField(
        _('-80%平均周期'), blank=True, null=True)
    test_period = models.CharField(
        _('测试周期'), max_length=5, blank=False, null=False, default='D')

    def __str__(self):
        return self.ts_code

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('跌幅天数统计')
        verbose_name_plural = verbose_name


class StrategyOnFixedDownPctTest(BaseModel):
    # test_strategy = models.ForeignKey(TradeStrategy, verbose_name=_('测试策略'), blank=False, null=False,
    #                                   on_delete=models.CASCADE)
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True, db_index=True)

    ts_code = models.CharField(
        _('股票代码'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日'), blank=False, null=False)  # symbol, e.g. 20200505
    pct10_period = models.FloatField(
        _('-10%最小周期'), blank=True, null=True)
    pct20_period = models.FloatField(
        _('-20%最小周期'), blank=True, null=True)
    pct30_period = models.FloatField(
        _('-30%最小周期'), blank=True, null=True)
    pct50_period = models.FloatField(
        _('-50%最小周期'), blank=True, null=True)
    pct80_period = models.FloatField(
        _('-80%最小周期'), blank=True, null=True)
    test_freq = models.CharField(
        _('测试周期'), max_length=5, blank=False, null=False, default='D')

    def __str__(self):
        return self.ts_code

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('跌幅天数')
        verbose_name_plural = verbose_name


class FocusAreaDuration(BaseModel):
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
    vol = models.FloatField(
        _('交易量'), blank=True, null=True)
    amount = models.FloatField(
        _('金额'), blank=True, null=True)
    duration = models.BooleanField(
        _('周期长度'), blank=True, null=True, default=False)
    jiuzhuan_count = models.FloatField(
        _('九转点'), blank=True, null=True, default=False)
    freq = models.CharField(
        _('分析周期'), max_length=5, blank=False, null=False, default='D')
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=True, null=True, db_index=True)

    def __str__(self):
        return self.ts_code

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('关注区周期长度')
        verbose_name_plural = verbose_name


class TradeStrategyStat(BaseModel):
    PERIOD_CHOICE = {
        ('M', _('月线')),
        ('W', _('周线')),
        ('D', _('日线')),
        ('60', _('60分钟')),
        ('30', _('30分钟')),
        ('15', _('15分钟')),
    }
    applied_period = models.CharField(
        _('应用周期'), choices=PERIOD_CHOICE, max_length=2, blank=True, null=True, default='60')
    name = models.CharField(_('策略名'), max_length=30)
    category = models.CharField(
        _('策略分类'), blank=True, null=True, max_length=25)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
                                on_delete=models.CASCADE)
    count = models.IntegerField(
        _('引用数量'), blank=False, null=False, default=0)
    success_count = models.IntegerField(
        _('成功次数'), blank=False, null=False, default=0)
    fail_count = models.IntegerField(
        _('失败次数'), blank=False, null=False, default=0)
    success_rate = models.FloatField(
        _('成功率'), blank=False, null=False, default=0)
    code = models.CharField(
        _('策略代码'), max_length=25, blank=False, null=False, default='buy')
    hist_analyzed = models.BooleanField(
        _('历史数据已分析？'), blank=False, null=False, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = _('交易策略统计')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PickedStocksMeetStrategy(BaseModel):
    done_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('操作者'), blank=True, null=True,
                                on_delete=models.SET_NULL)
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=False, null=False, db_index=True)
    ts_code = models.CharField(
        _('股票代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    stock_name = models.CharField(
        _('股票名称'), max_length=15, blank=False, null=False)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日'), blank=False, null=False)  # symbol, e.g. 20200505
    test_freq = models.CharField(
        _('K线周期'), max_length=5, blank=False, null=False, default='D')

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('选股结果')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ts_code
