from enum import unique
import random
import string
from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import date, datetime, timedelta
import decimal
from django import db

import tushare as ts
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Sum
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
# from analysis.utils import last_date_seq
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


class Province(BaseModel):
    name = models.CharField(
        _('省份'), max_length=50, blank=False, null=False, unique=True, db_index=True, )  # name e.g. 平安银行
    country = models.CharField(
        _('国家'), max_length=50, blank=True, null=False, default='中国')
    province_pinyin = models.CharField(
        _('省份拼音'), max_length=50, blank=True, null=True,)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'country')
        verbose_name = _('省份')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class City(BaseModel):
    name = models.CharField(
        _('城市'), max_length=50, blank=False, null=False, unique=True, db_index=True)  # name e.g. 平安银行
    province = models.ForeignKey(
        Province, related_name='city_province', blank=True, null=True, on_delete=models.SET_NULL)
    city_pinyin = models.CharField(
        _('城市拼音'), max_length=50, blank=True, null=True,)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'province')
        verbose_name = _('城市')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Industry(BaseModel):
    industry = models.CharField(
        _('行业'), max_length=50, blank=False, null=False, unique=True, db_index=True)  # name e.g. 平安银行
    industry_pinyin = models.CharField(
        _('行业名称拼音'), max_length=50, blank=True, null=True)  # name e.g. 平安银行
    stock_count = models.IntegerField(_('股票数'), blank=True, null=True, )
    snap_date = models.DateField(
        _('统计日期'), blank=True, null=True)  # symbol, e.g. 20200505
    pe_10pct = models.FloatField(_('PE低位'), blank=True, null=True, )
    pe_50pct = models.FloatField(_('PE中位'), blank=True, null=True, )
    pe_90pct = models.FloatField(_('PE高位'), blank=True, null=True, )
    pb_10pct = models.FloatField(_('PB低位'), blank=True, null=True, )
    pb_50pct = models.FloatField(_('PB中位'), blank=True, null=True, )
    pb_90pct = models.FloatField(_('PB高位'), blank=True, null=True, )
    ps_10pct = models.FloatField(_('PS低位'), blank=True, null=True, )
    ps_50pct = models.FloatField(_('PS中位'), blank=True, null=True, )
    ps_90pct = models.FloatField(_('PS高位'), blank=True, null=True, )

    class Meta:
        ordering = ['industry']
        # unique_together = ('industry')
        verbose_name = _('行业')
        verbose_name_plural = verbose_name

    def get_latest_daily_basic(self):
        # date_seq = AnalysisDateSeq.objects.filter().order_by('-analysis_date').first()
        return self.industry_basic

    def __str__(self):
        return self.industry


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
    province = models.ForeignKey(Province, related_name='province',
                                 blank=True, null=True, on_delete=models.SET_NULL)
    industry = models.CharField(
        _('所属行业'), max_length=50, blank=True, null=True)
    ind = models.ForeignKey(Industry, related_name='company_ind',
                            blank=True, null=True, on_delete=models.SET_NULL)
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
    top10_holder_date = models.DateField(
        _('流通股持仓下载日期'), blank=True, null=True)
    fin_indicator_date = models.DateField(
        _('财务指标下载日期'), blank=True, null=True)
    balance_sheet_date = models.DateField(
        _('财务指标下载日期'), blank=True, null=True)
    popdb2fin_date = models.DateField(
        _('推送每日指标日期'), blank=True, null=True)
    # 0416/2022
    pop2eema_date = models.DateField(
        _('推送加强ema指标日期(短线窥探)'), blank=True, null=True)

    def __str__(self):
        return self.stock_name

    def get_latest_history(self):
        return self.close_history.first()

    def get_latest_daily_basic(self):
        return self.daily_basic.first()

    def get_daily_basic_by_date(self, trade_date):
        db = self.get_latest_daily_basic()
        if db is None:
            return None
        else:
            db = self.daily_basic.filter(trade_date__lte=trade_date).first()
            if db is not None:
                return db
            else:
                return None

    def get_company_basic(self):
        return self.company_basic.first()

    # def get_company_basic_by_province(self, province):
    #     return self.company_basic.filter()

    def get_company_top10_holders(self):
        return self.top10_holder.order_by('-end_date')[:10]

    def get_company_top10_holders_pct(self):
        return self.top10_holder_pct

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('股票基本信息')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class CompanyBasic(BaseModel):
    company = models.ForeignKey(StockNameCodeMap, related_name='company_basic',
                                blank=True, null=True, on_delete=models.SET_NULL)

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
    shengfen = models.ForeignKey(Province, related_name='company_province',
                                 blank=True, null=True, on_delete=models.SET_NULL)
    city = models.CharField(
        _('城市'), max_length=50, blank=True, null=True)
    chengshi = models.ForeignKey(City, related_name='company_city',
                                 blank=True, null=True, on_delete=models.SET_NULL)
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
    company = models.ForeignKey(StockNameCodeMap, related_name='index_basic',
                                blank=True, null=True, on_delete=models.SET_NULL)

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


class CompanyBasicFilter(BaseModel):
    company = models.OneToOneField(StockNameCodeMap, related_name='basic_filter',
                                   blank=True, null=True, on_delete=models.SET_NULL)

    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=False, null=False, db_index=True)  # e.g. 000001.SZ
    trade_date = models.DateField(
        _('交易日期'), blank=True, null=True)
    turnover_rate = models.IntegerField(
        _('换手率'), blank=True, null=True)
    turnover_rate_f = models.IntegerField(
        _('换手率(自由流通)'), blank=True, null=True)
    volume_ratio = models.IntegerField(_('量比'),
                                       blank=True, null=True)
    pe = models.IntegerField(
        _('市盈率'), blank=True, null=True)
    pe_ttm = models.IntegerField(
        _('市盈率TTM'), blank=True, null=True)
    pb = models.IntegerField(
        _('市净率'), blank=True, null=True)
    ps = models.IntegerField(
        _('市销率'), blank=True, null=True)
    ps_ttm = models.IntegerField(
        _('市销率TTM'), blank=True, null=True)
    dv_ratio = models.IntegerField(
        _('股息'), blank=True, null=True)
    dv_ttm = models.IntegerField(
        _('股息率TTM'), blank=True, null=True)
    total_share = models.IntegerField(
        _('总股本'), blank=True, null=True)
    float_share = models.IntegerField(
        _('流通股本'), blank=True, null=True)
    free_share = models.IntegerField(
        _('自由流通股本'), blank=True, null=True)
    total_mv = models.IntegerField(
        _('总市值'), blank=True, null=True)  # name e.g. 平安银行
    circ_mv = models.IntegerField(
        _('流通市值'), blank=True, null=True)  # name e.g. 平安银行

    def __str__(self):
        return self.ts_code

    # def save(self, *args, **kwargs):
    #     self.stock_code = self.stock_code + '.' + self.market
    #     super.save(*args, **kwargs)

    class Meta:
        ordering = ['-ts_code']
        verbose_name = _('公司基本面过滤器')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
        # unique_together = ('ts_code', 'trade_date',)


class CompanyDailyBasic(BaseModel):
    company = models.ForeignKey(StockNameCodeMap, related_name='daily_basic',
                                blank=True, null=True, on_delete=models.SET_NULL)

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
        ordering = ['-trade_date']
        verbose_name = _('公司每日基本面')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
        unique_together = ('ts_code', 'trade_date',)


class CompanyManagers(BaseModel):
    company = models.ForeignKey(StockNameCodeMap, related_name='manager',
                                blank=True, null=True, on_delete=models.SET_NULL)

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
        ordering = ['-announce_date']
        verbose_name = _('公司管理层')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class ManagerRewards(BaseModel):
    company = models.ForeignKey(
        StockNameCodeMap, blank=True, null=True, on_delete=models.SET_NULL)

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


