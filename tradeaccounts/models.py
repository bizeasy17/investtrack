import logging
import random
import string
from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytz
import tushare as ts
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Sum
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

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


class TradeAccount(BaseModel):
    '''
    虚拟交易账户
    '''
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
        # bug, if none type of provider
        self.account_name = self.account_provider + self.account_type
        super().save()
        return self.id

    class Meta:
        ordering = ['-last_mod_time']
        unique_together = ('account_name', 'trader',)
        verbose_name = _('股票账户')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


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
    is_liquidated = models.BooleanField(
        _('是否清仓'), blank=False, null=False, default=False, db_index=True)
    trade_account = models.ForeignKey('TradeAccount', verbose_name=_(
        '交易账户'), on_delete=models.SET_NULL, blank=True, null=True)
    is_sychronized = models.BooleanField(
        _('是否同步'), blank=False, null=False, default=False)
    sychronized_datetime = models.DateTimeField(
        '同步时间', blank=True, null=True)
    # first transaction datetime
    ftd = models.DateTimeField(
        '建仓时间', blank=True, null=True)
    # last transaction datetime
    ltd = models.DateTimeField(
        '清仓时间', blank=True, null=True)
    # last transaction datetime
    target_chg_pct = models.DecimalField(
        '目标涨幅%', max_digits=2, decimal_places=2, blank=True, null=True, default=20)
    # realtime_objects = PositionManager() # The position-specific manager.

    def __str__(self):
        return self.stock_name

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
                self.is_liquidated = True
                if trade_time.tzinfo is None and trade_time.tzinfo.utcoffset(trade_time) is None:
                    cn_tz = pytz.timezone("Asia/Shanghai")
                    self.ltd = cn_tz.localize(trade_time)  # 清仓时间
                else:
                    self.ltd = trade_time  # 清仓时间
                self.cash = 0
            # self.update_sell_position(trade_direction, target_position, trade_lots,
            #                           trade_price, trade_cash, trader, trade_account, trade_time)
            # self.sync_position_realtime()
        elif trade_direction == 'a':  # 仓位调整
            pass
        self.save()
        return self.is_liquidated

    class Meta:
        ordering = ['stock_code']
        verbose_name = _('我的持仓')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class TradeAccountSnapshot(BaseModel):
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
        last_snapshot = TradeAccountSnapshot.objects.filter(
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
            relative_snapshot = TradeAccountSnapshot.objects.filter(
                trader=self.trader, trade_account=self.trade_account, snap_date=last_friday, applied_period='w')
            if relative_snapshot is not None and len(relative_snapshot) >= 1:
                profit_change = self.profit - relative_snapshot[0].profit
            else:
                profit_change = self.profit
            week_snapshot = TradeAccountSnapshot(
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
            relative_snapshot = TradeAccountSnapshot.objects.filter(
                trader=self.trader, trade_account=self.trade_account,
                snap_date__year=last_year, snap_date__month=last_mon, applied_period='m')
            if relative_snapshot is not None and len(relative_snapshot) >= 1:
                profit_change = self.profit - relative_snapshot[0].profit
            else:
                profit_change = self.profit
            last_day = self.snap_date - timedelta(days=7)  # 前一周周五
            mon_snapshot = TradeAccountSnapshot(
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
                    trader=user, is_liquidated=False)
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
        last_snapshot = TradeAccountSnapshot.objects.filter(
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
