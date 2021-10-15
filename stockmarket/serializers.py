import numpy as np
from analysis.models import IndustryBasicQuantileStat, StockHistoryDaily
from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, routers, serializers, status, viewsets

from .models import CompanyDailyBasic, StockNameCodeMap

BOARD_LIST = {
    'SHZB': '上海主板',
    'SZZB': '深圳主板',
    'ZXB': '中小板',
    'CYB': '创业板',
    'KCB': '科创板',
}

# Serializers define the API representation.


class Industry(models.Model):
    industry = models.CharField(
        _('行业'), max_length=50, blank=False, null=False, )
    stock_count = models.IntegerField(_('股票数'), blank=False, null=False, )
    snap_date = models.DateField(
        _('统计日期'), blank=False, null=False)  # symbol, e.g. 20200505
    pe_10pct = models.FloatField(_('PE低位'), blank=False, null=False, )
    pe_50pct = models.FloatField(_('PE中位'), blank=False, null=False, )
    pe_90pct = models.FloatField(_('PE高位'), blank=False, null=False, )
    pb_10pct = models.FloatField(_('PB低位'), blank=False, null=False, )
    pb_50pct = models.FloatField(_('PB中位'), blank=False, null=False, )
    pb_90pct = models.FloatField(_('PB高位'), blank=False, null=False, )
    ps_10pct = models.FloatField(_('PS低位'), blank=False, null=False, )
    ps_50pct = models.FloatField(_('PS中位'), blank=False, null=False, )
    ps_90pct = models.FloatField(_('PS高位'), blank=False, null=False, )
    

    class Meta:
        ordering = ['industry']
        verbose_name = _('行业')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.industry


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
    # circ_mv = models.FloatField(_('PS中位'), blank=False, null=False, )
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


class CompanyDailyBasicSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'trade_date': instance['trade_date'],
            'turnover_rate': instance['turnover_rate'] if not np.isnan(instance['turnover_rate']) else 0,
            'volume_ratio': instance['volume_ratio'] if not np.isnan(instance['volume_ratio']) else 0,
            'pe': instance['pe'] if instance['pe'] is not None and not np.isnan(instance['pe']) else 0,
            'pe_ttm': instance['pe_ttm'] if instance['pe_ttm'] and not np.isnan(instance['pe_ttm']) is not None else 0,
            'pb': instance['pb'] if not np.isnan(instance['pb']) else 0,
            'ps': instance['ps'] if not np.isnan(instance['ps']) else 0,
            'ps_ttm': instance['ps_ttm'] if not np.isnan(instance['ps_ttm']) else 0,
        }

    class Meta:
        model = CompanyDailyBasic
        fields = ['trade_date', 'turnover_rate',
                  'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm']


class CompanyDailyBasicExtSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'ts_code': instance.ts_code,
            'stock_name': instance.stock_name,
            'industry': instance.industry,
            'close': instance.close,
            'chg_pct': instance.chg_pct if not np.isnan(instance.chg_pct) else 0,
            'jiuzhuan_b': instance.jiuzhuan_b if instance.jiuzhuan_b is not None else 0,
            'jiuzhuan_s': instance.jiuzhuan_s if instance.jiuzhuan_s is not None else 0,
            'trade_date': instance.trade_date,
            # 'turnover_rate': instance.turnover_rate if not np.isnan(instance.turnover_rate) else 0,
            # 'volume_ratio': instance.volume_ratio if not np.isnan(instance.volume_ratio) else 0,
            'pe': instance['pe'] if instance['pe'] is not None else 0,
            'pe_ttm': instance['pe_ttm'] if instance['pe_ttm'] is not None else 0,
            'pb': instance.pb if not np.isnan(instance.pb) else 0,
            'ps': instance.ps if not np.isnan(instance.ps) else 0,
            'ps_ttm': instance.ps_ttm if not np.isnan(instance.ps_ttm) else 0,
        }

    class Meta:
        model = CompanyDailyBasicExt
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
