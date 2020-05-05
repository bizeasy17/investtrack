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
        _('TS代码'), max_length=50, blank=True, null=False)  # e.g. 000001.SZ
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False)  # symbol, e.g. 000001
    trade_date = models.CharField(
        _('交易日'), max_length=6, blank=False, null=False)  # symbol, e.g. 20200505
    # new fields
    open = models.FloatField(
        _('开盘价'), blank=True, null=True)
    high = models.FloatField(
        _('开盘价'), blank=True, null=True)
    pre_close = models.FloatField(
        _('前一日收盘价'), blank=True, null=True)
    close = models.FloatField(_('收盘价'), blank=True, null=True)
    change = models.FloatField(
        _('与前日价格变化'), max_length=50, blank=True, null=True)
    pct_chg = models.FloatField(
        _('与前日价格变化%'), max_length=50, blank=True, null=True)
    vol = models.FloatField(
        _('交易量'), max_length=50, blank=True, null=True)
    amount = models.FloatField(
        _('金额'), max_length=50, blank=True, null=True)
    chg4 = models.FloatField(
        _('与4日前变化'), max_length=50, blank=True, null=True)
    jiuzhuan_count = models.FloatField(
        _('九转序列'), max_length=50, blank=True, null=True, default=-1)

    def __str__(self):
        return self.stock_code

    # def save(self, *args, **kwargs):
    #     self.stock_code = self.stock_code + '.' + self.market
    #     super.save(*args, **kwargs)

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('股票代码表')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
