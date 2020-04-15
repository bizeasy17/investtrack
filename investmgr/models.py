import logging
import random
import string
from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import date, datetime, timedelta
from decimal import *

import tushare as ts
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Sum
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from . import utils

# token settings (not sure should put it here)
# ts.set_token('3ebfccf82c537f1e8010e97707393003c1d98b86907dfd09f9d17589')

# Create your models here.
logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(_('创建时间'), default=now)
    last_mod_time = models.DateTimeField(_('最后更新时间'), default=now)

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


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

    STOCK_MARKET_CHOICES = (
        ('ZB', _('主板')),
        ('ZXB', _('中小板')),
        ('CYB', _('创业板')),
        ('KCB', _('科创板')),

    )

    # slug = models.SlugField(default='no-slug', max_length=200, blank=True)
    market = models.CharField(
        _('股票市场'), choices=STOCK_MARKET_CHOICES, max_length=10, blank=False, null=False, editable=False)
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=False, null=False)
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False)
    direction = models.CharField(_('交易类型'), max_length=1,
                                 choices=TRADE_DIRECTION, default='b')
    # 交易日期
    trade_time = models.DateTimeField(
        '交易时间', default=now, blank=False, null=False)
    price = models.DecimalField(
        _('交易价格'), max_digits=5, decimal_places=2, blank=False, null=False)
    sell_price = models.DecimalField(
        _('卖出价'), max_digits=5, decimal_places=2, blank=True, null=True)
    current_price = models.DecimalField(
        _('股票现价'), max_digits=5, decimal_places=2, blank=False, null=False, default=0)
    target_position = models.PositiveIntegerField(
        _('目标仓位（股）'), blank=True, null=True, default=100)
    board_lots = models.PositiveIntegerField(_('本次交易量(股)'), default=100)
    lots_remain = models.PositiveIntegerField(_('剩余持仓'), default=0)
    cash = models.DecimalField(
        _('交易现金额'), max_digits=10, decimal_places=2, blank=True, null=True)
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
    is_liquadated = models.BooleanField(
        _('是否已清仓'), blank=False, null=False, default=False, editable=False)
    trade_account = models.ForeignKey(
        'TradeAccount', verbose_name=_('交易账户'), on_delete=models.SET_NULL, blank=True, null=True)
    rec_ref_number = models.CharField(
        _('买入记录编号'), max_length=10, blank=True, null=True)
    sell_stock_refer = models.ForeignKey(
        'TradeRec', verbose_name=_('卖对应之买入'), on_delete=models.SET_NULL, blank=True, null=True)
    is_sold = models.BooleanField(
        _('是否已卖出'), blank=False, null=False, default=False)
    sold_time = models.DateTimeField(
        '卖出时间', blank=True, null=True)
    created_or_mod_by = models.CharField(
        _('创建人'), max_length=50, blank=False, null=False, editable=False, default='human')

    def __str__(self):
        return self.stock_name

    class Meta:
        ordering = ['-last_mod_time']
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

    def sync_stock_price_for_investor(self, investor):
        '''
        根据stock_symbol更新最新的价格
        '''
        stock_symbols = []
        stock_symbols_dict = Positions.objects.filter(trader=investor).exclude(
            is_liquadated=True,).distinct().values('stock_code')
        try:
            if stock_symbols_dict is not None and len(stock_symbols_dict) > 0:
                for stock_symbol in stock_symbols_dict.values():
                    stock_symbols.append(stock_symbol)
            realtime_stock_quotes = utils.get_realtime_price(stock_symbols)
            in_stock_positions = Positions.objects.select_for_update().filter(
                trader=investor).exclude(is_liquadated=True,)
            with transaction.atomic():
                for entry in in_stock_positions:
                    entry.make_profit_updated(
                        realtime_stock_quotes[entry.stock_code])
        except Exception as e:
            logger.error(e)

    def save(self, *args, **kwargs):
        # 自动给股票代码加上.SH或者.SZ
        # if self.stock_name.isnumeric():  # 用户的输入为股票代码
        #     code = self.stock_name
        #     map = StockNameCodeMap.objects.filter(stock_code=code)
        #     if map.count() > 0:
        #         self.stock_name = map[0].stock_name
        #         self.stock_code = map[0].stock_code
        #     # else: not found
        # else:  # 用户的输入为股票名称
        #     map = StockNameCodeMap.objects.filter(stock_name=self.stock_name)
        #     if map.count() > 0:
        #         self.stock_code = map[0].stock_code

        # if str(self.stock_code)[0] == '6':
        #     # self.stock_code = self.stock_code + '.SH'
        #     self.market = 'SH'
        # else:
        #     # self.stock_code = self.stock_code + '.SZ'
        #     self.market = 'SZ'
        # if self.direction == 'b'if: #and not self.created_or_mod_by == 'system':
        if not self.created_or_mod_by == 'system':
            try:
                if not self.pk:  # 新建持仓
                    p = Positions.objects.filter(
                        trader=self.trader.id, stock_code=self.stock_code, trade_account=self.trade_account, is_liquadated=False)
                    if p is not None and p.count() == 0:
                        if self.direction == 's':  # 卖出不能大于现有持仓（0）
                            return False  # 需要返回定义好的code
                        # 新建仓
                        p = Positions(market=self.market,
                                      stock_name=self.stock_name, stock_code=self.stock_code)
                        self.in_stock_positions = p
                    else:
                        # 增仓或者减仓
                        p = p[0]
                        self.in_stock_positions = p
                        if self.direction == 's' and self.board_lots > p.lots:  # 卖出不能大于现有持仓
                            return False  # 需要返回定义好的code
                    # 更新持仓信息后返回是否清仓
                    self.is_liquadated = p.update_transaction_position(  # update_stock_position(
                        self.direction, self.target_position,
                        self.board_lots, self.price, self.cash, self.trader, self.trade_account, self.trade_time)

                    if self.is_liquadated:
                        entries = TradeRec.objects.select_for_update().filter(
                            trader=self.trader, stock_code=self.stock_code, direction='b', is_liquadated=False,)
                        with transaction.atomic():
                            for entry in entries:
                                entry.is_liquadated = True
                                entry.save()

                    self.rec_ref_number = id_generator()
                    super().save(*args, **kwargs)
                else:
                    super().save()
            except Exception as e:
                logger.error(e)
        else:
            super().save()

        if self.direction == 's':  # 根据策略：FIFO/LIFO，卖出符合要求的仓位
            try:
                self.allocate_stock_for_sell()
            except Exception as e:
                logger.error(e)
        return True

    def allocate_stock_for_sell(self):
        # self 当前的卖出记录
        if settings.STOCK_OUT_STRATEGY == 'FIFO':  # 先进先出
            quantity_to_sell = self.board_lots
            recs = TradeRec.objects.filter(trader=self.trader, trade_account=self.trade_account, stock_code=self.stock_code, direction='b',
                                           lots_remain__gt=0, is_sold=False, is_liquadated=False,).exclude(created_or_mod_by='system').order_by('trade_time')
            for rec in recs:
                # 卖出时需要拷贝当前持仓，由系统system创建一条新的记录 -- 新建
                if quantity_to_sell > rec.lots_remain:
                    # 以前买入的股数不够卖，那该持仓全部卖出，
                    remain_shares = rec.lots_remain
                    quantity_to_sell -= rec.lots_remain
                    rec.lots_remain = 0
                    rec.sold_time = self.trade_time
                    rec.is_sold = True
                    rec.save()
                    # 需要拷贝当前持仓，由系统创建一条新的记录 -- 新建
                    new_sys_rec = rec  # ?? 需要新创建对象？？
                    new_sys_rec.pk = None
                    new_sys_rec.id = None
                    # new_sys_rec.is_sold = True
                    new_sys_rec.board_lots = remain_shares
                    new_sys_rec.created_or_mod_by = 'system'
                    new_sys_rec.sell_stock_refer = self
                    new_sys_rec.sell_price = self.price
                    # new_sys_rec.board_lots = quantity_to_sell
                    new_sys_rec.save()
                elif quantity_to_sell == rec.lots_remain:
                    # 以前买入的股数刚好等于卖出量，那该持仓全部卖出，
                    rec.lots_remain = 0
                    rec.sold_time = self.trade_time
                    rec.is_sold = True
                    rec.save()
                    # 因此需要拷贝当前持仓，由系统创建一条新的记录 -- 新建
                    new_sys_rec = rec
                    new_sys_rec.pk = None
                    new_sys_rec.id = None
                    # new_sys_rec.is_sold = True
                    new_sys_rec.board_lots = quantity_to_sell
                    new_sys_rec.created_or_mod_by = 'system'
                    new_sys_rec.sell_stock_refer = self
                    new_sys_rec.sell_price = self.price
                    new_sys_rec.save()
                    # allocate已有持仓，当前持仓已经满足卖出条件，需要卖出股数设置为0，退出循环。
                    quantity_to_sell = 0
                    break
                else:
                    # 已有持仓大于卖出股数，因此需要拷贝当前持仓，
                    # 原有持仓数量更新为卖出量
                    # 老的买入记录更新为卖出状态，--更新
                    rec.lots_remain -= quantity_to_sell
                    rec.save()
                    # 由系统创建一条新的记录 --新建
                    new_sys_rec = rec
                    new_sys_rec.pk = None
                    new_sys_rec.id = None
                    new_sys_rec.lots_remain = 0
                    new_sys_rec.is_sold = True
                    new_sys_rec.created_or_mod_by = 'system'
                    new_sys_rec.sell_stock_refer = self
                    new_sys_rec.sell_price = self.price
                    new_sys_rec.sold_time = self.trade_time
                    new_sys_rec.board_lots = quantity_to_sell
                    new_sys_rec.save()
                    # allocate已有持仓，当前持仓已经满足卖出条件，需要卖出设置为0，退出循环。
                    quantity_to_sell = 0
                    break
        elif settings.STOCK_OUT_STRATEGY == 'LIFO':  # 后进先出
            pass
        else:
            pass
