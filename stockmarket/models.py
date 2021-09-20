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
        _('股票名称'), max_length=50, blank=False, null=False)  # name e.g. 平安银行
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False, )  # symbol, e.g. 000001
    # is_valid = models.BooleanField(
    #     _('是否退市'), blank=False, null=False, default=False)

    # new fields
    exchange = models.CharField(
        _('交易所代码'), choices=EXCHANGE_CHOICES, max_length=10, blank=True, null=True)
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, unique=True)  # e.g. 000001.SZ
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
    dailybasic_date = models.DateField(
        _('基本面下载日期'), blank=True, null=True)

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


class CompanyBasic(BaseModel):
    company =  models.ForeignKey(StockNameCodeMap,blank=True, null=True, on_delete=models.SET_NULL)

    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False, unique=True)  # symbol, e.g. 000001
    exchange = models.CharField(
        _('交易所代码'), max_length=10, blank=True, null=True)
    index_category = models.CharField(
        _('板块'), max_length=10, blank=True, null=True)
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, unique=True)  # e.g. 000001.SZ
    chairman = models.CharField(_('法人代表'), max_length=50,
                                blank=True, null=True)
    manager = models.CharField(
        _('总经理'), max_length=50, blank=True, null=True)
    secretary = models.CharField(
        _('董秘'), max_length=50, blank=True, null=True)
    reg_capital = models.FloatField(_('注册资本'),
                                    blank=True, null=True)
    setup_date = models.DateField(
        _('注册日期'), blank=True, null=True)
    province = models.CharField(
        _('所在省'), max_length=50, blank=True, null=True)
    city = models.CharField(
        _('城市'), max_length=50, blank=True, null=True)
    introduction = models.CharField(
        _('介绍'), max_length=5000, blank=True, null=True)
    website = models.CharField(
        _('主页'), max_length=128, blank=True, null=True)
    email = models.CharField(
        _('邮件'), max_length=128, blank=True, null=True)
    office = models.CharField(
        _('办公地址'), max_length=100, blank=True, null=True)
    employees = models.IntegerField(
        _('员工数'), blank=True, null=True)  # name e.g. 平安银行
    main_business = models.CharField(
        _('主营业务'), max_length=5000, blank=True, null=True)  # name e.g. 平安银行
    business_scope = models.CharField(
        _('经营范围'), max_length=5000, blank=True, null=True)  # name e.g. 平安银行

    def __str__(self):
        return self.stock_name

    # def save(self, *args, **kwargs):
    #     self.stock_code = self.stock_code + '.' + self.market
    #     super.save(*args, **kwargs)

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('公司基本信息')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class IndexDailyBasic(BaseModel):
    company =  models.ForeignKey(StockNameCodeMap, blank=True, null=True, on_delete=models.SET_NULL)

    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, )  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日期'), blank=True, null=True)
    turnover_rate = models.FloatField(
        _('换手率'), max_length=50, blank=True, null=True)
    turnover_rate_f = models.FloatField(
        _('换手率(自由流通)'), max_length=50, blank=True, null=True)
    pe = models.FloatField(
        _('市盈率'), blank=True, null=True)
    pe_ttm = models.FloatField(
        _('市盈率TTM'), blank=True, null=True)
    pb = models.FloatField(
            _('市净率'), blank=True, null=True)
    total_share = models.FloatField(
        _('总股本'), blank=True, null=True)
    float_share = models.FloatField(
        _('流通股本'), blank=True, null=True)
    free_share = models.FloatField(
        _('自由流通股本'), blank=True, null=True)
    total_mv = models.FloatField(
        _('总市值'), blank=True, null=True)  # name e.g. 平安银行
    float_mv = models.FloatField(
        _('流通市值'), blank=True, null=True)  # name e.g. 平安银行

    def __str__(self):
        return self.ts_code

    # def save(self, *args, **kwargs):
    #     self.stock_code = self.stock_code + '.' + self.market
    #     super.save(*args, **kwargs)

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('指数每日基本')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class CompanyDailyBasic(BaseModel):
    company =  models.ForeignKey(StockNameCodeMap, blank=True, null=True, on_delete=models.SET_NULL)

    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, db_index=True)  # e.g. 000001.SZ
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False,)  # symbol, e.g. 000001
    trade_date = models.DateField(
        _('交易日期'), blank=True, null=True)
    close = models.FloatField(_('收盘价'),
                              blank=True, null=True)
    turnover_rate = models.FloatField(
        _('换手率'), max_length=50, blank=True, null=True)
    turnover_rate_f = models.FloatField(
        _('换手率(自由流通)'), max_length=50, blank=True, null=True)
    volume_ratio = models.FloatField(_('量比'),
                                     blank=True, null=True)
    pe = models.FloatField(
        _('市盈率'), blank=True, null=True)
    pe_ttm = models.FloatField(
        _('市盈率TTM'), blank=True, null=True)
    pb = models.FloatField(
        _('市净率'), blank=True, null=True)
    ps = models.FloatField(
        _('市销率'), blank=True, null=True)
    ps_ttm = models.FloatField(
        _('市销率TTM'), blank=True, null=True)
    dv_ratio = models.FloatField(
        _('股息'), blank=True, null=True)
    dv_ttm = models.FloatField(
        _('股息率TTM'), blank=True, null=True)
    total_share = models.FloatField(
        _('总股本'), blank=True, null=True)
    float_share = models.FloatField(
        _('流通股本'), blank=True, null=True)
    free_share = models.FloatField(
        _('自由流通股本'), blank=True, null=True)
    total_mv = models.FloatField(
        _('总市值'), blank=True, null=True)  # name e.g. 平安银行
    circ_mv = models.FloatField(
        _('流通市值'), blank=True, null=True)  # name e.g. 平安银行

    def __str__(self):
        return self.ts_code

    # def save(self, *args, **kwargs):
    #     self.stock_code = self.stock_code + '.' + self.market
    #     super.save(*args, **kwargs)

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('公司每日基本')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
        unique_together = ('ts_code', 'trade_date',)