class CompanyIncomeSheet(BaseModel):
    '''
    ts_code	str	Y	TS代码
    ann_date	str	Y	公告日期
    f_ann_date	str	Y	实际公告日期
    end_date	str	Y	报告期
    report_type	str	Y	报告类型 见底部表
    comp_type	str	Y	公司类型(1一般工商业2银行3保险4证券)
    end_type	str	Y	报告期类型
    basic_eps	float	Y	基本每股收益
    diluted_eps	float	Y	稀释每股收益
    total_revenue	float	Y	营业总收入
    revenue	float	Y	营业收入
    int_income	float	Y	利息收入
    prem_earned	float	Y	已赚保费
    comm_income	float	Y	手续费及佣金收入
    n_commis_income	float	Y	手续费及佣金净收入
    n_oth_income	float	Y	其他经营净收益
    n_oth_b_income	float	Y	加:其他业务净收益
    prem_income	float	Y	保险业务收入
    out_prem	float	Y	减:分出保费
    une_prem_reser	float	Y	提取未到期责任准备金
    reins_income	float	Y	其中:分保费收入
    n_sec_tb_income	float	Y	代理买卖证券业务净收入
    n_sec_uw_income	float	Y	证券承销业务净收入
    n_asset_mg_income	float	Y	受托客户资产管理业务净收入
    oth_b_income	float	Y	其他业务收入
    fv_value_chg_gain	float	Y	加:公允价值变动净收益
    invest_income	float	Y	加:投资净收益
    ass_invest_income	float	Y	其中:对联营企业和合营企业的投资收益
    forex_gain	float	Y	加:汇兑净收益
    total_cogs	float	Y	营业总成本
    oper_cost	float	Y	减:营业成本
    int_exp	float	Y	减:利息支出
    comm_exp	float	Y	减:手续费及佣金支出
    biz_tax_surchg	float	Y	减:营业税金及附加
    sell_exp	float	Y	减:销售费用
    admin_exp	float	Y	减:管理费用
    fin_exp	float	Y	减:财务费用
    assets_impair_loss	float	Y	减:资产减值损失
    prem_refund	float	Y	退保金
    compens_payout	float	Y	赔付总支出
    reser_insur_liab	float	Y	提取保险责任准备金
    div_payt	float	Y	保户红利支出
    reins_exp	float	Y	分保费用
    oper_exp	float	Y	营业支出
    compens_payout_refu	float	Y	减:摊回赔付支出
    insur_reser_refu	float	Y	减:摊回保险责任准备金
    reins_cost_refund	float	Y	减:摊回分保费用
    other_bus_cost	float	Y	其他业务成本
    operate_profit	float	Y	营业利润
    non_oper_income	float	Y	加:营业外收入
    non_oper_exp	float	Y	减:营业外支出
    nca_disploss	float	Y	其中:减:非流动资产处置净损失
    total_profit	float	Y	利润总额
    income_tax	float	Y	所得税费用
    n_income	float	Y	净利润(含少数股东损益)
    n_income_attr_p	float	Y	净利润(不含少数股东损益)
    minority_gain	float	Y	少数股东损益
    oth_compr_income	float	Y	其他综合收益
    t_compr_income	float	Y	综合收益总额
    compr_inc_attr_p	float	Y	归属于母公司(或股东)的综合收益总额
    compr_inc_attr_m_s	float	Y	归属于少数股东的综合收益总额
    ebit	float	Y	息税前利润
    ebitda	float	Y	息税折旧摊销前利润
    insurance_exp	float	Y	保险业务支出
    undist_profit	float	Y	年初未分配利润
    distable_profit	float	Y	可分配利润
    rd_exp	float	Y	研发费用
    fin_exp_int_exp	float	Y	财务费用:利息费用
    fin_exp_int_inc	float	Y	财务费用:利息收入
    transfer_surplus_rese	float	Y	盈余公积转入
    transfer_housing_imprest	float	Y	住房周转金转入
    transfer_oth	float	Y	其他转入
    adj_lossgain	float	Y	调整以前年度损益
    withdra_legal_surplus	float	Y	提取法定盈余公积
    withdra_legal_pubfund	float	Y	提取法定公益金
    withdra_biz_devfund	float	Y	提取企业发展基金
    withdra_rese_fund	float	Y	提取储备基金
    withdra_oth_ersu	float	Y	提取任意盈余公积金
    workers_welfare	float	Y	职工奖金福利
    distr_profit_shrhder	float	Y	可供股东分配的利润
    prfshare_payable_dvd	float	Y	应付优先股股利
    comshare_payable_dvd	float	Y	应付普通股股利
    capit_comstock_div	float	Y	转作股本的普通股股利
    net_after_nr_lp_correct	float	N	扣除非经常性损益后的净利润（更正前）
    credit_impa_loss	float	N	信用减值损失
    net_expo_hedging_benefits	float	N	净敞口套期收益
    oth_impair_loss_assets	float	N	其他资产减值损失
    total_opcost	float	N	营业总成本（二）
    amodcost_fin_assets	float	N	以摊余成本计量的金融资产终止确认收益
    oth_income	float	N	其他收益
    asset_disp_income	float	N	资产处置收益
    continued_net_profit	float	N	持续经营净利润
    end_net_profit	float	N	终止经营净利润
    update_flag	str	Y	更新标识
    '''
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False)  # e.g. 000001.SZ
    company = models.ForeignKey(
        StockNameCodeMap, related_name='income', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('企业营收表')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class CompanyBalanceSheet(BaseModel):
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, db_index=True)  # e.g. 000001.SZ
    announce_date = models.DateField(
        _('公告日期'), blank=True, null=True)  # ann_date	str	Y	公告日期
    f_announce_date = models.DateField(
        _('实际公告日期'), blank=True, null=True)  # ann_date	str	Y	实际公告日期
    end_date = models.DateField(
        _('报告期'), blank=True, null=True)  # end_date	str	Y	报告期
    report_type = models.CharField(
        _('报表类型'), max_length=50, blank=True, null=True)  # str	Y	报表类型
    comp_type = models.CharField(
        _('公司类型'), max_length=50, blank=True, null=True)		# str	Y	公司类型(1一般工商业2银行3保险4证券)
    end_type = models.CharField(
        _('报告期类型'), max_length=50, blank=True, null=True)		# str	Y	报告期类型
    total_share = models.FloatField(
        _('期末总股本'), blank=True, null=True)  # float	Y	期末总股本
    cap_rese = models.FloatField(
        _('资本公积金'), blank=True, null=True)  # float	Y	资本公积金
    undistr_porfit = models.FloatField(
        _('未分配利润'), blank=True, null=True)  # float	Y	未分配利润
    surplus_rese = models.FloatField(
        _('盈余公积金'), blank=True, null=True)  # float	Y	盈余公积金
    special_rese = models.FloatField(
        _('专项储备'), blank=True, null=True)  # float	Y	专项储备
    money_cap = models.FloatField(
        _('货币资金'), blank=True, null=True)  # float	Y	货币资金
    trad_asset = models.FloatField(
        _('交易性金融资产'), blank=True, null=True)  # float	Y	交易性金融资产
    notes_receiv = models.FloatField(
        _('应收票据'), blank=True, null=True)  # float	Y	应收票据
    accounts_receiv = models.FloatField(
        _('应收账款'), blank=True, null=True)  # float	Y	应收账款
    oth_receiv = models.FloatField(
        _('其他应收款'), blank=True, null=True)  # float	Y	其他应收款
    prepayment = models.FloatField(
        _('预付款项'), blank=True, null=True)  # float	Y	预付款项
    div_receiv = models.FloatField(
        _('应收股利'), blank=True, null=True)  # float	Y	应收股利
    int_receiv = models.FloatField(
        _('应收利息'), blank=True, null=True)  # float	Y	应收利息
    inventories = models.FloatField(
        _('存货'), blank=True, null=True)  # float	Y	存货
    amor_exp = models.FloatField(
        _('长期待摊费用'), blank=True, null=True)  # float	Y	长期待摊费用
    nca_within_1y = models.FloatField(
        _('一年内到期的非流动资产'), blank=True, null=True)  # float	Y	一年内到期的非流动资产
    sett_rsrv = models.FloatField(
        _('结算备付金'), blank=True, null=True)  # float	Y	结算备付金
    loanto_oth_bank_fi = models.FloatField(
        _('拆出资金'), blank=True, null=True)  # float	Y	拆出资金
    premium_receiv = models.FloatField(
        _('应收保费'), blank=True, null=True)  # float	Y	应收保费
    reinsur_receiv = models.FloatField(
        _('应收分保账款'), blank=True, null=True)  # float	Y	应收分保账款
    reinsur_res_receiv = models.FloatField(
        _('应收分保合同准备金'), blank=True, null=True)  # float	Y	应收分保合同准备金
    pur_resale_fa = models.FloatField(
        _('买入返售金融资产'), blank=True, null=True)  # float	Y	买入返售金融资产
    oth_cur_assets = models.FloatField(
        _('其他流动资产'), blank=True, null=True)  # float	Y	其他流动资产
    total_cur_assets = models.FloatField(
        _('流动资产合计'), blank=True, null=True)  # float	Y	流动资产合计
    fa_avail_for_sale = models.FloatField(
        _('可供出售金融资产'), blank=True, null=True)  # float	Y	可供出售金融资产
    htm_invest = models.FloatField(
        _('持有至到期投资'), blank=True, null=True)  # float	Y	持有至到期投资
    lt_eqt_invest = models.FloatField(
        _('长期股权投资'), blank=True, null=True)  # float	Y	长期股权投资
    invest_real_estate = models.FloatField(
        _('投资性房地产'), blank=True, null=True)  # float	Y	投资性房地产
    time_deposits = models.FloatField(
        _('定期存款'), blank=True, null=True)  # float	Y	定期存款
    oth_assets = models.FloatField(
        _('其他资产'), blank=True, null=True)  # float	Y	其他资产
    lt_rec = models.FloatField(
        _('长期应收款'), blank=True, null=True)  # float	Y	长期应收款
    fix_assets = models.FloatField(
        _('固定资产'), blank=True, null=True)  # float	Y	固定资产
    cip = models.FloatField(
        _('在建工程'), blank=True, null=True)  # float	Y	在建工程
    const_materials = models.FloatField(
        _('工程物资'), blank=True, null=True)  # float	Y	工程物资
    fixed_assets_disp = models.FloatField(
        _('固定资产清理'), blank=True, null=True)  # float	Y	固定资产清理
    produc_bio_assets = models.FloatField(
        _('生产性生物资产'), blank=True, null=True)  # float	Y	生产性生物资产
    oil_and_gas_assets = models.FloatField(
        _('油气资产'), blank=True, null=True)  # float	Y	油气资产
    intan_assets = models.FloatField(
        _('无形资产'), blank=True, null=True)  # float	Y	无形资产
    r_and_d = models.FloatField(
        _('研发支出'), blank=True, null=True)  # float	Y	研发支出
    goodwill = models.FloatField(
        _('商誉'), blank=True, null=True)  # float	Y	商誉
    lt_amor_exp = models.FloatField(
        _('长期待摊费用'), blank=True, null=True)  # float	Y	长期待摊费用
    defer_tax_assets = models.FloatField(
        _('递延所得税资产'), blank=True, null=True)  # float	Y	递延所得税资产
    decr_in_disbur = models.FloatField(
        _('发放贷款及垫款'), blank=True, null=True)  # float	Y	发放贷款及垫款
    oth_nca = models.FloatField(
        _('其他非流动资产'), blank=True, null=True)  # float	Y	其他非流动资产
    total_nca = models.FloatField(
        _('非流动资产合计'), blank=True, null=True)  # float	Y	非流动资产合计
    cash_reser_cb = models.FloatField(
        _('现金及存放中央银行款项'), blank=True, null=True)  # float	Y	现金及存放中央银行款项
    depos_in_oth_bfi = models.FloatField(
        _('存放同业和其它金融机构款项'), blank=True, null=True)  # float	Y	存放同业和其它金融机构款项
    prec_metals = models.FloatField(
        _('贵金属'), blank=True, null=True)  # float	Y	贵金属
    deriv_assets = models.FloatField(
        _('衍生金融资产'), blank=True, null=True)  # float	Y	衍生金融资产
    rr_reins_une_prem = models.FloatField(
        _('应收分保未到期责任准备金'), blank=True, null=True)  # float	Y	应收分保未到期责任准备金
    rr_reins_outstd_cla = models.FloatField(
        _('应收分保未决赔款准备金'), blank=True, null=True)  # float	Y	应收分保未决赔款准备金
    rr_reins_lins_liab = models.FloatField(
        _('应收分保寿险责任准备金'), blank=True, null=True)  # float	Y	应收分保寿险责任准备金
    rr_reins_lthins_liab = models.FloatField(
        _('应收分保长期健康险责任准备金'), blank=True, null=True)  # float	Y	应收分保长期健康险责任准备金
    refund_depos = models.FloatField(
        _('存出保证金'), blank=True, null=True)  # float	Y	存出保证金
    ph_pledge_loans = models.FloatField(
        _('保户质押贷款'), blank=True, null=True)  # float	Y	保户质押贷款
    refund_cap_depos = models.FloatField(
        _('存出资本保证金'), blank=True, null=True)  # float	Y	存出资本保证金
    indep_acct_assets = models.FloatField(
        _('独立账户资产'), blank=True, null=True)  # float	Y	独立账户资产
    client_depos = models.FloatField(
        _('客户资金存款'), blank=True, null=True)  # float	Y	其中：客户资金存款
    client_prov = models.FloatField(
        _('客户备付金'), blank=True, null=True)  # float	Y	其中：客户备付金
    transac_seat_fee = models.FloatField(
        _('交易席位费'), blank=True, null=True)  # float	Y	其中:交易席位费
    invest_as_receiv = models.FloatField(
        _('应收款项类投资'), blank=True, null=True)  # float	Y	应收款项类投资
    total_assets = models.FloatField(
        _('资产总计'), blank=True, null=True)  # float	Y	资产总计
    lt_borr = models.FloatField(
        _('长期借款'), blank=True, null=True)  # float	Y	长期借款
    st_borr = models.FloatField(
        _('短期借款'), blank=True, null=True)  # float	Y	短期借款
    cb_borr = models.FloatField(
        _('向中央银行借款'), blank=True, null=True)  # float	Y	向中央银行借款
    depos_ib_deposits = models.FloatField(
        _('吸收存款及同业存放'), blank=True, null=True)  # float	Y	吸收存款及同业存放
    loan_oth_bank = models.FloatField(
        _('拆入资金'), blank=True, null=True)  # float	Y	拆入资金
    trading_fl = models.FloatField(
        _('交易性金融负债'), blank=True, null=True)  # float	Y	交易性金融负债
    notes_payable = models.FloatField(
        _('应付票据'), blank=True, null=True)  # float	Y	应付票据
    acct_payable = models.FloatField(
        _('应付账款'), blank=True, null=True)  # float	Y	应付账款
    adv_receipts = models.FloatField(
        _('预收款项'), blank=True, null=True)  # float	Y	预收款项
    sold_for_repur_fa = models.FloatField(
        _('卖出回购金融资产款'), blank=True, null=True)  # float	Y	卖出回购金融资产款
    comm_payable = models.FloatField(
        _('应付手续费及佣金'), blank=True, null=True)  # float	Y	应付手续费及佣金
    payroll_payable = models.FloatField(
        _('应付职工薪酬'), blank=True, null=True)  # float	Y	应付职工薪酬
    taxes_payable = models.FloatField(
        _('应交税费'), blank=True, null=True)  # float	Y	应交税费
    int_payable = models.FloatField(
        _('应付利息'), blank=True, null=True)  # float	Y	应付利息
    div_payable = models.FloatField(
        _('应付股利'), blank=True, null=True)  # float	Y	应付股利
    oth_payable = models.FloatField(
        _('其他应付款'), blank=True, null=True)  # float	Y	其他应付款
    acc_exp = models.FloatField(
        _('预提费用'), blank=True, null=True)  # float	Y	预提费用
    deferred_inc = models.FloatField(
        _('递延收益'), blank=True, null=True)  # float	Y	递延收益
    st_bonds_payable = models.FloatField(
        _('应付短期债券'), blank=True, null=True)  # float	Y	应付短期债券
    payable_to_reinsurer = models.FloatField(
        _('应付分保账款'), blank=True, null=True)  # float	Y	应付分保账款
    rsrv_insur_cont = models.FloatField(
        _('保险合同准备金'), blank=True, null=True)  # float	Y	保险合同准备金
    acting_trading_sec = models.FloatField(
        _('代理买卖证券款'), blank=True, null=True)  # float	Y	代理买卖证券款
    acting_uw_sec = models.FloatField(
        _('代理承销证券款'), blank=True, null=True)  # float	Y	代理承销证券款
    non_cur_liab_due_1y = models.FloatField(
        _('一年内到期的非流动负债'), blank=True, null=True)  # float	Y	一年内到期的非流动负债
    oth_cur_liab = models.FloatField(
        _('其他流动负债'), blank=True, null=True)  # float	Y	其他流动负债
    total_cur_liab = models.FloatField(
        _('流动负债合计'), blank=True, null=True)  # float	Y	流动负债合计
    bond_payable = models.FloatField(
        _('应付债券'), blank=True, null=True)  # float	Y	应付债券
    lt_payable = models.FloatField(
        _('长期应付款'), blank=True, null=True)  # float	Y	长期应付款
    specific_payables = models.FloatField(
        _('专项应付款'), blank=True, null=True)  # float	Y	专项应付款
    estimated_liab = models.FloatField(
        _('预计负债'), blank=True, null=True)  # float	Y	预计负债
    defer_tax_liab = models.FloatField(
        _('递延所得税负债'), blank=True, null=True)  # float	Y	递延所得税负债
    defer_inc_non_cur_liab = models.FloatField(
        _('递延收益-非流动负债'), blank=True, null=True)  # float	Y	递延收益-非流动负债
    oth_ncl = models.FloatField(
        _('其他非流动负债'), blank=True, null=True)  # float	Y	其他非流动负债
    total_ncl = models.FloatField(
        _('非流动负债合计'), blank=True, null=True)  # float	Y	非流动负债合计
    depos_oth_bfi = models.FloatField(
        _('同业和其它金融机构存放款项'), blank=True, null=True)  # float	Y	同业和其它金融机构存放款项
    deriv_liab = models.FloatField(
        _('衍生金融负债'), blank=True, null=True)  # float	Y	衍生金融负债
    depos = models.FloatField(
        _('吸收存款'), blank=True, null=True)  # float	Y	吸收存款
    agency_bus_liab = models.FloatField(
        _('代理业务负债'), blank=True, null=True)  # float	Y	代理业务负债
    oth_liab = models.FloatField(
        _('其他负债'), blank=True, null=True)  # float	Y	其他负债
    prem_receiv_adva = models.FloatField(
        _('预收保费'), blank=True, null=True)  # float	Y	预收保费
    depos_received = models.FloatField(
        _('存入保证金'), blank=True, null=True)  # float	Y	存入保证金
    ph_invest = models.FloatField(
        _('保户储金及投资款'), blank=True, null=True)  # float	Y	保户储金及投资款
    reser_une_prem = models.FloatField(
        _('未到期责任准备金'), blank=True, null=True)  # float	Y	未到期责任准备金
    reser_outstd_claims = models.FloatField(
        _('未决赔款准备金'), blank=True, null=True)  # float	Y	未决赔款准备金
    reser_lins_liab = models.FloatField(
        _('寿险责任准备金'), blank=True, null=True)  # float	Y	寿险责任准备金
    reser_lthins_liab = models.FloatField(
        _('长期健康险责任准备金'), blank=True, null=True)  # float	Y	长期健康险责任准备金
    indept_acc_liab = models.FloatField(
        _('独立账户负债'), blank=True, null=True)  # float	Y	独立账户负债
    pledge_borr = models.FloatField(
        _('质押借款'), blank=True, null=True)  # float	Y	其中:质押借款
    indem_payable = models.FloatField(
        _('应付赔付款'), blank=True, null=True)  # float	Y	应付赔付款
    policy_div_payable = models.FloatField(
        _('应付保单红利'), blank=True, null=True)  # float	Y	应付保单红利
    total_liab = models.FloatField(
        _('负债合计'), blank=True, null=True)  # float	Y	负债合计
    treasury_share = models.FloatField(
        _('减:库存股'), blank=True, null=True)  # float	Y	减:库存股
    ordin_risk_reser = models.FloatField(
        _('一般风险准备'), blank=True, null=True)  # float	Y	一般风险准备
    forex_differ = models.FloatField(
        _('外币报表折算差额'), blank=True, null=True)  # float	Y	外币报表折算差额
    invest_loss_unconf = models.FloatField(
        _('未确认的投资损失'), blank=True, null=True)  # float	Y	未确认的投资损失
    minority_int = models.FloatField(
        _('少数股东权益'), blank=True, null=True)  # float	Y	少数股东权益
    total_hldr_eqy_exc_min_int = models.FloatField(
        _('股东权益合计(不含少数股东权益)'), blank=True, null=True)  # float	Y	股东权益合计(不含少数股东权益)
    total_hldr_eqy_inc_min_int = models.FloatField(
        _('股东权益合计(含少数股东权益)'), blank=True, null=True)  # float	Y	股东权益合计(含少数股东权益)
    total_liab_hldr_eqy = models.FloatField(
        _('负债及股东权益总计'), blank=True, null=True)  # float	Y	负债及股东权益总计
    lt_payroll_payable = models.FloatField(
        _('长期应付职工薪酬'), blank=True, null=True)  # float	Y	长期应付职工薪酬
    oth_comp_income = models.FloatField(
        _('其他综合收益'), blank=True, null=True)  # float	Y	其他综合收益
    oth_eqt_tools = models.FloatField(
        _('其他权益工具'), blank=True, null=True)  # float	Y	其他权益工具
    oth_eqt_tools_p_shr  = models.FloatField(
        _('其他权益工具(优先股)'), blank=True, null=True)   # float	Y	其他权益工具(优先股)
    lending_funds = models.FloatField(
        _('融出资金'), blank=True, null=True)  # float	Y	融出资金
    acc_receivable = models.FloatField(
        _('应收款项'), blank=True, null=True)  # float	Y	应收款项
    st_fin_payable = models.FloatField(
        _('应付短期融资款'), blank=True, null=True)  # float	Y	应付短期融资款
    payables = models.FloatField(
        _('应付款项'), blank=True, null=True)  # float	Y	应付款项
    hfs_assets = models.FloatField(
        _('持有待售的资产'), blank=True, null=True)  # float	Y	持有待售的资产
    hfs_sales = models.FloatField(
        _('持有待售的负债'), blank=True, null=True)  # float	Y	持有待售的负债
    cost_fin_assets = models.FloatField(
        _('以摊余成本计量的金融资产'), blank=True, null=True)  # float	Y	以摊余成本计量的金融资产
    fair_value_fin_assets = models.FloatField(
        _('公允价值计量计入的金融资产'), blank=True, null=True)  # float	Y	以公允价值计量且其变动计入其他综合收益的金融资产
    cip_total = models.FloatField(
        _('在建工程'), blank=True, null=True)  # float	Y	在建工程(合计)(元)
    oth_pay_total = models.FloatField(
        _('在建工程'), blank=True, null=True)  # float	Y	在建工程(合计)(元)
    long_pay_total = models.FloatField(
        _('长期应付款'), blank=True, null=True)  # float	Y	长期应付款(合计)(元)
    debt_invest = models.FloatField(
        _('债权投资'), blank=True, null=True)  # float	Y	债权投资(元)
    oth_debt_invest = models.FloatField(
        _('其他债权投资'), blank=True, null=True)  # float	Y	其他债权投资(元)
    oth_eq_invest = models.FloatField(
        _('其他权益工具投资'), blank=True, null=True)  # float	N	其他权益工具投资(元)
    oth_illiq_fin_assets = models.FloatField(
        _('其他非流动金融资产'), blank=True, null=True)  # float	N	其他非流动金融资产(元)
    oth_eq_ppbond = models.FloatField(
        _('其他权益工具永续债'), blank=True, null=True)  # float	N	其他权益工具:永续债(元)
    receiv_financing = models.FloatField(
        _('应收款项融资'), blank=True, null=True)  # float	N	应收款项融资
    use_right_assets = models.FloatField(
        _('使用权资产'), blank=True, null=True)  # float	N	使用权资产
    lease_liab = models.FloatField(
        _('租赁负债'), blank=True, null=True)  # float	N	租赁负债
    contract_assets = models.FloatField(
        _('合同资产'), blank=True, null=True)  # float	Y	合同资产
    contract_liab = models.FloatField(
        _('合同负债'), blank=True, null=True)  # float	Y	合同负债
    accounts_receiv_bill = models.FloatField(
        _('应收票据及应收账款'), blank=True, null=True)  # float	Y	应收票据及应收账款
    accounts_pay = models.FloatField(
        _('应付票据及应付账款'), blank=True, null=True)  # float	Y	应付票据及应付账款
    oth_rcv_total = models.FloatField(
        _('其他应收款(合计)'), blank=True, null=True)  # float	Y	其他应收款(合计)（元）
    fix_assets_total = models.FloatField(
        _('固定资产(合计)'), blank=True, null=True)  # float	Y	固定资产(合计)(元)
    update_flag = models.CharField(
        _('更新标识'), max_length=50, blank=True, null=False, )  # str	Y	更新标识
    company = models.ForeignKey(
        StockNameCodeMap, related_name='balance_sheet', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('资产负债表')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class CompanyCashflow(BaseModel):
    '''
    ts_code	str	Y	TS股票代码
    ann_date	str	Y	公告日期
    f_ann_date	str	Y	实际公告日期
    end_date	str	Y	报告期
    comp_type	str	Y	公司类型(1一般工商业2银行3保险4证券)
    report_type	str	Y	报表类型
    end_type	str	Y	报告期类型
    net_profit	float	Y	净利润
    finan_exp	float	Y	财务费用
    c_fr_sale_sg	float	Y	销售商品、提供劳务收到的现金
    recp_tax_rends	float	Y	收到的税费返还
    n_depos_incr_fi	float	Y	客户存款和同业存放款项净增加额
    n_incr_loans_cb	float	Y	向中央银行借款净增加额
    n_inc_borr_oth_fi	float	Y	向其他金融机构拆入资金净增加额
    prem_fr_orig_contr	float	Y	收到原保险合同保费取得的现金
    n_incr_insured_dep	float	Y	保户储金净增加额
    n_reinsur_prem	float	Y	收到再保业务现金净额
    n_incr_disp_tfa	float	Y	处置交易性金融资产净增加额
    ifc_cash_incr	float	Y	收取利息和手续费净增加额
    n_incr_disp_faas	float	Y	处置可供出售金融资产净增加额
    n_incr_loans_oth_bank	float	Y	拆入资金净增加额
    n_cap_incr_repur	float	Y	回购业务资金净增加额
    c_fr_oth_operate_a	float	Y	收到其他与经营活动有关的现金
    c_inf_fr_operate_a	float	Y	经营活动现金流入小计
    c_paid_goods_s	float	Y	购买商品、接受劳务支付的现金
    c_paid_to_for_empl	float	Y	支付给职工以及为职工支付的现金
    c_paid_for_taxes	float	Y	支付的各项税费
    n_incr_clt_loan_adv	float	Y	客户贷款及垫款净增加额
    n_incr_dep_cbob	float	Y	存放央行和同业款项净增加额
    c_pay_claims_orig_inco	float	Y	支付原保险合同赔付款项的现金
    pay_handling_chrg	float	Y	支付手续费的现金
    pay_comm_insur_plcy	float	Y	支付保单红利的现金
    oth_cash_pay_oper_act	float	Y	支付其他与经营活动有关的现金
    st_cash_out_act	float	Y	经营活动现金流出小计
    n_cashflow_act	float	Y	经营活动产生的现金流量净额
    oth_recp_ral_inv_act	float	Y	收到其他与投资活动有关的现金
    c_disp_withdrwl_invest	float	Y	收回投资收到的现金
    c_recp_return_invest	float	Y	取得投资收益收到的现金
    n_recp_disp_fiolta	float	Y	处置固定资产、无形资产和其他长期资产收回的现金净额
    n_recp_disp_sobu	float	Y	处置子公司及其他营业单位收到的现金净额
    stot_inflows_inv_act	float	Y	投资活动现金流入小计
    c_pay_acq_const_fiolta	float	Y	购建固定资产、无形资产和其他长期资产支付的现金
    c_paid_invest	float	Y	投资支付的现金
    n_disp_subs_oth_biz	float	Y	取得子公司及其他营业单位支付的现金净额
    oth_pay_ral_inv_act	float	Y	支付其他与投资活动有关的现金
    n_incr_pledge_loan	float	Y	质押贷款净增加额
    stot_out_inv_act	float	Y	投资活动现金流出小计
    n_cashflow_inv_act	float	Y	投资活动产生的现金流量净额
    c_recp_borrow	float	Y	取得借款收到的现金
    proc_issue_bonds	float	Y	发行债券收到的现金
    oth_cash_recp_ral_fnc_act	float	Y	收到其他与筹资活动有关的现金
    stot_cash_in_fnc_act	float	Y	筹资活动现金流入小计
    free_cashflow	float	Y	企业自由现金流量
    c_prepay_amt_borr	float	Y	偿还债务支付的现金
    c_pay_dist_dpcp_int_exp	float	Y	分配股利、利润或偿付利息支付的现金
    incl_dvd_profit_paid_sc_ms	float	Y	其中:子公司支付给少数股东的股利、利润
    oth_cashpay_ral_fnc_act	float	Y	支付其他与筹资活动有关的现金
    stot_cashout_fnc_act	float	Y	筹资活动现金流出小计
    n_cash_flows_fnc_act	float	Y	筹资活动产生的现金流量净额
    eff_fx_flu_cash	float	Y	汇率变动对现金的影响
    n_incr_cash_cash_equ	float	Y	现金及现金等价物净增加额
    c_cash_equ_beg_period	float	Y	期初现金及现金等价物余额
    c_cash_equ_end_period	float	Y	期末现金及现金等价物余额
    c_recp_cap_contrib	float	Y	吸收投资收到的现金
    incl_cash_rec_saims	float	Y	其中:子公司吸收少数股东投资收到的现金
    uncon_invest_loss	float	Y	未确认投资损失
    prov_depr_assets	float	Y	加:资产减值准备
    depr_fa_coga_dpba	float	Y	固定资产折旧、油气资产折耗、生产性生物资产折旧
    amort_intang_assets	float	Y	无形资产摊销
    lt_amort_deferred_exp	float	Y	长期待摊费用摊销
    decr_deferred_exp	float	Y	待摊费用减少
    incr_acc_exp	float	Y	预提费用增加
    loss_disp_fiolta	float	Y	处置固定、无形资产和其他长期资产的损失
    loss_scr_fa	float	Y	固定资产报废损失
    loss_fv_chg	float	Y	公允价值变动损失
    invest_loss	float	Y	投资损失
    decr_def_inc_tax_assets	float	Y	递延所得税资产减少
    incr_def_inc_tax_liab	float	Y	递延所得税负债增加
    decr_inventories	float	Y	存货的减少
    decr_oper_payable	float	Y	经营性应收项目的减少
    incr_oper_payable	float	Y	经营性应付项目的增加
    others	float	Y	其他
    im_net_cashflow_oper_act	float	Y	经营活动产生的现金流量净额(间接法)
    conv_debt_into_cap	float	Y	债务转为资本
    conv_copbonds_due_within_1y	float	Y	一年内到期的可转换公司债券
    fa_fnc_leases	float	Y	融资租入固定资产
    im_n_incr_cash_equ	float	Y	现金及现金等价物净增加额(间接法)
    net_dism_capital_add	float	Y	拆出资金净增加额
    net_cash_rece_sec	float	Y	代理买卖证券收到的现金净额(元)
    credit_impa_loss	float	Y	信用减值损失
    use_right_asset_dep	float	Y	使用权资产折旧
    oth_loss_asset	float	Y	其他资产减值损失
    end_bal_cash	float	Y	现金的期末余额
    beg_bal_cash	float	Y	减:现金的期初余额
    end_bal_cash_equ	float	Y	加:现金等价物的期末余额
    beg_bal_cash_equ	float	Y	减:现金等价物的期初余额
    update_flag	str	Y	更新标志(1最新）
    '''
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False)  # e.g. 000001.SZ
    company = models.ForeignKey(
        StockNameCodeMap, related_name='cashflow', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['ts_code']
        verbose_name = _('现金流量表')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class CompanyFinIndicators(BaseModel):

    # ts_code	str	Y	TS代码
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, db_index=True)  # e.g. 000001.SZ
    announce_date = models.DateField(
        _('公告日期'), blank=True, null=True)  # ann_date	str	Y	公告日期
    end_date = models.DateField(
        _('截至日期'), blank=True, null=True)  # end_date	str	Y	报告期
    eps = models.FloatField(
        _('基本每股收益'), blank=True, null=True)  # eps	float	Y	基本每股收益
    dt_eps = models.FloatField(
        _('稀释每股收益'), blank=True, null=True)  # float	Y	稀释每股收益
    total_revenue_ps = models.FloatField(
        _('每股营业总收入'), blank=True, null=True)  # float	Y	每股营业总收入, 
    revenue_ps = models.FloatField(
        _('每股营业收入'), blank=True, null=True)  # float	Y	每股营业收入
    capital_rese_ps = models.FloatField(
        _('每股资本公积'), blank=True, null=True)  # float	Y	每股资本公积
    surplus_rese_ps = models.FloatField(
        _('每股盈余公积'), blank=True, null=True)  # float	Y	每股盈余公积
    undist_profit_ps = models.FloatField(
        _('每股未分配利润'), blank=True, null=True)  # float	Y	每股未分配利润
    extra_item = models.FloatField(
        _('非经常性损益'), blank=True, null=True)  # float	Y	非经常性损益
    profit_dedt = models.FloatField(
        _('扣非净利润'), blank=True, null=True)  # float	Y	扣除非经常性损益后的净利润（扣非净利润）
    gross_margin = models.FloatField(
        _('毛利'), blank=True, null=True)  # float	Y	毛利
    current_ratio = models.FloatField(
        _('流动比率'), blank=True, null=True)  # float	Y	流动比率
    quick_ratio = models.FloatField(
        _('速动比率'), blank=True, null=True)  # float	Y	速动比率
    cash_ratio = models.FloatField(
        _('保守速动比率'), blank=True, null=True)  # float	Y	保守速动比率
    invturn_days = models.FloatField(
        _('存货周转天数'), blank=True, null=True)  # float	N	存货周转天数
    arturn_days = models.FloatField(
        _('应收账款周转天数'), blank=True, null=True)  # float	N	应收账款周转天数
    inv_turn = models.FloatField(
        _('存货周转率'), blank=True, null=True)  # float	N	存货周转率
    ar_turn = models.FloatField(
        _('应收账款周转率'), blank=True, null=True)  # float	Y	应收账款周转率
    ca_turn = models.FloatField(
        _('流动资产周转率'), blank=True, null=True)  # float	Y	流动资产周转率
    fa_turn = models.FloatField(
        _('固定资产周转率'), blank=True, null=True)  # float	Y	固定资产周转率
    assets_turn = models.FloatField(
        _('总资产周转率'), blank=True, null=True)  # float	Y	总资产周转率
    op_income = models.FloatField(
        _('经营活动净收益'), blank=True, null=True)  # float	Y	经营活动净收益
    valuechange_income = models.FloatField(
        _('价值变动净收益'), blank=True, null=True)  # float	N	价值变动净收益
    interst_income = models.FloatField(
        _('利息费用'), blank=True, null=True)  # float	N	利息费用
    daa = models.FloatField(
        _('折旧与摊销'), blank=True, null=True)  # float	N	折旧与摊销
    ebit = models.FloatField(
        _('息税前利润'), blank=True, null=True)  # float	Y	息税前利润
    ebitda = models.FloatField(
        _('息税折旧摊销前利润'), blank=True, null=True)  # float	Y	息税折旧摊销前利润
    fcff = models.FloatField(
        _('企业自由现金流量'), blank=True, null=True)  # float	Y	企业自由现金流量
    fcfe = models.FloatField(
        _('股权自由现金流量'), blank=True, null=True)  # float	Y	股权自由现金流量
    current_exint = models.FloatField(
        _('无息流动负债'), blank=True, null=True)  # float	Y	无息流动负债
    noncurrent_exint = models.FloatField(
        _('无息非流动负债'), blank=True, null=True)  # float	Y	无息非流动负债
    interestdebt = models.FloatField(
        _('带息债务'), blank=True, null=True)  # float	Y	带息债务
    netdebt = models.FloatField(
        _('净债务'), blank=True, null=True)  # float	Y	净债务
    tangible_asset = models.FloatField(
        _('有形资产'), blank=True, null=True)  # float	Y	有形资产
    working_capital = models.FloatField(
        _('营运资金'), blank=True, null=True)  # float	Y	营运资金
    networking_capital = models.FloatField(
        _('营运流动资本'), blank=True, null=True)  # float	Y	营运流动资本
    invest_capital = models.FloatField(
        _('全部投入资本'), blank=True, null=True)  # float	Y	全部投入资本
    retained_earnings = models.FloatField(
        _('留存收益'), blank=True, null=True)  # float	Y	留存收益
    diluted2_eps = models.FloatField(
        _('期末摊薄每股收益'), blank=True, null=True)  # float	Y	期末摊薄每股收益
    bps = models.FloatField(
        _('每股净资产'), blank=True, null=True)  # float	Y	每股净资产
    ocfps = models.FloatField(
        _('每股经营活动产生的现金流量净额'), blank=True, null=True)  # float	Y	每股经营活动产生的现金流量净额
    retainedps = models.FloatField(
        _('每股留存收益'), blank=True, null=True)  # float	Y	每股留存收益
    cfps = models.FloatField(
        _('每股现金流量净额'), blank=True, null=True)  # float	Y	每股现金流量净额
    ebit_ps = models.FloatField(
        _('每股息税前利润'), blank=True, null=True)  # float	Y	每股息税前利润
    fcff_ps = models.FloatField(
        _('每股企业自由现金流量'), blank=True, null=True)  # float	Y	每股企业自由现金流量
    fcfe_ps = models.FloatField(
        _('每股股东自由现金流量'), blank=True, null=True)  # float	Y	每股股东自由现金流量
    netprofit_margin = models.FloatField(
        _('销售净利率'), blank=True, null=True)  # float	Y	销售净利率
    grossprofit_margin = models.FloatField(
        _('销售毛利率'), blank=True, null=True)  # float	Y	销售毛利率
    cogs_of_sales = models.FloatField(
        _('销售成本率'), blank=True, null=True)  # float	Y	销售成本率
    expense_of_sales = models.FloatField(
        _('销售期间费用率'), blank=True, null=True)  # float	Y	销售期间费用率
    profit_to_gr = models.FloatField(
        _('净利润/营业总收入'), blank=True, null=True)  # float	Y	净利润/营业总收入
    saleexp_to_gr = models.FloatField(
        _('销售费用/营业总收入'), blank=True, null=True)  # float	Y	销售费用/营业总收入
    adminexp_of_gr = models.FloatField(
        _('管理费用/营业总收入'), blank=True, null=True)  # float	Y	管理费用/营业总收入
    finaexp_of_gr = models.FloatField(
        _('财务费用/营业总收入'), blank=True, null=True)  # float	Y	财务费用/营业总收入
    impai_ttm = models.FloatField(
        _('资产减值损失/营业总收入'), blank=True, null=True)  # float	Y	资产减值损失/营业总收入
    gc_of_gr = models.FloatField(
        _('营业总成本/营业总收入'), blank=True, null=True)  # float	Y	营业总成本/营业总收入
    op_of_gr = models.FloatField(
        _('营业利润/营业总收入'), blank=True, null=True)  # float	Y	营业利润/营业总收入
    ebit_of_gr = models.FloatField(
        _('息税前利润/营业总收入'), blank=True, null=True)  # float	Y	息税前利润/营业总收入
    roe = models.FloatField(
        _('净资产收益率'), blank=True, null=True)  # float 	Y	净资产收益率
    roe_waa = models.FloatField(
        _('加权平均净资产收益率'), blank=True, null=True)  # float	Y	加权平均净资产收益率
    roe_dt = models.FloatField(
        _('净资产收益率(扣除非经常损益)'), blank=True, null=True)  # float	Y	净资产收益率(扣除非经常损益)
    roa = models.FloatField(
        _('总资产报酬率'), blank=True, null=True)  # float	Y	总资产报酬率
    npta = models.FloatField(
        _('总资产净利润'), blank=True, null=True)  # float	Y	总资产净利润
    roic = models.FloatField(
        _('投入资本回报率'), blank=True, null=True)  # float	Y	投入资本回报率
    roe_yearly = models.FloatField(
        _('年化净资产收益率'), blank=True, null=True)  # float	Y	年化净资产收益率
    roa2_yearly = models.FloatField(
        _('年化总资产报酬率'), blank=True, null=True)  # float	Y	年化总资产报酬率
    roe_avg = models.FloatField(
        _('平均净资产收益率(增发条件)'), blank=True, null=True)  # float	N	平均净资产收益率(增发条件)
    opincome_of_ebt = models.FloatField(
        _('经营活动净收益/利润总额'), blank=True, null=True)  # float	N	经营活动净收益/利润总额
    investincome_of_ebt = models.FloatField(
        _('价值变动净收益/利润总额'), blank=True, null=True)  # float	N	价值变动净收益/利润总额
    n_op_profit_of_ebt = models.FloatField(
        _('营业外收支净额/利润总额'), blank=True, null=True)  # float	N	营业外收支净额/利润总额
    tax_to_ebt = models.FloatField(
        _('所得税/利润总额'), blank=True, null=True)  # float	N	所得税/利润总额
    dtprofit_to_profit = models.FloatField(
        _('扣除非经常损益后的净利润/净利润'), blank=True, null=True)  # float	N	扣除非经常损益后的净利润/净利润
    salescash_to_or = models.FloatField(
        _('销售商品提供劳务收到的现金/营业收入'), blank=True, null=True)  # float	N	销售商品提供劳务收到的现金/营业收入
    ocf_to_or = models.FloatField(
        _('经营活动产生的现金流量净额/营业收入'), blank=True, null=True)  # float	N	经营活动产生的现金流量净额/营业收入
    ocf_to_opincome = models.FloatField(
        _('经营活动产生的现金流量净额/经营活动净收益'), blank=True, null=True)  # float	N	经营活动产生的现金流量净额/经营活动净收益
    capitalized_to_da = models.FloatField(
        _('资本支出/折旧和摊销'), blank=True, null=True)  # float	N	资本支出/折旧和摊销
    debt_to_assets = models.FloatField(
        _('资产负债率'), blank=True, null=True)  # float	Y	资产负债率
    assets_to_eqt = models.FloatField(
        _('权益乘数'), blank=True, null=True)  # float	Y	权益乘数
    dp_assets_to_eqt = models.FloatField(
        _('权益乘数(杜邦分析)'), blank=True, null=True)  # float	Y	权益乘数(杜邦分析)
    ca_to_assets = models.FloatField(
        _('流动资产/总资产'), blank=True, null=True)  # float	Y	流动资产/总资产
    nca_to_assets = models.FloatField(
        _('非流动资产/总资产'), blank=True, null=True)  # float	Y	非流动资产/总资产
    tbassets_to_totalassets = models.FloatField(
        _('有形资产/总资产'), blank=True, null=True)  # float	Y	有形资产/总资产
    int_to_talcap = models.FloatField(
        _('带息债务/全部投入资本'), blank=True, null=True)  # float	Y	带息债务/全部投入资本
    eqt_to_talcapital = models.FloatField(
        _('归属于母公司的股东权益/全部投入资本'), blank=True, null=True)  # float	Y	归属于母公司的股东权益/全部投入资本
    currentdebt_to_debt = models.FloatField(
        _('流动负债/负债合计'), blank=True, null=True)  # float	Y	流动负债/负债合计
    longdeb_to_debt = models.FloatField(
        _('非流动负债/负债合计'), blank=True, null=True)  # float	Y	非流动负债/负债合计
    ocf_to_shortdebt = models.FloatField(
        _('经营活动产生的现金流量净额/流动负债'), blank=True, null=True)  # float	Y	经营活动产生的现金流量净额/流动负债
    debt_to_eqt = models.FloatField(
        _('产权比率'), blank=True, null=True)  # float Y	产权比率
    eqt_to_debt = models.FloatField(
        _('归属于母公司的股东权益/负债合计'), blank=True, null=True)  # float	Y	归属于母公司的股东权益/负债合计
    eqt_to_interestdebt = models.FloatField(
        _('归属于母公司的股东权益/带息债务'), blank=True, null=True)  # float	Y	归属于母公司的股东权益/带息债务
    tangibleasset_to_debt = models.FloatField(
        _('有形资产/负债合计'), blank=True, null=True)  # float	Y	有形资产/负债合计
    tangasset_to_intdebt = models.FloatField(
        _('有形资产/带息债务'), blank=True, null=True)  # float	Y	有形资产/带息债务
    tangibleasset_to_netdebt = models.FloatField(
        _('有形资产/净债务'), blank=True, null=True)  # float	Y	有形资产/净债务
    ocf_to_debt = models.FloatField(
        _('经营活动产生的现金流量净额/负债合计'), blank=True, null=True)  # float	Y	经营活动产生的现金流量净额/负债合计
    ocf_to_interestdebt = models.FloatField(
        _('经营活动产生的现金流量净额/带息债务'), blank=True, null=True)  # float	N	经营活动产生的现金流量净额/带息债务
    ocf_to_netdebt = models.FloatField(
        _('经营活动产生的现金流量净额/净债务'), blank=True, null=True)  # float	N	经营活动产生的现金流量净额/净债务
    ebit_to_interest = models.FloatField(
        _('已获利息倍数(EBIT/利息费用)'), blank=True, null=True)  # float	N	已获利息倍数(EBIT/利息费用)
    longdebt_to_workingcapital = models.FloatField(
        _('长期债务与营运资金比率'), blank=True, null=True)  # float	N	长期债务与营运资金比率
    ebitda_to_debt = models.FloatField(
        _('息税折旧摊销前利润/负债合计'), blank=True, null=True)  # float	N	息税折旧摊销前利润/负债合计
    turn_days = models.FloatField(
        _('营业周期'), blank=True, null=True)  # float	Y	营业周期
    roa_yearly = models.FloatField(
        _('年化总资产净利率'), blank=True, null=True)  # float	Y	年化总资产净利率
    roa_dp = models.FloatField(
        _('总资产净利率'), blank=True, null=True)  # float	Y	总资产净利率(杜邦分析)
    fixed_assets = models.FloatField(
        _('固定资产合计'), blank=True, null=True)  # float	Y	固定资产合计
    profit_prefin_exp = models.FloatField(
        _('扣除财务费用前营业利润'), blank=True, null=True)  # float	N	扣除财务费用前营业利润
    non_op_profit = models.FloatField(
        _('非营业利润'), blank=True, null=True)  # float	N	非营业利润
    op_to_ebt = models.FloatField(
        _('营业利润／利润总额'), blank=True, null=True)  # float	N	营业利润／利润总额
    nop_to_ebt = models.FloatField(
        _('非营业利润／利润总额'), blank=True, null=True)  # float	N	非营业利润／利润总额
    ocf_to_profit = models.FloatField(
        _('经营活动产生的现金流量净额／营业利润'), blank=True, null=True)  # float	N	经营活动产生的现金流量净额／营业利润
    cash_to_liqdebt = models.FloatField(
        _('货币资金／流动负债'), blank=True, null=True)  # float	N	货币资金／流动负债
    cash_to_liqdebt_withinterest = models.FloatField(
        _('货币资金／带息流动负债'), blank=True, null=True)  # float	N	货币资金／带息流动负债
    op_to_liqdebt = models.FloatField(
        _('营业利润／流动负债'), blank=True, null=True)  # float	N	营业利润／流动负债
    op_to_debt = models.FloatField(
        _('营业利润／负债合计'), blank=True, null=True)  # float	N	营业利润／负债合计
    roic_yearly = models.FloatField(
        _('年化投入资本回报率'), blank=True, null=True)  # float	N	年化投入资本回报率
    total_fa_trun = models.FloatField(
        _('固定资产合计周转率'), blank=True, null=True)  # float	N	固定资产合计周转率
    profit_to_op = models.FloatField(
        _('利润总额／营业收入'), blank=True, null=True)  # float	Y	利润总额／营业收入
    q_opincome = models.FloatField(
        _('经营活动单季度净收益'), blank=True, null=True)  # float	N	经营活动单季度净收益
    q_investincome = models.FloatField(
        _('价值变动单季度净收益'), blank=True, null=True)  # float	N	价值变动单季度净收益
    q_dtprofit = models.FloatField(
        _('扣除非经常损益后的单季度净利润'), blank=True, null=True)  # float	N	扣除非经常损益后的单季度净利润
    q_eps = models.FloatField(
        _('每股收益'), blank=True, null=True)  # float	N	每股收益(单季度)
    q_netprofit_margin = models.FloatField(
        _('销售净利率'), blank=True, null=True)  # float	N	销售净利率(单季度)
    q_gsprofit_margin = models.FloatField(
        _('销售毛利率'), blank=True, null=True)  # float	N	销售毛利率(单季度)
    q_exp_to_sales = models.FloatField(
        _('销售期间费用率'), blank=True, null=True)  # float	N	销售期间费用率(单季度)
    q_profit_to_gr = models.FloatField(
        _('净利润／营业总收入'), blank=True, null=True)  # float	N	净利润／营业总收入(单季度)
    q_saleexp_to_gr = models.FloatField(
        _('销售费用／营业总收入'), blank=True, null=True)  # float	Y	销售费用／营业总收入 (单季度)
    q_adminexp_to_gr = models.FloatField(
        _('管理费用／营业总收入'), blank=True, null=True)  # float	N	管理费用／营业总收入 (单季度)
    q_finaexp_to_gr = models.FloatField(
        _('财务费用／营业总收入'), blank=True, null=True)  # float	N	财务费用／营业总收入 (单季度)
    q_impair_to_gr_ttm = models.FloatField(
        _('资产减值损失／营业总收入'), blank=True, null=True)  # float	N	资产减值损失／营业总收入(单季度)
    q_gc_to_gr = models.FloatField(
        _('营业总成本／营业总收入'), blank=True, null=True)  # float	Y	营业总成本／营业总收入 (单季度)
    q_op_to_gr = models.FloatField(
        _('营业利润／营业总收入'), blank=True, null=True)  # float	N	营业利润／营业总收入(单季度)
    q_roe = models.FloatField(
        _('净资产收益率'), blank=True, null=True)  # float	Y	净资产收益率(单季度)
    q_dt_roe = models.FloatField(
        _('净资产单季度收益率'), blank=True, null=True)  # float	Y	净资产单季度收益率(扣除非经常损益)
    q_npta = models.FloatField(
        _('总资产净利润'), blank=True, null=True)  # float	Y	总资产净利润(单季度)
    q_opincome_to_ebt = models.FloatField(
        _('经营活动净收益／利润总额'), blank=True, null=True)  # float	N	经营活动净收益／利润总额(单季度)
    q_investincome_to_ebt = models.FloatField(
        _('价值变动净收益／利润总额'), blank=True, null=True)  # float	N	价值变动净收益／利润总额(单季度)
    q_dtprofit_to_profit = models.FloatField(
        _('扣除非经常损益后的净利润／净利润'), blank=True, null=True)  # float	N	扣除非经常损益后的净利润／净利润(单季度)
    q_salescash_to_or = models.FloatField(
        _('销售商品提供劳务收到的现金／营业收入'), blank=True, null=True)  # float	N	销售商品提供劳务收到的现金／营业收入(单季度)
    q_ocf_to_sales = models.FloatField(
        _('经营活动产生的现金流量净额／营业收入'), blank=True, null=True)  # float	Y	经营活动产生的现金流量净额／营业收入(单季度)
    q_ocf_to_or = models.FloatField(
        _('经营活动产生的现金流量净额／经营活动净收益'), blank=True, null=True)  # float	N	经营活动产生的现金流量净额／经营活动净收益(单季度)
    basic_eps_yoy = models.FloatField(
        _('基本每股收益同比增长率'), blank=True, null=True)  # float	Y	基本每股收益同比增长率(%)
    dt_eps_yoy = models.FloatField(
        _('稀释每股收益同比增长率'), blank=True, null=True)  # float	Y	稀释每股收益同比增长率(%)
    cfps_yoy = models.FloatField(
        _('每股经营活动产生的现金流量净额同比增长率'), blank=True, null=True)  # float	Y	每股经营活动产生的现金流量净额同比增长率(%)
    op_yoy = models.FloatField(
        _('营业利润同比增长率'), blank=True, null=True)  # float	Y	营业利润同比增长率(%)
    ebt_yoy = models.FloatField(
        _('利润总额同比增长率'), blank=True, null=True)  # float	Y	利润总额同比增长率(%)
    netprofit_yoy = models.FloatField(
        _('归属母公司股东的净利润同比增长率'), blank=True, null=True)  # float	Y	归属母公司股东的净利润同比增长率(%)
    dt_netprofit_yoy = models.FloatField(
        _('归属母公司股东的净利润-扣除非经常损益同比增长率'), blank=True, null=True)  # float	Y	归属母公司股东的净利润-扣除非经常损益同比增长率(%)
    ocf_yoy = models.FloatField(
        _('经营活动产生的现金流量净额同比增长率'), blank=True, null=True)  # float	Y	经营活动产生的现金流量净额同比增长率(%)
    roe_yoy = models.FloatField(
        _('净资产收益率(摊薄)同比增长率'), blank=True, null=True)  # float	Y	净资产收益率(摊薄)同比增长率(%)
    bps_yoy = models.FloatField(
        _('每股净资产相对年初增长率'), blank=True, null=True)  # float	Y	每股净资产相对年初增长率(%)
    assets_yoy = models.FloatField(
        _('资产总计相对年初增长率'), blank=True, null=True)  # float	Y	资产总计相对年初增长率(%)
    eqt_yoy = models.FloatField(
        _('归属母公司的股东权益相对年初增长率'), blank=True, null=True)  # float	Y	归属母公司的股东权益相对年初增长率(%)
    tr_yoy = models.FloatField(
        _('营业总收入同比增长率'), blank=True, null=True)  # float	Y	营业总收入同比增长率(%)
    or_yoy = models.FloatField(
        _('营业收入同比增长率'), blank=True, null=True)  # float	Y	营业收入同比增长率(%)
    q_gr_yoy = models.FloatField(
        _('营业总收入同比增长率'), blank=True, null=True)  # float	N	营业总收入同比增长率(%)(单季度)
    q_gr_qoq = models.FloatField(
        _('营业总收入环比增长率'), blank=True, null=True)  # float	N	营业总收入环比增长率(%)(单季度)
    q_sales_yoy = models.FloatField(
        _('营业收入同比增长率'), blank=True, null=True)  # float	Y	营业收入同比增长率(%)(单季度)
    q_sales_qoq = models.FloatField(
        _('营业收入环比增长率'), blank=True, null=True)  # float	N	营业收入环比增长率(%)(单季度)
    q_op_yoy = models.FloatField(
        _('营业利润同比增长率'), blank=True, null=True)  # float	N	营业利润同比增长率(%)(单季度)
    q_op_qoq = models.FloatField(
        _('营业利润环比增长率'), blank=True, null=True)  # float	Y	营业利润环比增长率(%)(单季度)
    q_profit_yoy = models.FloatField(
        _('净利润同比增长率'), blank=True, null=True)  # float	N	净利润同比增长率(%)(单季度)
    q_profit_qoq = models.FloatField(
        _('净利润环比增长率'), blank=True, null=True)  # float	N	净利润环比增长率(%)(单季度)
    q_netprofit_yoy = models.FloatField(
        _('归属母公司股东的净利润同比增长率'), blank=True, null=True)  # float	N	归属母公司股东的净利润同比增长率(%)(单季度)
    q_netprofit_qoq = models.FloatField(
        _('归属母公司股东的净利润环比增长率'), blank=True, null=True)  # float	N	归属母公司股东的净利润环比增长率(%)(单季度)
    equity_yoy = models.FloatField(
        _('净资产同比增长率'), blank=True, null=True)  # float	Y	净资产同比增长率
    rd_exp = models.FloatField(
        _('研发费用'), blank=True, null=True)  # float	N	研发费用
    update_flag = models.CharField(
        _('更新标识'),  max_length=5, blank=True, null=True)  # str	N	更新标识
    # daily basic，用于市值估算
    total_mv = models.FloatField(
        _('总市值'), blank=True, null=True)  # float	Y	价格
    close = models.FloatField(
        _('价格'), blank=True, null=True)  # float	Y	价格
    pe = models.FloatField(
        _('pe'), blank=True, null=True)  # float	Y	pe
    pe_ttm = models.FloatField(
        _('pe_ttm'), blank=True, null=True)  # float	Y	pe_ttm
    pb = models.FloatField(
        _('pb'), blank=True, null=True)  # float	Y	pb
    ps = models.FloatField(
        _('ps'), blank=True, null=True)  # float	Y	ps
    ps_ttm = models.FloatField(
        _('ps_ttm'), blank=True, null=True)  # float	Y	ps_ttm
    company = models.ForeignKey(
        StockNameCodeMap, related_name='fin_indicator', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-end_date']
        verbose_name = _('财务指标')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class CompanyTop10FloatHolders(BaseModel):
    '''
    ts_code	str	TS股票代码
    ann_date	str	公告日期
    end_date	str	报告期
    holder_name	str	股东名称
    hold_amount	float	持有数量（股）
    '''
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, db_index=True)  # e.g. 000001.SZ
    announce_date = models.DateField(
        _('公告日期'), blank=True, null=True)
    end_date = models.DateField(
        _('截至日期'), blank=True, null=True)
    holder_name = models.CharField(
        _('股东名称'), max_length=200, blank=True, null=True)
    hold_amount = models.FloatField(
        _('持股数'), blank=True, null=True)
    company = models.ForeignKey(
        StockNameCodeMap, related_name='top10_holder', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-end_date']
        verbose_name = _('前10大流通股')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class CompanyTop10FloatHoldersFilter(BaseModel):
    '''
    ts_code	str	TS股票代码
    ann_date	str	公告日期
    end_date	str	报告期
    holder_name	str	股东名称
    hold_amount	float	持有数量（股）
    '''
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, db_index=True)  # e.g. 000001.SZ
    announce_date = models.DateField(
        _('公告日期'), blank=True, null=True)
    end_date = models.DateField(
        _('截至日期'), blank=True, null=True)
    hold_pct = models.FloatField(
        _('持股比例'), blank=True, null=True)
    hold_amount = models.FloatField(
        _('持股数'), blank=True, null=True)
    float_amount = models.FloatField(
        _('流通股数'), blank=True, null=True)
    company = models.OneToOneField(
        StockNameCodeMap, related_name='top10_holder_pct', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-end_date']
        verbose_name = _('前10大流通股持股比例')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class CompanyTop10FloatHoldersStat(BaseModel):
    '''
    ts_code	str	TS股票代码
    ann_date	str	公告日期
    end_date	str	报告期
    holder_name	str	股东名称
    hold_amount	float	持有数量（股）
    '''
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, db_index=True)  # e.g. 000001.SZ
    announce_date = models.DateField(
        _('公告日期'), blank=True, null=True)
    end_date = models.DateField(
        _('截至日期'), blank=True, null=True)
    hold_pct = models.FloatField(
        _('持股比例'), blank=True, null=True)
    hold_amount = models.FloatField(
        _('持股数'), blank=True, null=True)
    float_amount = models.FloatField(
        _('流通股数'), blank=True, null=True)
    close = models.FloatField(_('收盘价'),
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
    company = models.ForeignKey(
        StockNameCodeMap, related_name='top10_holder_stat', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-end_date']
        verbose_name = _('前10大流通股持股统计')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class CompanyIndicatorCorrelation(BaseModel):
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False, db_index=True)  # e.g. 000001.SZ
    end_date = models.DateField(
        _('报告期'), blank=True, null=True)  # end_date	str	Y	报告期
    a_indicator = models.FloatField(
        _('计算指标'), blank=True, null=True,  db_index=True)  # float	Y	期末总股本
    correlation = models.FloatField(
        _('关联度'), blank=True, null=True)  # float	Y	资本公积金
    company = models.ForeignKey(
        StockNameCodeMap, related_name='company_correlation', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-end_date']
        verbose_name = _('指标关联度')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'