# First, define the Manager subclass.


# 目前持有仓位数据model

class Positions(BaseModel):
    '''
    深交所和上海交易所的股票均需要收取过户费，过户费按成交股票金额的0.02%进行双向收取，即买入和卖出都需要收取。
    一般股票市场上的交易费由三部分组成，分别是佣金、印花税和过户费。
    1.印花税按卖出成交金额的0.1%进行单向收取；
    2.过户费按成交股票金额的0.02%进行双向收取；
    3.佣金按成交金额的0.01%~0.3%进行双向收取，佣金和券商经理进行协商，资金量和成交量都可以适当降低。不同的营业部的佣金比例不同。
    法律依据："《中华人民共和国证券法》第四十六条　证券交易的收费必须合理，并公开收费项目、收费标准和收费办法。
    证券交易的收费项目、收费标准和管理办法由国务院有关主管部门统一规定。"
    单位：元（人民币）
    '''
    MIN_TRANSFER_FEE = Decimal(1)  # 最少过户费
    # TRANSFER_FEE_PER_LOT = 0.1 #每100股0.1元
    TRANSFER_FEE_RATE = Decimal(0.0002)
    STAMP_TAX_RATE = Decimal(0.001)
    MIN_SERVICE_CHARGE = Decimal(5)

    market = models.CharField(
        _('股票市场'), max_length=10, blank=False, null=False)
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=False, null=False)
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False)
    trader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('持仓人'), blank=False, null=False,
                               on_delete=models.CASCADE)
    position_price = models.DecimalField(
        _('持仓价格'), max_digits=5, decimal_places=2, blank=False, null=False, default=0)
    current_price = models.DecimalField(
        _('股票现价'), max_digits=5, decimal_places=2, blank=False, null=False, default=0)
    profit = models.DecimalField(
        _('利润'), max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    profit_ratio = models.CharField(
        _('利润率'), max_length=100, blank=True, null=True)
    cash = models.DecimalField(
        _('投入现金额'), max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    lots = models.PositiveIntegerField(_('持仓'), default=0)
    target_position = models.PositiveIntegerField(
        _('目标仓位（股）'), blank=False, null=False, default=0)
    is_liquadated = models.BooleanField(
        _('是否清仓'), blank=False, null=False, default=False, db_index=True)
    trade_account = models.ForeignKey('TradeAccount', verbose_name=_(
        '交易账户'), on_delete=models.SET_NULL, blank=True, null=True)
    is_sychronized = models.BooleanField(
        _('是否同步'), blank=False, null=False, default=False)
    sychronized_datetime = models.DateTimeField(
        '同步时间', blank=True, null=True)
    # realtime_objects = PositionManager() # The position-specific manager.

    def __str__(self):
        return self.stock_name

    def make_profit_updated(self, realtime_quote=''):
        '''
        # 获得实时报价
        # ts_code = str(self.stock_code).split('.')[0]
        realtime_df = ts.get_realtime_quotes(self.stock_code)  # 需要再判断一下ts_code
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'time']]
        realtime_price = round(Decimal(realtime_df['price'].mean()), 2)
        self.current_price = realtime_price

        # 如果有现有仓位，计算实时持仓利润
        if self.lots != 0 and self.position_price != 0:
            self.profit = round(
                (realtime_price - self.position_price) * self.lots, 2)
        '''

        # 获得实时报价
        # ts_code = str(self.stock_code).split('.')[0]
        if not realtime_quote:
            realtime_df = ts.get_realtime_quotes(
                self.stock_code)  # 需要再判断一下ts_code
            realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                       'high', 'low', 'bid', 'ask', 'volume', 'amount', 'time']]
            realtime_price = round(Decimal(realtime_df['price'].mean()), 2)
            realtime_bid = round(Decimal(realtime_df['bid'].mean()), 2)
            realtime_pre_close = round(
                Decimal(realtime_df['pre_close'].mean()), 2)

            if realtime_price != Decimal(0.00):
                realtime_price = realtime_price
            elif realtime_bid != Decimal(0.00):
                realtime_price = realtime_bid
            else:
                realtime_price = realtime_pre_close
        else:
            realtime_price = realtime_quote

        if self.lots != 0 and self.position_price != 0:
            self.profit = (realtime_price - self.position_price) * self.lots
            self.profit_ratio = str(
                round((realtime_price - self.position_price) / self.position_price * 100, 2)) + '%'
            self.current_price = realtime_price
            self.save()

        return realtime_price

    def calculate_misc_fee(self, trade_account, direction, trade_lots, trade_price):
        amount = trade_lots * trade_price
        # 计算过户费
        transfer_fee = amount * Positions.TRANSFER_FEE_RATE
        if transfer_fee <= 1:
            transfer_fee = Positions.MIN_TRANSFER_FEE
        # 计算佣金
        service_charge = amount * Decimal(trade_account.service_charge)
        if service_charge <= 5:
            service_charge = Positions.MIN_SERVICE_CHARGE
        if direction == 'b':
            self.profit = self.profit - transfer_fee - service_charge
        elif direction == 's':
            # 计算印花税
            stamp_tax = amount * Positions.STAMP_TAX_RATE
            self.profit = self.profit - transfer_fee - service_charge - stamp_tax
        else:
            pass

    def calculate_misc_trade_fee(self, direction, trade_account, trade_lots, trade_price):
        misc_fee = 0
        # 交易额
        amount = trade_lots * trade_price
        # 计算过户费
        transfer_fee = amount * Positions.TRANSFER_FEE_RATE
        if transfer_fee <= 1:
            transfer_fee = Positions.MIN_TRANSFER_FEE
        # 计算佣金
        service_charge = amount * Decimal(trade_account.service_charge)
        if service_charge <= 5:
            service_charge = Positions.MIN_SERVICE_CHARGE
        # 计算净利润
        if direction == 'b':
            misc_fee = transfer_fee + service_charge
        elif direction == 's':
            # 计算印花税
            stamp_tax = amount * Positions.STAMP_TAX_RATE
            misc_fee = transfer_fee + service_charge + stamp_tax
        return misc_fee

    def get_realtime_quote(self, symbol):
        realtime_df = ts.get_realtime_quotes(symbol)  # 需要再判断一下ts_code
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'time']]
        realtime_price = round(Decimal(realtime_df['price'].mean()), 2)
        realtime_bid = round(Decimal(realtime_df['bid'].mean()), 2)
        realtime_pre_close = round(
            Decimal(realtime_df['pre_close'].mean()), 2)

        if realtime_price != Decimal(0.00):
            realtime_price = realtime_price
        elif realtime_bid != Decimal(0.00):
            realtime_price = realtime_bid
        else:
            realtime_price = realtime_pre_close
        return realtime_price

    def calibrate_realtime_position(self):
        '''
        非清仓股持仓成本和利润算法
        1. 获取当前实时报价
        2. 查询所有与该持仓相关的交易记录（除系统生成之外）
        3. 循环所有记录
        3.1 计算首次建仓
        3.2 计算买入
        3.3 计算卖出
        4. 用实时报价最后计算实时仓位利润

        1. 利润 = 原持仓利润 + (如果未收盘tushare取当前股票价格/收盘价c - 交易价格) * 本次交易量(手) * 100 (1手=100股)
        2. 持仓价格 =
        2.1 如果利润是(负-)的
            每手亏损 = 利润 / (已有持仓-卖出量(手)）
            持仓价格 = 当前股票价格：如果未收盘/收盘价 + 每手亏损
        2.2 如果利润是(正+)的
            每手利润 = 利润 / (已有持仓-卖出量(手)）
            持仓价格 = 当前股票价格：如果未收盘/收盘价 - 每手利润

        调用时需要判断是否已经synchronize，并且
        '''
        count = 0
        profit = Decimal()
        position_price = Decimal()
        # profit_margin = ''
        # trade_fee = Decimal()
        total_shares = 0
        realtime_quote = self.get_realtime_quote(self.stock_code)   
        if self.is_sychronized:
            transaction_recs = TradeRec.objects.filter(in_stock_positions=self.id, last_mod_time__gte=self.sychronized_datetime).exclude(
                    created_or_mod_by='system').order_by('trade_time')
        # 只有在有新交易后才会重新计算
        if not self.is_sychronized or (transaction_recs is not None and transaction_recs.count() > 0):
            transaction_recs = TradeRec.objects.filter(in_stock_positions=self.id).exclude(
                created_or_mod_by='system').order_by('trade_time')
            # 对所有之前买入的改股票交易，按照卖出价重新计算利润
            if transaction_recs is not None and transaction_recs.count() > 0:
                for transaction_rec in transaction_recs:
                    if count == 0:
                        # 首次建仓
                        if transaction_rec.direction == 'b':
                            profit -= self.calculate_misc_trade_fee(
                                'b', self.trade_account, transaction_rec.board_lots, transaction_rec.price)
                            total_shares = transaction_rec.board_lots
                            position_price = transaction_rec.price - profit / total_shares
                    else:
                        if transaction_rec.direction == 'b':
                            profit = (transaction_rec.price - position_price) * total_shares - self.calculate_misc_trade_fee(
                                'b', self.trade_account, transaction_rec.board_lots, transaction_rec.price)
                            total_shares += transaction_rec.board_lots
                            position_price = transaction_rec.price - profit / total_shares
                        elif transaction_rec.direction == 's':
                            profit = (transaction_rec.price - position_price) * total_shares - \
                                self.calculate_misc_trade_fee(
                                    's', self.trade_account, transaction_rec.board_lots, transaction_rec.price)
                            total_shares -= transaction_rec.board_lots
                            position_price = transaction_rec.price - profit / total_shares
                        else:
                            pass
                    count += 1
        # 重新计算持仓后，更新持仓价
        if count > 0:
            self.position_price = round(position_price, 2)
        # 根据实时报价更新持仓
        self.profit = round(
            (realtime_quote - self.position_price) * self.lots, 2)
        self.profit_ratio = str(round(self.profit / self.cash * 100, 2)) + '%'
        self.current_price = realtime_quote
        self.is_sychronized = True
        self.sychronized_datetime = datetime.now()
        self.save()
        pass

    def sync_position_realtime(self):
        realtime_quote = self.get_realtime_quote(self.stock_code)
        # 更新持仓利润、利润率和现价
        if self.lots != 0 and self.position_price != 0:
            self.position_price = realtime_quote - self.profit / self.lots
            # self.profit = (realtime_quote - self.position_price) * self.lots
            # self.profit_ratio = str(
            #     round(self.profit / self.cash * 100, 2)) + '%'
            self.current_price = realtime_quote

    # 持仓算法
    def update_transaction_position(self, trade_direction, target_position, trade_lots, trade_price, trade_cash, trader, trade_account, trade_time):
        '''
        1. 永远只能按照卖出时的价格，计算持仓利润，而不是最新价
        2. 持仓后，如果只是实时更新持仓利润，价格按照目前实时价格计算
        '''
        self.trader = trader
        self.target_position = target_position
        self.trade_account = trade_account
        if trade_direction == 'b':
            self.cash += trade_cash + \
                self.calculate_misc_trade_fee(
                    trade_direction, self.trade_account, trade_lots, trade_price)
            self.lots += trade_lots
            # self.update_buy_position(trade_direction, target_position,
            #                          trade_lots, trade_price, trade_cash, trader, trade_account)
        elif trade_direction == 's':
            self.lots -= trade_lots
            self.cash -= trade_cash
            if self.lots == 0:
                # 清仓，设置is_liquadated = True
                self.is_liquadated = True
                self.cash = 0
            # self.update_sell_position(trade_direction, target_position, trade_lots,
            #                           trade_price, trade_cash, trader, trade_account, trade_time)
            # self.sync_position_realtime()
        elif trade_direction == 'a':  # 仓位调整
            pass
        self.save()
        return self.is_liquadated

    # 持仓算法
    def update_stock_position(self, trade_direction, target_position, trade_lots, trade_price, trade_cash, trader, trade_account):
        '''
        1. 永远只能按照卖出时的价格，计算持仓利润，而不是最新价
        2. 持仓后，如果只是实时更新持仓利润，价格按照目前实时价格计算
        '''
        if trade_direction == 's':
            realtime_price = self.make_profit_updated(
                realtime_quote=trade_price)
        else:
            realtime_price = self.make_profit_updated()
        self.trader = trader
        self.target_position = target_position
        self.current_price = realtime_price
        self.trade_account = trade_account

        # 什么时候计算？
        # 持仓利润 = 原持仓利润 + (如果未收盘tushare取当前股票价格/收盘价c - 目前持仓价格) * 持仓数量(手) * 100 (1手=100股)

        if trade_direction == 's':  # 已有仓位卖出
            self.lots = self.lots - trade_lots
            self.cash = self.cash - trade_cash
            if self.lots == 0:
                # 清仓，设置is_liquadated = True
                self.is_liquadated = True
                self.cash = 0
        elif trade_direction == 'b':
            self.lots = self.lots + trade_lots
            self.cash = self.cash + trade_cash
            self.profit = round(self.profit +
                                (realtime_price - trade_price) * trade_lots, 2)
        elif trade_direction == 'a':
            pass
        # 计算手续费，印花税和过户费
        self.calculate_misc_fee(
            trade_account, trade_direction, trade_lots, trade_price)
        '''
        1. 利润 = 原持仓利润 + (如果未收盘tushare取当前股票价格/收盘价c - 交易价格) * 本次交易量(手) * 100 (1手=100股)
        2. 持仓价格 =
        2.1 如果利润是(负-)的
            每手亏损 = 利润 / (已有持仓-卖出量(手)）
            持仓价格 = 当前股票价格：如果未收盘/收盘价 + 每手亏损
        2.2 如果利润是(正+)的
            每手利润 = 利润 / (已有持仓-卖出量(手)）
            持仓价格 = 当前股票价格：如果未收盘/收盘价 - 每手利润
        '''
        if not self.is_liquadated:
            self.position_price = round(realtime_price - self.profit /
                                        self.lots, 2)
            self.profit_ratio = str(
                round((realtime_price - self.position_price) / self.position_price * 100, 2)) + '%'

            if trade_direction == 's':
                self.make_profit_updated()

        self.save()
        # 有持仓变化时更新当日持仓快照？？不确定是否需要在此时更新snapshot
        # snapshot = TradeProfitSnapshot.objects.filter(
        #     trader=trader, trade_account=trade_account, snap_date=date.today())
        # if snapshot is None or len(snapshot) == 0:
        #     new_snapshot = TradeProfitSnapshot(
        #         trader=trader, trade_account=trade_account, profit=self.profit, snap_date=date.today())
        #     new_snapshot.save()
        # else:
        #     # 更新快照持仓数量，利润，
        #     snapshot.lots = self.lots
        #     snapshot.profit = self.profit
        #     snapshot[0].save()
        return self.is_liquadated

    class Meta:
        ordering = ['stock_code']
        verbose_name = _('我的持仓')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class TradeSettings(BaseModel):

    SETTING_CHOICES = (
        ('TARGET_POSITION', _('目标仓位')),
        ('SERVICE_FEE', _('交易手续费')),
        ('STAMP_TAX', _('印花税')),
    )
    name = models.CharField(_('参数名'), choices=SETTING_CHOICES,
                            max_length=50, blank=False, null=False)
    value = models.CharField(_('参数值'), max_length=50, blank=False, null=False)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
                                on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']
        verbose_name = _('交易参数设置')
        verbose_name_plural = verbose_name


