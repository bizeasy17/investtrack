import numpy as np
from analysis.models import IndustryBasicQuantileStat, StockHistoryDaily, StockHistoryIndicators
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, routers, serializers, status, viewsets

from .models import BaseModel, CompanyDailyBasic, CompanyTop10FloatHoldersStat, IndexDailyBasic, Province, StockNameCodeMap, Industry, City

BOARD_LIST = {
    'SHZB': '上海主板',
    'SZZB': '深圳主板',
    'ZXB': '中小板',
    'CYB': '创业板',
    'KCB': '科创板',
}

# Serializers define the API representation.


# class Industry(models.Model):
#     industry = models.CharField(
#         _('行业'), max_length=50, blank=False, null=False, )
#     stock_count = models.IntegerField(_('股票数'), blank=False, null=False, )
#     snap_date = models.DateField(
#         _('统计日期'), blank=False, null=False)  # symbol, e.g. 20200505
#     pe_10pct = models.FloatField(_('PE低位'), blank=False, null=False, )
#     pe_50pct = models.FloatField(_('PE中位'), blank=False, null=False, )
#     pe_90pct = models.FloatField(_('PE高位'), blank=False, null=False, )
#     pb_10pct = models.FloatField(_('PB低位'), blank=False, null=False, )
#     pb_50pct = models.FloatField(_('PB中位'), blank=False, null=False, )
#     pb_90pct = models.FloatField(_('PB高位'), blank=False, null=False, )
#     ps_10pct = models.FloatField(_('PS低位'), blank=False, null=False, )
#     ps_50pct = models.FloatField(_('PS中位'), blank=False, null=False, )
#     ps_90pct = models.FloatField(_('PS高位'), blank=False, null=False, )


#     class Meta:
#         ordering = ['industry']
#         verbose_name = _('行业')
#         verbose_name_plural = verbose_name

#     def __str__(self):
#         return self.industry


class Equity(models.Model):
    date = models.DateField(
        _('日期'), blank=False, null=False, )
    equity = models.FloatField(_('资产净值'), blank=False, null=True, )
    drawdownpct = models.FloatField(_('最大资金回撤率'), blank=False, null=True, )
    drawdownduration = models.IntegerField(_('最大回撤周期'), blank=False, null=True, )

    class Meta:
        ordering = ['date']
        verbose_name = _('资产净值')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ts_code


class StockHistoryOHLC(BaseModel):
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
    close = models.FloatField(_('收盘价'), blank=True, null=True)
    pct_chg = models.FloatField(
        _('价格变化%'), blank=True, null=True)
    vol = models.FloatField(
        _('交易量'), blank=True, null=True)
    amount = models.FloatField(
        _('金额'), blank=True, null=True)
    equity = models.FloatField(
        _('资产净值'), blank=True, null=True, default=1.0)

class OHLCSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'd': instance.trade_date,
            'o': instance.open,
            'h': instance.high,
            'l': instance.low,
            'c': instance.close,
            'v': instance.vol,
            'e': instance.equity,
        }

    class Meta:
        model = StockHistoryOHLC

class RSI(BaseModel):
    ts_code = models.CharField(
        _('TS代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日'), max_length=6, blank=False, null=False)  # symbol, e.g. 20200505
    # new fields
    rsi_1 = models.FloatField(
        _('RSI_1'), blank=True, null=True)
    rsi_2 = models.FloatField(
        _('RSI_2'), blank=True, null=True)
    rsi_3 = models.FloatField(
        _('RSI_3'), blank=True, null=True)


class RSISerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'rsi_1': instance.rsi_1,
            'rsi_2': instance.rsi_2,
            'rsi_3': instance.rsi_3,
        }

    class Meta:
        model = RSI

class KDJ(BaseModel):
    ts_code = models.CharField(
        _('TS代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日'), max_length=6, blank=False, null=False)  # symbol, e.g. 20200505
    # new fields
    k = models.FloatField(
        _('K'), blank=True, null=True)
    d = models.FloatField(
        _('D'), blank=True, null=True)
    j = models.FloatField(
        _('J'), blank=True, null=True)


class KDJSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'k': instance.k,
            'd': instance.d,
            'j': instance.j,
        }

    class Meta:
        model = KDJ

class MACD(BaseModel):
    ts_code = models.CharField(
        _('TS代码'), max_length=15, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日'), max_length=6, blank=False, null=False)  # symbol, e.g. 20200505
    # new fields
    diff = models.FloatField(
        _('diff'), blank=True, null=True)
    dea = models.FloatField(
        _('dea'), blank=True, null=True)
    bar = models.FloatField(
        _('bar'), blank=True, null=True)

class MACDSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'diff': instance.diff,
            'dea': instance.dea,
            'bar': instance.bar,
        }

    class Meta:
        model = MACD


class EquitySerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'dt': instance.date,
            'eq': round(instance.equity,2),
            # 'ddp': instance.drawdownpct,
            # 'ddd': instance.drawdownduration,
        }

    class Meta:
        model = Equity

class TradesSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'size': instance.Size,
            'entrybar': instance.Equity,
            'exitbar': instance.DrawdownPct,
            'entryprice': instance.DrawdownDuration,
            'exitprice': instance.DrawdownDuration,
            'pnl': instance.DrawdownDuration,
            'returnpct': instance.DrawdownDuration,
            'entrytime': instance.DrawdownDuration,
            'exittime': instance.DrawdownDuration,
            'duration': instance.DrawdownDuration,
        }

    # class Meta:
    #     model = Trades


class CompanyDailyBasicExt(CompanyDailyBasic):
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=False, null=False, )
    # close = models.FloatField(_('收盘价'), blank=False, null=False, )
    chg_pct = models.FloatField(_('涨跌幅'), blank=False, null=False, )
    vol = models.FloatField(_('成交量'), blank=False, null=False, )
    amount = models.FloatField(_('成交额'), blank=False, null=False, )
    # pe = models.FloatField(_('PE'), blank=False, null=False, )
    # pe_ttm = models.FloatField(_('动态PE'), blank=False, null=False, )
    # pb = models.FloatField(_('PB'), blank=False, null=False, )
    # ps = models.FloatField(_('PS'), blank=False, null=False, )
    # ps_ttm = models.FloatField(_('动态PS'), blank=False, null=False, )
    # total_mv = models.FloatField(_('总市值'), blank=False, null=False, )
    float_hold_pct = models.FloatField(_('流通股持仓%'), blank=True, null=True, )
    jiuzhuan_b = models.IntegerField(_('九转买'), blank=False, null=False, )
    jiuzhuan_s = models.IntegerField(_('九转卖'), blank=False, null=False, )
    industry = models.CharField(
        _('所属行业'), max_length=50, blank=False, null=False, )

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('股票基本面')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ts_code


class IndustrySerializer(serializers.ModelSerializer):
    # industry = serializers.CharField(max_length=50)
    # stock_count = serializers.IntegerField()
    # pe_10pct = serializers.FloatField()
    # pe_50pct = serializers.FloatField()
    # pe_90pct = serializers.FloatField()
    # pb_10pct = serializers.FloatField()
    # pb_50pct = serializers.FloatField()
    # pb_90pct = serializers.FloatField()
    # ps_10pct = serializers.FloatField()
    # ps_50pct = serializers.FloatField()
    # ps_90pct = serializers.FloatField()

    def to_representation(self, instance):
        return {
            'industry': instance.industry,
            'stock_count': instance.stock_count,
            # 'snap_date': instance.snap_date,
            'pe_low': instance.pe_10pct if not np.isnan(instance.pe_10pct) else 0,
            'pe_med': instance.pe_50pct if not np.isnan(instance.pe_50pct) else 0,
            'pe_high': instance.pe_90pct if not np.isnan(instance.pe_90pct) else 0,
            'pb_low': instance.pb_10pct if not np.isnan(instance.pb_10pct) else 0,
            'pb_med': instance.pb_50pct if not np.isnan(instance.pb_50pct) else 0,
            'pb_high': instance.pb_90pct if not np.isnan(instance.pb_90pct) else 0,
            'ps_low': instance.ps_10pct if not np.isnan(instance.ps_10pct) else 0,
            'ps_med': instance.ps_50pct if not np.isnan(instance.ps_50pct) else 0,
            'ps_high': instance.ps_90pct if not np.isnan(instance.ps_90pct) else 0,
        }

    class Meta:
        model = Industry
        fields = ['industry']


class CompanySerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'ts_code': instance.ts_code,
            'stock_code': instance.stock_code,
            'stock_name': instance.stock_name,
            'industry': instance.industry,
            'area': instance.area,
            'list_date': instance.list_date,
            'market': BOARD_LIST[instance.market],
        }

    class Meta:
        model = StockNameCodeMap
        # fields = ['ts_code', 'stock_code', 'stock_name',
        #           'market', 'industry', 'area', 'list_date']


# Serializers define the API representation.
class StockCloseHistorySerializer(serializers.ModelSerializer):

    # def to_representation(self, instance):
    #     quantile = []
    #     qt_10 = []
    #     qt_90 = []
    #     qt_50 = []

    #     return {
    #         'close': instance.close,
    #         'ts_code': instance.ts_code,
    #         'trade_date': instance.trade_date,
    #         'pct_chg': round(instance.pct_chg, 2)
    #     }

    class Meta:
        model = StockHistoryDaily
        fields = ['close', 'trade_date']

# Serializers define the API representation.
class StockIndicRSVSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'vol': instance['vol'],
            'trade_date': instance['trade_date'],
            'amount': instance['amount'],
            'rsv': instance['rsv'] if not np.isnan(instance['rsv']) else 0,
            'eema_b': instance['eema_b'] if not np.isnan(instance['eema_b']) else 0,
            'eema_s': instance['eema_s'] if not np.isnan(instance['eema_s']) else 0,
            'var1': instance['var1'],
            'var2': instance['var2'] if not np.isnan(instance['var2']) else 0,
            'var3': instance['var3'] if not np.isnan(instance['var3'])  else 0
        }

    class Meta:
        model = StockHistoryIndicators
        fields = ['vol', 'trade_date', 'amount', 'rsv', 'eema_b', 'eema_s', 'var1', 'var2', 'var3']


class CompanyDailyBasicSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'trade_date': instance['trade_date'],
            'turnover_rate': instance['turnover_rate'] if instance['turnover_rate'] is not None and not np.isnan(instance['turnover_rate']) else 0,
            'volume_ratio': instance['volume_ratio'] if instance['volume_ratio'] is not None and  not np.isnan(instance['volume_ratio']) else 0,
            'pe': instance['pe'] if instance['pe'] is not None and not np.isnan(instance['pe']) else 0,
            'pe_ttm': instance['pe_ttm'] if instance['pe_ttm'] is not None and not np.isnan(instance['pe_ttm']) else 0,
            'pb': instance['pb'] if instance['pb'] is not None and  not np.isnan(instance['pb']) else 0,
            'ps': instance['ps'] if instance['ps'] is not None and  not np.isnan(instance['ps']) else 0,
            'ps_ttm': instance['ps_ttm'] if instance['ps_ttm'] is not None and  not np.isnan(instance['ps_ttm']) else 0,
        }

    class Meta:
        model = CompanyDailyBasic
        fields = ['trade_date', 'turnover_rate',
                  'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm']


class IndexDailyBasicSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'trade_date': instance['trade_date'],
            'turnover_rate': instance['turnover_rate'] if not np.isnan(instance['turnover_rate']) else 0,
            # 'volume_ratio': instance['volume_ratio'] if not np.isnan(instance['volume_ratio']) else 0,
            'pe': instance['pe'] if instance['pe'] is not None and not np.isnan(instance['pe']) else 0,
            'pe_ttm': instance['pe_ttm'] if instance['pe_ttm'] is not None and not np.isnan(instance['pe_ttm']) else 0,
            'pb': instance['pb'] if not np.isnan(instance['pb']) else 0,
            # 'ps': instance['ps'] if not np.isnan(instance['ps']) else 0,
            # 'ps_ttm': instance['ps_ttm'] if not np.isnan(instance['ps_ttm']) else 0,
        }

    class Meta:
        model = IndexDailyBasic
        fields = ['trade_date', 'turnover_rate','pe', 'pe_ttm', 'pb',]


class CompanyDailyBasicExtSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'ts_code': instance.ts_code,
            'stock_name': instance.stock_name,
            'industry': instance.industry,
            'close': instance.close,
            'chg_pct': instance.chg_pct if instance.chg_pct is not None else 0,
            'jiuzhuan_b': instance.jiuzhuan_b if instance.jiuzhuan_b is not None else 0,
            'jiuzhuan_s': instance.jiuzhuan_s if instance.jiuzhuan_s is not None else 0,
            'trade_date': instance.trade_date,
            # 'turnover_rate': instance.turnover_rate if not np.isnan(instance.turnover_rate) else 0,
            # 'volume_ratio': instance.volume_ratio if not np.isnan(instance.volume_ratio) else 0,
            'pe': instance.pe if (instance.pe is not None and not np.isnan(instance.pe)) else 0,
            'pe_ttm': instance.pe_ttm if (instance.pe_ttm is not None and not np.isnan(instance.pe_ttm)) else 0,
            'pb': instance.pb if (instance.pb is not None and not np.isnan(instance.pb)) else 0,
            'ps': instance.ps if (instance.ps is not None and not np.isnan(instance.ps)) else 0,
            'ps_ttm': instance.ps_ttm if (instance.ps_ttm is not None and not np.isnan(instance.ps_ttm)) else 0,
            'total_mv': instance.total_mv if instance.total_mv is not None else 0,
            'top10_hold_pct': instance.float_hold_pct if instance.float_hold_pct is not None else 0,

        }

    class Meta:
        model = CompanyDailyBasicExt
        # fields = ['trade_date', 'turnover_rate',
        #           'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm']


class CompanyTop10HoldersStatSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'ts_code': instance.ts_code,
            # 'stock_name': instance.stock_name,
            'hold_pct': instance.hold_pct * 100,
            'close': instance.close,
            'trade_date': instance.end_date,
            'hold_amount': instance.hold_amount,
            'float_amount': instance.float_amount,
            'pe': instance.pe if (instance.pe is not None and not np.isnan(instance.pe)) else 0,
            'pe_ttm': instance.pe_ttm if (instance.pe_ttm is not None and not np.isnan(instance.pe_ttm)) else 0,
            'pb': instance.pb if (instance.pb is not None and not np.isnan(instance.pb)) else 0,
            'ps': instance.ps if (instance.ps is not None and not np.isnan(instance.ps)) else 0,
            'ps_ttm': instance.ps_ttm if (instance.ps_ttm is not None and not np.isnan(instance.ps_ttm)) else 0,
        }

    class Meta:
        model = CompanyTop10FloatHoldersStat
        # fields = ['trade_date', 'turnover_rate',
        #           'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm']


class IndustryBasicQuantileSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'industry': instance['industry'],
            'basic_type': instance['basic_type'],
            'trade_date': instance['snap_date'],
            'quantile': instance['quantile'],
            'stock_count': instance['stk_quantity'],
            'quantile_val': instance['quantile_val'] if not np.isnan(instance['quantile_val']) else 0,
        }

    class Meta:
        model = IndustryBasicQuantileStat
        # fields = ['trade_date', 'turnover_rate',
        #           'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm']


class ProvinceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Province
        fields = ['name']


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ['name']
