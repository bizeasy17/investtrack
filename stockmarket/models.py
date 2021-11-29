from enum import unique
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
        unique_together = ('name','country')
        verbose_name = _('省份')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class City(BaseModel):
    name = models.CharField(
        _('城市'), max_length=50, blank=False, null=False, unique=True, db_index=True)  # name e.g. 平安银行
    province = models.ForeignKey(Province, related_name='city_province', blank=True, null=True, on_delete=models.SET_NULL)
    city_pinyin = models.CharField(
        _('城市拼音'), max_length=50, blank=True, null=True,)

    class Meta:
        ordering = ['name']
        unique_together = ('name','province')
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
        

    def __str__(self):
        return self.stock_name

    def get_latest_history(self):
        return self.close_history.first()

    def get_latest_daily_basic(self):
        return self.daily_basic.first()

    def get_company_basic(self):
        return self.company_basic.first()

    # def get_company_basic_by_province(self, province):
    #     return self.company_basic.filter()

    def get_company_top10_holders(self):
        return self.top10_holder.order_by('-end_date')[:10]

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
    '''
    ts_code	str	Y	TS股票代码
    ann_date	str	Y	公告日期
    f_ann_date	str	Y	实际公告日期
    end_date	str	Y	报告期
    report_type	str	Y	报表类型
    comp_type	str	Y	公司类型(1一般工商业2银行3保险4证券)
    end_type	str	Y	报告期类型
    total_share	float	Y	期末总股本
    cap_rese	float	Y	资本公积金
    undistr_porfit	float	Y	未分配利润
    surplus_rese	float	Y	盈余公积金
    special_rese	float	Y	专项储备
    money_cap	float	Y	货币资金
    trad_asset	float	Y	交易性金融资产
    notes_receiv	float	Y	应收票据
    accounts_receiv	float	Y	应收账款
    oth_receiv	float	Y	其他应收款
    prepayment	float	Y	预付款项
    div_receiv	float	Y	应收股利
    int_receiv	float	Y	应收利息
    inventories	float	Y	存货
    amor_exp	float	Y	长期待摊费用
    nca_within_1y	float	Y	一年内到期的非流动资产
    sett_rsrv	float	Y	结算备付金
    loanto_oth_bank_fi	float	Y	拆出资金
    premium_receiv	float	Y	应收保费
    reinsur_receiv	float	Y	应收分保账款
    reinsur_res_receiv	float	Y	应收分保合同准备金
    pur_resale_fa	float	Y	买入返售金融资产
    oth_cur_assets	float	Y	其他流动资产
    total_cur_assets	float	Y	流动资产合计
    fa_avail_for_sale	float	Y	可供出售金融资产
    htm_invest	float	Y	持有至到期投资
    lt_eqt_invest	float	Y	长期股权投资
    invest_real_estate	float	Y	投资性房地产
    time_deposits	float	Y	定期存款
    oth_assets	float	Y	其他资产
    lt_rec	float	Y	长期应收款
    fix_assets	float	Y	固定资产
    cip	float	Y	在建工程
    const_materials	float	Y	工程物资
    fixed_assets_disp	float	Y	固定资产清理
    produc_bio_assets	float	Y	生产性生物资产
    oil_and_gas_assets	float	Y	油气资产
    intan_assets	float	Y	无形资产
    r_and_d	float	Y	研发支出
    goodwill	float	Y	商誉
    lt_amor_exp	float	Y	长期待摊费用
    defer_tax_assets	float	Y	递延所得税资产
    decr_in_disbur	float	Y	发放贷款及垫款
    oth_nca	float	Y	其他非流动资产
    total_nca	float	Y	非流动资产合计
    cash_reser_cb	float	Y	现金及存放中央银行款项
    depos_in_oth_bfi	float	Y	存放同业和其它金融机构款项
    prec_metals	float	Y	贵金属
    deriv_assets	float	Y	衍生金融资产
    rr_reins_une_prem	float	Y	应收分保未到期责任准备金
    rr_reins_outstd_cla	float	Y	应收分保未决赔款准备金
    rr_reins_lins_liab	float	Y	应收分保寿险责任准备金
    rr_reins_lthins_liab	float	Y	应收分保长期健康险责任准备金
    refund_depos	float	Y	存出保证金
    ph_pledge_loans	float	Y	保户质押贷款
    refund_cap_depos	float	Y	存出资本保证金
    indep_acct_assets	float	Y	独立账户资产
    client_depos	float	Y	其中：客户资金存款
    client_prov	float	Y	其中：客户备付金
    transac_seat_fee	float	Y	其中:交易席位费
    invest_as_receiv	float	Y	应收款项类投资
    total_assets	float	Y	资产总计
    lt_borr	float	Y	长期借款
    st_borr	float	Y	短期借款
    cb_borr	float	Y	向中央银行借款
    depos_ib_deposits	float	Y	吸收存款及同业存放
    loan_oth_bank	float	Y	拆入资金
    trading_fl	float	Y	交易性金融负债
    notes_payable	float	Y	应付票据
    acct_payable	float	Y	应付账款
    adv_receipts	float	Y	预收款项
    sold_for_repur_fa	float	Y	卖出回购金融资产款
    comm_payable	float	Y	应付手续费及佣金
    payroll_payable	float	Y	应付职工薪酬
    taxes_payable	float	Y	应交税费
    int_payable	float	Y	应付利息
    div_payable	float	Y	应付股利
    oth_payable	float	Y	其他应付款
    acc_exp	float	Y	预提费用
    deferred_inc	float	Y	递延收益
    st_bonds_payable	float	Y	应付短期债券
    payable_to_reinsurer	float	Y	应付分保账款
    rsrv_insur_cont	float	Y	保险合同准备金
    acting_trading_sec	float	Y	代理买卖证券款
    acting_uw_sec	float	Y	代理承销证券款
    non_cur_liab_due_1y	float	Y	一年内到期的非流动负债
    oth_cur_liab	float	Y	其他流动负债
    total_cur_liab	float	Y	流动负债合计
    bond_payable	float	Y	应付债券
    lt_payable	float	Y	长期应付款
    specific_payables	float	Y	专项应付款
    estimated_liab	float	Y	预计负债
    defer_tax_liab	float	Y	递延所得税负债
    defer_inc_non_cur_liab	float	Y	递延收益-非流动负债
    oth_ncl	float	Y	其他非流动负债
    total_ncl	float	Y	非流动负债合计
    depos_oth_bfi	float	Y	同业和其它金融机构存放款项
    deriv_liab	float	Y	衍生金融负债
    depos	float	Y	吸收存款
    agency_bus_liab	float	Y	代理业务负债
    oth_liab	float	Y	其他负债
    prem_receiv_adva	float	Y	预收保费
    depos_received	float	Y	存入保证金
    ph_invest	float	Y	保户储金及投资款
    reser_une_prem	float	Y	未到期责任准备金
    reser_outstd_claims	float	Y	未决赔款准备金
    reser_lins_liab	float	Y	寿险责任准备金
    reser_lthins_liab	float	Y	长期健康险责任准备金
    indept_acc_liab	float	Y	独立账户负债
    pledge_borr	float	Y	其中:质押借款
    indem_payable	float	Y	应付赔付款
    policy_div_payable	float	Y	应付保单红利
    total_liab	float	Y	负债合计
    treasury_share	float	Y	减:库存股
    ordin_risk_reser	float	Y	一般风险准备
    forex_differ	float	Y	外币报表折算差额
    invest_loss_unconf	float	Y	未确认的投资损失
    minority_int	float	Y	少数股东权益
    total_hldr_eqy_exc_min_int	float	Y	股东权益合计(不含少数股东权益)
    total_hldr_eqy_inc_min_int	float	Y	股东权益合计(含少数股东权益)
    total_liab_hldr_eqy	float	Y	负债及股东权益总计
    lt_payroll_payable	float	Y	长期应付职工薪酬
    oth_comp_income	float	Y	其他综合收益
    oth_eqt_tools	float	Y	其他权益工具
    oth_eqt_tools_p_shr	float	Y	其他权益工具(优先股)
    lending_funds	float	Y	融出资金
    acc_receivable	float	Y	应收款项
    st_fin_payable	float	Y	应付短期融资款
    payables	float	Y	应付款项
    hfs_assets	float	Y	持有待售的资产
    hfs_sales	float	Y	持有待售的负债
    cost_fin_assets	float	Y	以摊余成本计量的金融资产
    fair_value_fin_assets	float	Y	以公允价值计量且其变动计入其他综合收益的金融资产
    cip_total	float	Y	在建工程(合计)(元)
    oth_pay_total	float	Y	其他应付款(合计)(元)
    long_pay_total	float	Y	长期应付款(合计)(元)
    debt_invest	float	Y	债权投资(元)
    oth_debt_invest	float	Y	其他债权投资(元)
    oth_eq_invest	float	N	其他权益工具投资(元)
    oth_illiq_fin_assets	float	N	其他非流动金融资产(元)
    oth_eq_ppbond	float	N	其他权益工具:永续债(元)
    receiv_financing	float	N	应收款项融资
    use_right_assets	float	N	使用权资产
    lease_liab	float	N	租赁负债
    contract_assets	float	Y	合同资产
    contract_liab	float	Y	合同负债
    accounts_receiv_bill	float	Y	应收票据及应收账款
    accounts_pay	float	Y	应付票据及应付账款
    oth_rcv_total	float	Y	其他应收款(合计)（元）
    fix_assets_total	float	Y	固定资产(合计)(元)
    update_flag	str	Y	更新标识
    '''

    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False)  # e.g. 000001.SZ
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


class CompanyTop10FloatHolders(BaseModel):
    '''
    ts_code	str	TS股票代码
    ann_date	str	公告日期
    end_date	str	报告期
    holder_name	str	股东名称
    hold_amount	float	持有数量（股）
    '''
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False)  # e.g. 000001.SZ
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
