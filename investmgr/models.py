import logging
from abc import ABCMeta, abstractmethod, abstractproperty

import tushare as ts
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

# token settings (not sure should put it here)
ts.set_token('3ebfccf82c537f1e8010e97707393003c1d98b86907dfd09f9d17589')

# Create your models here.


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(_('创建时间'), default=now)
    last_mod_time = models.DateTimeField(_('修改时间'), default=now)

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


class TradeRec(BaseModel):
    """交易记录"""
    VISIBLE_CHOICES = (
        ('g', _('公开')),
        ('s', _('私密')),
        ('f', _('仅好友')),
    )
    COMMENT_STATUS = (
        ('o', _('打开')),
        ('c', _('关闭')),
    )
    TRADE_DIRECTION = (
        ('b', _('买入')),
        ('s', _('卖出')),
    )

    # slug = models.SlugField(default='no-slug', max_length=200, blank=True)
    market = models.CharField(
        _('股票市场'), max_length=10, blank=False, null=False, editable=False)
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=False, null=False)
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False)
    direction = models.CharField(_('交易类型'), max_length=1,
                                 choices=TRADE_DIRECTION, default='b')
    # 交易日期
    trade_time = models.DateTimeField(
        '交易时间', default=now, blank=False, null=False)
    price = models.FloatField(_('交易价格'), blank=False, null=False)
    target_position = models.PositiveIntegerField(
        _('目标仓位（手）'), blank=False, null=False, default=100)
    board_lots = models.PositiveIntegerField(_('本次交易量(手)'), default=100)
    cash = models.FloatField(_('投入现金额'), blank=True, null=True)
    visible = models.CharField(_('可见性'), max_length=1,
                               choices=VISIBLE_CHOICES, default='s')
    comment_status = models.CharField(
        _('评论状态'), max_length=1, choices=COMMENT_STATUS, default='c')
    views = models.PositiveIntegerField(_('浏览量'), default=0)
    trader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
                               on_delete=models.CASCADE)
    strategy = models.ForeignKey(
        'TradeStrategy', verbose_name=_('策略'), on_delete=models.SET_NULL, blank=True, null=True)
    # tags = models.ManyToManyField('Tag', verbose_name=_('标签集合'), blank=True)
    featured_image = models.ImageField(
        _('特色图片'), upload_to='investmgr_pictures/%Y/%m/%d/', blank=True, null=True, editable=False)
    in_stock_positions = models.ForeignKey('Positions', verbose_name=_('股票持仓'), blank=False, null=True,
                                           on_delete=models.CASCADE, editable=False)
    is_deleted = models.BooleanField(
        _('是否被删除'), blank=False, null=False, default=False)

    def __str__(self):
        return self.stock_name

    class Meta:
        ordering = ['-created_time']
        verbose_name = _('交易记录')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def get_absolute_url(self):
        return reverse('investmgr:detailbyid', kwargs={
            'investmgr_id': self.id,
            'year': self.created_time.year,
            'month': self.created_time.month,
            'day': self.created_time.day
        })

    def get_strategy_tree(self):
        tree = self.strategy.get_strategy_tree()
        names = list(map(lambda s: (s.name, s.get_absolute_url()), tree))
        return names

    def save(self, *args, **kwargs):
        # 自动给股票代码加上.SH或者.SZ
        if self.stock_code.isnumeric():
            if str(self.stock_code)[0] == '6':
                self.stock_code = + self.stock_code + '.SH'
                self.market = 'SH'
            else:
                self.stock_code = self.stock_code + '.SZ'
                self.market = 'SZ'

        # 更新持仓
        p = Positions.objects.filter(
            trader=self.trader.id, stock_code=self.stock_code, is_liquadated=False)
        if p.count() == 0:
            # 新建仓
            p = Positions(market=self.market,
                          stock_name=self.stock_name, stock_code=self.stock_code)
            self.in_stock_positions = p
        else:
            # 增仓或者减仓
            p = p[0]
            self.in_stock_positions = p

        p.update_stock_position(
            self.direction, self.target_position, self.board_lots, self.price, self.cash, self.trader)
        super().save(*args, **kwargs)


