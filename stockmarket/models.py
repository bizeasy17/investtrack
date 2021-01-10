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

class StockNameCodeMap(BaseModel):
    STOCK_MARKET_CHOICES = (
        ('ZB', _('主板')),
        ('ZXB', _('中小板')),
        ('CYB', _('创业板')),
        ('KCB', _('科创板')),

    )

    EXCHANGE_CHOICES = (
        ('SSE', _('上交所')),
        ('SZSE', _('深交所')),
    )

    ASSET_CHOICES = (
        ('I', _('INDEX')),
        ('E', _('STOCK')),
    )

    LIST_STATUS_CHOICES = (
        ('L', _('上市')),
        ('D', _('退市')),
        ('P', _('暂停上市')),
    )

    HS_CHOICES = (
        ('N', _('否')),
        ('H', _('沪股通')),
        ('S', _('深股通')),
    )

    market = models.CharField(
        _('市场类型'), choices=STOCK_MARKET_CHOICES, max_length=50, blank=True, null=True)
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=False, null=False, unique=True)  # name e.g. 平安银行
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False, unique=True)  # symbol, e.g. 000001
    # is_valid = models.BooleanField(
    #     _('是否退市'), blank=False, null=False, default=False)

    # new fields
    exchange = models.CharField(
        _('交易所代码'), choices=EXCHANGE_CHOICES, max_length=10, blank=True, null=True)
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False)  # e.g. 000001.SZ
    area = models.CharField(_('所在地域'), max_length=50,
                            blank=True, null=True)
    industry = models.CharField(
        _('所属行业'), max_length=50, blank=True, null=True)
    fullname = models.CharField(
        _('股票全称'), max_length=100, blank=True, null=True)
    en_name = models.CharField(_('英文全称'), max_length=100,
                               blank=True, null=True)
    list_status = models.CharField(
        _('上市状态'), choices=LIST_STATUS_CHOICES, max_length=1, blank=True, null=True)
    list_date = models.DateField(
        _('上市日期'), blank=True, null=True)
    delist_date = models.DateField(
        _('退市日期'), blank=True, null=True)
    is_hs = models.CharField(
        _('是否沪深港通标的'), choices=HS_CHOICES, max_length=10, blank=True, null=True)
    last_update_date = models.DateField(
        _('上次更新日期'), blank=True, null=True)
    last_analyze_date = models.DateField(
        _('上次分析日期'), blank=True, null=True)
    asset = models.CharField(
        _('股票/指数'), choices=ASSET_CHOICES, max_length=1, blank=True, null=True, default='E')
    stock_name_pinyin = models.CharField(
        _('股票名称拼音'), max_length=50, blank=True, null=True)  # name e.g. 平安银行
    # is_hist_downloaded = models.BooleanField(
    #     _('交易历史已下载？'), blank=False, null=False, default=False)
    # is_marked_jiuzhuan = models.BooleanField(
    #     _('是否标注九转'), blank=False, null=False, default=False)
    # is_marked_dingdi = models.BooleanField(
    #     _('是否标注顶底'), blank=False, null=False, default=False)
    # is_marked_wm = models.BooleanField(
    #     _('是否标注Wd底/M顶？'), blank=True, null=True)
    # is_marked_tupo = models.BooleanField(
    #     _('是否标注突破？'), blank=True, null=True)
    # is_marked_junxian = models.BooleanField(
    #     _('是否标注均线买卖点？'), blank=True, null=True)
    # is_hist_downloaded = models.BooleanField(
    #     _('交易历史已下载？'), blank=False, null=False, default=False)
    # is_hist_updated = models.BooleanField(
    #     _('交易历史已更新？'), blank=False, null=False, default=False)
    # hist_update_date = models.DateField(
    #     _('更新日期？'), blank=True, null=True)
    
    def __str__(self):
        return self.stock_name

    # def save(self, *args, **kwargs):
    #     self.stock_code = self.stock_code + '.' + self.market
    #     super.save(*args, **kwargs)

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('股票代码表')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