class TradeStrategy(BaseModel):
    PERIOD_CHOICE = {
        ('mm', _('月线')),
        ('wk', _('周线')),
        ('dd', _('日线')),
        ('60', _('60分钟')),
        ('30', _('30分钟')),
        ('15', _('15分钟')),
    }
    applied_period = models.CharField(
        _('应用周期'), choices=PERIOD_CHOICE, max_length=2, blank=True, null=False, default='60')
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
        ('ZB', _('主板')),
        ('ZXB', _('中小板')),
        ('CYB', _('创业板')),
        ('KCB', _('科创板')),

    )

    EXCHANGE_CHOICES = (
        ('SSE', _('上交所')),
        ('SZSE', _('深交所')),
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
    list_date = models.DateTimeField(
        _('上市日期'), default=now, blank=True, null=True)
    delist_date = models.DateTimeField(
        _('退市日期'), default=now, blank=True, null=True)
    is_hs = models.CharField(
        _('是否沪深港通标的'), choices=HS_CHOICES, max_length=10, blank=True, null=True)

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


class StockFollowing(BaseModel):
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False)
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=True, null=True)  # name e.g. 平安银行
    trader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('持仓人'), blank=False, null=False,
                               on_delete=models.CASCADE)
    is_following = models.BooleanField(
        _('是否关注'), blank=False, null=False, default=True)

    def __str__(self):
        return str(self.stock_code)

    class Meta:
        unique_together = ('stock_code', 'trader',)
        ordering = ['-last_mod_time']
        verbose_name = _('自选股票')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class TradeAccount(BaseModel):
    TRADE_PROVIDER_CHOICES = (
        ('htzq', _('华泰证券')),
        ('zszq', _('招商证券')),
        ('gfzq', _('广发证券')),
        ('swhy', _('申万宏源')),
        ('zygj', _('中银国际')),
    )

    trader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('持仓人'), blank=False, null=False,
                               on_delete=models.CASCADE)
    account_provider = models.CharField(
        _('开户证券公司'), choices=TRADE_PROVIDER_CHOICES, max_length=50, blank=True, null=True)
    account_type = models.CharField(
        _('账户类型'), max_length=50, blank=True, null=True)
    account_name = models.CharField(
        _('账户名称'), max_length=50, blank=False, null=False)
    account_capital = models.DecimalField(
        _('本金'), max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    account_balance = models.DecimalField(
        _('账户余额'), max_digits=10, decimal_places=2, blank=False, null=False, default=0)

    service_charge = models.DecimalField(
        _('交易手续费'), max_digits=10, decimal_places=10, blank=False, null=False, default=0.0005)
    activate_date = models.DateField(
        _('开户时间'), blank=False, null=False, default=now)
    is_valid = models.BooleanField(
        _('是否有效'), blank=False, null=False, default=True)
    is_default = models.BooleanField(
        _('默认账户'), blank=False, null=False, default=False)

    def __str__(self):
        return str(self.account_provider)

    def update_account_balance(self):
        account_profit_sum = Positions.objects.filter(
            trader=self.trader, trade_account=self).aggregate(sum_profit=Sum('profit'))
        if account_profit_sum['sum_profit'] is not None:
            self.account_balance = self.account_capital + \
                account_profit_sum['sum_profit']
            self.save()

    def save(self, *args, **kwargs):
        self.account_name = self.account_provider + self.account_type
        super().save()
        return self.id

    class Meta:
        ordering = ['-last_mod_time']
        unique_together = ('account_name', 'trader',)
        verbose_name = _('股票账户')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


# class InStockTransactionStrategy(BaseModel):
#     name = models.CharField(_('策略名'), max_length=30, unique=True)
#     creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
#                                 on_delete=models.CASCADE)

#     # slug = models.SlugField(default='no-slug', max_length=60, blank=True)

#     class Meta:
#         ordering = ['name']
#         verbose_name = _('持仓股卖出策略')
#         verbose_name_plural = verbose_name
class StockPositionSnapshot(BaseModel):
    """
    should run every day after 3:30pm, on trade date
    """
    PERIOD_CHOICE = {
        ('m', _('月')),
        ('w', _('周')),
        ('d', _('日')),
    }

    trader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('持仓人'), blank=False, null=False,
                               on_delete=models.CASCADE)
    trade_account = models.ForeignKey('TradeAccount', verbose_name=_('股票账户'), blank=False, null=False,
                                      on_delete=models.CASCADE)
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=False, null=False)
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False)
    profit = models.DecimalField(
        _('利润'), max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    profit_change = models.DecimalField(
        _('利润变化'), max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    profit_ratio = models.DecimalField(
        _('利润率'), max_digits=10, decimal_places=5, blank=False, null=False, default=0)
    snap_date = models.DateField(
        _('快照时间'), blank=False, null=False, default=now)
    applied_period = models.CharField(
        _('收益周期'), choices=PERIOD_CHOICE, max_length=1, blank=True, null=False, default='d')

    def __str__(self):
        return str(self.trade_account)


class TradeProfitSnapshot(BaseModel):
    """
    should run every day after 3:30pm, on trade date
    """
    PERIOD_CHOICE = {
        ('m', _('月')),
        ('w', _('周')),
        ('d', _('日')),
    }

    trader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('持仓人'), blank=False, null=False,
                               on_delete=models.CASCADE)
    trade_account = models.ForeignKey('TradeAccount', verbose_name=_('股票账户'), blank=False, null=False,
                                      on_delete=models.CASCADE)
    account_capital = models.DecimalField(
        _('本金'), max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    profit = models.DecimalField(
        _('利润'), max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    profit_change = models.DecimalField(
        _('利润变化'), max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    profit_ratio = models.DecimalField(
        _('利润率'), max_digits=10, decimal_places=5, blank=False, null=False, default=0)
    snap_date = models.DateField(
        _('快照时间'), blank=False, null=False, default=now)
    applied_period = models.CharField(
        _('收益周期'), choices=PERIOD_CHOICE, max_length=1, blank=True, null=False, default='d')

    def __str__(self):
        return str(self.trade_account)

    def take_account_snapshot(self):
        '''
        周一到周五，每天收盘后半小时，定时任务会call这个方法生成账户快照
        '''
        import calendar
        if self.snap_date.weekday() == calendar.SUNDAY:  # 当前是周日，前一snapshot day是上周五，往前推2天
            last_snap_date = self.snap_date - timedelta(days=2)
        elif self.snap_date.weekday() == calendar.MONDAY:  # 当前是周一，前一snapshot day是上周五，往前推三天
            last_snap_date = self.snap_date - timedelta(days=3)
        else:  # 周二到周六，前一snapshot day往前推一天
            last_snap_date = self.snap_date - timedelta(days=1)
        # 更新
        self.trader = self.trade_account.trader
        self.profit = self.trade_account.account_balance - \
            self.trade_account.account_capital
        self.profit_ratio = round(
            (self.trade_account.account_balance - self.trade_account.account_capital) / self.trade_account.account_capital, 2)
        self.account_capital = self.trade_account.account_capital
        # 与上一snapshot day环比的变化
        last_snapshot = TradeProfitSnapshot.objects.filter(
            trade_account=self.trade_account, snap_date=last_snap_date, applied_period='d')
        if last_snapshot is not None and len(last_snapshot) >= 1:
            self.profit_change = self.profit - last_snapshot[0].profit
        else:
            self.profit_change = self.profit
        self.applied_period = 'd'
        self.save()
        # 如果是周五，需要多生成一条周'w'快照
        if self.snap_date.weekday() == calendar.FRIDAY:
            last_friday = self.snap_date - timedelta(days=7)  # 前一周周五
            relative_snapshot = TradeProfitSnapshot.objects.filter(
                trader=self.trader, trade_account=self.trade_account, snap_date=last_friday, applied_period='w')
            if relative_snapshot is not None and len(relative_snapshot) >= 1:
                profit_change = self.profit - relative_snapshot.profit
            else:
                profit_change = self.profit
            week_snapshot = TradeProfitSnapshot(
                trader=self.trader, trade_account=self.trade_account,
                profit=self.profit, profit_change=profit_change, profit_ratio=self.profit_ratio,
                account_capital=self.account_capital, applied_period='w')
            week_snapshot.save()
        # 如果每月最后一天，需要多生成一条月'm'快照
        mon_range = calendar.monthrange(
            self.snap_date.year, self.snap_date.month)
        last_day = date(self.snap_date.year,
                        self.snap_date.month, mon_range[1])
        if self.snap_date == last_day:
            year = self.snap_date.year
            month = self.snap_date.month
            if month == 1:
                last_year = year - 1
                last_mon = 12
            else:
                last_year = year
                last_mon = month - 1
            relative_snapshot = TradeProfitSnapshot.objects.filter(
                trader=self.trader, trade_account=self.trade_account,
                snap_date__year=last_year, snap_date__month=last_mon, applied_period='m')
            if relative_snapshot is not None and len(relative_snapshot) >= 1:
                profit_change = self.profit - relative_snapshot.profit
            else:
                profit_change = self.profit
            last_day = self.snap_date - timedelta(days=7)  # 前一周周五
            mon_snapshot = TradeProfitSnapshot(
                trader=self.trader, trade_account=self.trade_account,
                profit=self.profit, profit_change=profit_change, profit_ratio=self.profit_ratio,
                account_capital=self.account_capital, applied_period='m')
            mon_snapshot.save()

    def update_snapshot(self):
        pass

    def take_snapshot_job(self, snapshot_date):
        from users.models import User
        users = User.objects.filter(is_active=True)
        if users is not None and len(users) > 0:
            for user in users:
                positions = Positions.objects.filter(
                    trader=user, is_liquadated=False)
                if positions is not None and len(positions) >= 1:
                    for position in positions:
                        self.take_snapshot(position, self.applied_period)

    def take_snapshot(self, position, applied_period):
        snap_date = self.snap_date
        if snap_date.weekday() == 6:  # 周日推2天
            last_snap_date = snap_date - timedelta(days=2)
        elif snap_date.weekday() == 0:  # 周一
            last_snap_date = snap_date - timedelta(days=3)
        else:  # 周二到周六其他的往前推一天
            last_snap_date = snap_date - timedelta(days=1)
        # 上一个交易日的snapshot
        last_snapshot = TradeProfitSnapshot.objects.filter(
            trade_account=position['trade_account'], snap_date=last_snap_date)
        if last_snapshot is not None and len(last_snapshot) >= 1:
            self.profit_change = position['sum_profit'] - \
                last_snapshot[0].profit
        else:
            self.profit_change = position['sum_profit']
        # self.trader = trader
        trade_account = TradeAccount.objects.get(id=position['trade_account'])
        self.profit = position['sum_profit']
        self.profit_ratio = round(
            position['sum_profit'] / trade_account.account_capital, 5)
        self.applied_period = applied_period
        self.save()

    class Meta:
        ordering = ['-last_mod_time']
        verbose_name = _('收益快照')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class StockPositionTransaction(BaseModel):
    TRANS_TYPE = (
        ('b', _('买入')),
        ('s', _('卖出')),
        ('a', _('调整')),
    )
    trader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('持仓人'), blank=False, null=False,
                               on_delete=models.CASCADE)
    account_name = models.ForeignKey('TradeAccount', verbose_name=_('股票账户'), blank=False, null=False,
                                     on_delete=models.CASCADE)
    stock_name = models.CharField(
        _('股票名称'), max_length=50, blank=False, null=False)
    stock_code = models.CharField(
        _('股票代码'), max_length=50, blank=False, null=False)
    transaction_type = models.CharField(_('交易类型'), max_length=1,
                                        choices=TRANS_TYPE, default='b')
    # 交易日期
    trade_time = models.DateTimeField(
        '交易时间', default=now, blank=False, null=False)
    price = models.DecimalField(
        _('交易价格'), max_digits=5, decimal_places=2, blank=False, null=False)
    current_price = models.DecimalField(
        _('股票现价'), max_digits=5, decimal_places=2, blank=False, null=False, default=0)
    stock_positions = models.ForeignKey('Positions', verbose_name=_('股票持仓'), blank=False, null=True,
                                        on_delete=models.CASCADE, editable=False)
    from_lot = models.PositiveIntegerField(
        _('初始持仓（股）'), default=100)
    to_lot = models.PositiveIntegerField(
        _('交易后持仓（股）'), default=100)
    created_by = models.CharField(
        _('创建人'), max_length=50, blank=False, null=False, editable=False, default='system')

    def __str__(self):
        return str(self.account_name)