class CompanyManagers(BaseModel):
    company =  models.ForeignKey(StockNameCodeMap, blank=True, null=True, on_delete=models.SET_NULL)

    # stock_code = models.CharField(
    #     _('股票代码'), max_length=50, blank=False, null=False)  # symbol, e.g. 000001
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False,)  # e.g. 000001.SZ
    announce_date = models.DateField(_('公告日期'), blank=True, null=True)
    name = models.CharField(
        _('姓名'), max_length=50, blank=True, null=True)
    gender = models.CharField(
        _('性别'), max_length=10, blank=True, null=True)
    level = models.CharField(_('岗位类别'), max_length=50,
                             blank=True, null=True)
    title = models.CharField(
        _('岗位'), max_length=50, blank=True, null=True)
    edu = models.CharField(
        _('学历'), max_length=10, blank=True, null=True)
    national = models.CharField(
        _('国籍'), max_length=50, blank=True, null=True)
    birthday = models.CharField(
        _('出生年月'), max_length=10, blank=True, null=True)
    begin_date = models.CharField(
        _('上任日期'), max_length=10, blank=True, null=True)
    end_date = models.CharField(
        _('离任日期'), max_length=10, blank=True, null=True)
    resume = models.CharField(
        _('简历'), max_length=500, blank=True, null=True)

    def __str__(self):
        return self.stock_name

    # def save(self, *args, **kwargs):
    #     self.stock_code = self.stock_code + '.' + self.market
    #     super.save(*args, **kwargs)

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('公司管理层')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class ManagerRewards(BaseModel):
    company =  models.ForeignKey(StockNameCodeMap, blank=True, null=True, on_delete=models.SET_NULL)

    # stock_code = models.CharField(
    #     _('股票代码'), max_length=50, blank=False, null=False,)  # symbol, e.g. 000001
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False)  # e.g. 000001.SZ
    announce_date = models.DateField(
        _('公告日期'), blank=True, null=True)
    end_date = models.DateField(
        _('截至日期'), blank=True, null=True)
    name = models.CharField(
        _('姓名'), max_length=50, blank=True, null=True)
    title = models.CharField(
        _('职务'), max_length=50, blank=True, null=True)
    reward = models.FloatField(
        _('报酬'), blank=True, null=True)
    hold_value = models.FloatField(
        _('持股数'), blank=True, null=True)

    def __str__(self):
        return self.stock_name

    # def save(self, *args, **kwargs):
    #     self.stock_code = self.stock_code + '.' + self.market
    #     super.save(*args, **kwargs)

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('管理层薪酬')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