# 目前持有仓位数据model
class Positions(BaseModel):
    market = models.CharField(
        _('股票市场'), max_length=10, blank=False, null=False)
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=False, null=False)
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False)
    trader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('持仓人'), blank=False, null=False,
                               on_delete=models.CASCADE)
    position_price = models.FloatField(
        _('持仓价格'), blank=False, null=False, default=0)
    current_price = models.FloatField(
        _('股票现价'), blank=False, null=False, default=0)
    profit = models.FloatField(_('利润'), blank=False, null=False, default=0)
    cash = models.FloatField(_('投入现金额'), blank=False, null=False, default=0)
    lots = models.PositiveIntegerField(_('持仓量(手)'), default=0)
    target_position = models.FloatField(
        _('仓位'), blank=False, null=False, default='0')
    is_liquadated = models.BooleanField(
        _('是否清仓'), blank=False, null=False, default=False, db_index=True)

    def __str__(self):
        return self.stock_name

    # 持仓算法
    def update_stock_position(self, trade_direction, target_position, trade_lots, trade_price, trade_cash, trader):
        self.trader = trader
        self.cash += trade_cash
        if self.target_position == 0:
            self.target_position = target_position

        # 获得实时报价
        realtime_df = ts.get_realtime_quotes(
            str(self.stock_code).split('.')[0])  # 需要再判断一下ts_code
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'time']]
        realtime_price = realtime_df['price'].mean()

        # 计算持仓股利润
        # 持仓利润 = 原持仓利润 + (如果未收盘tushare取当前股票价格/收盘价c - 目前持仓价格) * 持仓数量(手) * 100 (1手=100股)
        if self.lots != 0 or self.position_price != 0:
            self.profit = self.profit + \
                float((realtime_price - self.position_price) * self.lots * 100)

        if trade_direction == 'b':
            # 已有仓位加仓
            '''
            1. 利润 = 原持仓利润 + (如果未收盘tushare取当前股票价格/收盘价c - 交易价格) * 本次交易量(手) * 100 (1手=100股)
            2. 持仓价格 = 
            2.1 如果利润是(负-)的
                每手亏损 = 利润 / (已有持仓+新增持仓量(手)）
                持仓价格 = 当前股票价格：如果未收盘/收盘价 + 每手亏损
            2.2 如果利润是(正+)的
                每手利润 = 利润 / (已有持仓+新增持仓量(手)）
                持仓价格 = 当前股票价格：如果未收盘/收盘价 - 每手利润
            '''
            # 计算
            self.profit = self.profit + \
                (realtime_price - trade_price) * trade_lots * 100
            new_position_price = realtime_price - self.profit / \
                (trade_lots + self.lots)
            self.position_price = new_position_price
            self.current_price = realtime_price
            self.lots = trade_lots + self.lots
        else:  # 已有仓位减仓
            if self.lots == trade_lots:
                # 清仓，设置is_liquadated = True
                self.is_liquadated = True
                self.lots = 0
                self.cash = 0
                self.current_price = realtime_price
            else:
                    # 普通减仓
                '''
                1. 利润 = 原持仓利润 + (当前股票价格：如果未收盘/收盘价 - 交易价格) * 本次交易量(手) * 100 (1手=100股)
                2. 持仓价格 = 
                2.1 如果利润是(负-)的
                    每手亏损 = 利润 / (已有持仓-卖出量(手)）
                    持仓价格 = 当前股票价格：如果未收盘/收盘价 + 每手亏损
                2.2 如果利润是(正+)的
                    每手利润 = 利润 / (已有持仓-卖出量(手)）
                    持仓价格 = 当前股票价格：如果未收盘/收盘价 - 每手利润
                '''
                self.profit = self.profit + \
                    (realtime_price - trade_price) * trade_lots * 100
                new_position_price = realtime_price - self.profit / \
                    (self.lots - trade_lots)
                self.position_price = new_position_price
                self.current_price = realtime_price

        self.save()

    class Meta:
        ordering = ['stock_code']
        verbose_name = _('持仓')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class TradeStrategy(BaseModel):
    """"""
    name = models.CharField(_('策略名'), max_length=30, unique=True)
    parent_strategy = models.ForeignKey(
        'self', verbose_name=_('父级策略'), blank=True, null=True, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
                                on_delete=models.CASCADE)

    # slug = models.SlugField(default='no-slug', max_length=60, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('交易策略')
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse('investmgr:strategy_detail_by_id', kwargs={'id': self.id})

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

    def get_sub_strategies(self):
        """
        获得当前分类目录所有子集
        :return: 
        """
        strategies = []
        all_strategies = TradeStrategy.objects.all()

        def parse(strategy):
            if strategy not in strategies:
                strategies.append(strategy)
            childs = all_strategies.filter(parent_strategy=strategy)
            for child in childs:
                if strategy not in strategies:
                    strategies.append(child)
                parse(child)

        parse(self)
        return strategies


class StockNameCodeMap(BaseModel):
    STOCK_MARKET_CHOICES = (
        ('SH', _('上海')),
        ('SZ', _('深圳')),
    )

    market = models.CharField(
        _('股票市场'), choices=STOCK_MARKET_CHOICES, max_length=50, blank=True, null=True)
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=False, null=False, unique=True)
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False, unique=True)
    is_valid = models.BooleanField(
        _('是否退市'), blank=False, null=False, default=False)

    def __str__(self):
        return self.stock_name

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('股票代码表')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
