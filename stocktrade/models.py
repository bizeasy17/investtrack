import logging
import pytz
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import models, transaction


from tradeaccounts.models import Positions, TradeAccount
from investtrack import utils
from investors.models import TradeStrategy

# Create your models here.
logger = logging.getLogger(__name__)
cn_tz = pytz.timezone('Asia/Shanghai')

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(_('创建时间'), default=now)
    last_mod_time = models.DateTimeField(_('最后更新时间'), default=now)

    class Meta:
        abstract = True


class Transactions(BaseModel):
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
    trader = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('投资人'), blank=False, null=False,
                               on_delete=models.CASCADE)
    strategy = models.ForeignKey(
        TradeStrategy, verbose_name=_('策略'), on_delete=models.SET_NULL, blank=True, null=True)
    # tags = models.ManyToManyField('Tag', verbose_name=_('标签集合'), blank=True)
    in_stock_positions = models.ForeignKey(Positions, verbose_name=_('股票持仓'), blank=False, null=True,
                                           on_delete=models.CASCADE, editable=False)
    is_liquidated = models.BooleanField(
        _('是否已清仓'), blank=False, null=False, default=False, editable=False)
    trade_account = models.ForeignKey(
        TradeAccount, verbose_name=_('交易账户'), on_delete=models.SET_NULL, blank=True, null=True)
    rec_ref_number = models.CharField(
        _('买入记录编号'), max_length=10, blank=True, null=True)
    sell_stock_refer = models.ForeignKey(
        'self', verbose_name=_('卖对应之买入'), on_delete=models.SET_NULL, blank=True, null=True)
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
        verbose_name = _('交易明细')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def save(self, *args, **kwargs):
        '''
        生成交易记录
        在生成卖出交易时，会由系统自动按照FIFO的方式来匹配买入的股票仓位。先买入的先被卖出（已实现）。
        由系统生成的交易记录标记为system
        后买入的交易，先卖出的逻辑目前未实现。
        '''
        if not self.created_or_mod_by == 'system':
            try:
                if not self.pk:  # 新建持仓
                    p = Positions.objects.filter(
                        trader=self.trader.id, stock_code=self.stock_code, trade_account=self.trade_account, is_liquidated=False)
                    if p is not None and p.count() == 0:
                        if self.direction == 's':  # 卖出不能大于现有持仓（0）
                            return False  # 需要返回定义好的code
                        # 新建仓
                        p = Positions(market=self.market,
                                      stock_name=self.stock_name, stock_code=self.stock_code)
                        if self.trade_time.tzinfo is None and self.trade_time.tzinfo.utcoffset(self.trade_time) is None:
                            cn_tz = pytz.timezone('Asia/Shanghai')
                            p.ftd = cn_tz.localize(self.trade_time) # 建仓时间
                        else:
                            p.ftd = self.trade_time  # 建仓时间
                        self.in_stock_positions = p
                    else:
                        # 增仓或者减仓
                        p = p[0]
                        self.in_stock_positions = p
                        if self.direction == 's' and self.board_lots > p.lots:  # 卖出不能大于现有持仓
                            return False  # 需要返回定义好的code
                    # 根据策略：FIFO/LIFO，卖出符合要求的仓位
                    sys_alloc_list = []
                    if self.direction == 's':  
                        try:
                            sys_alloc_list = self.allocate_stock_for_sell()
                        except Exception as e:
                            logger.error(e)
                    # 更新持仓信息后返回是否清仓
                    self.is_liquidated = p.update_transaction_position(  # update_stock_position(
                        self.direction, self.target_position,
                        self.board_lots, self.price, self.cash, self.trader, self.trade_account, self.trade_time)

                    if self.is_liquidated:
                        stock_transactions = Transactions.objects.select_for_update().filter(
                            trader=self.trader, stock_code=self.stock_code, direction='b', is_liquidated=False,)
                        with transaction.atomic():
                            for entry in stock_transactions:
                                entry.is_liquidated = True
                                entry.save()

                    self.rec_ref_number = utils.id_generator()
                    super().save(*args, **kwargs)
                    # 由于原有买入记录在引用卖出交易时，FK需要先save，所以将system交易记录的save放在这之后
                    if sys_alloc_list is not None and len(sys_alloc_list) > 0:
                        for sys_gen_item in sys_alloc_list:
                            sys_gen_item.save()
                else:
                    super().save()
            except Exception as e:
                logger.error(e)
        else:
            super().save()
        return True

    def allocate_stock_for_sell(self):
        # self 当前的卖出记录
        if settings.STOCK_OUT_STRATEGY == 'FIFO':  # 先进先出
            system_gen_recs = []
            quantity_to_sell = self.board_lots
            recs = Transactions.objects.filter(trader=self.trader, trade_account=self.trade_account, stock_code=self.stock_code, direction='b',
                                           lots_remain__gt=0, is_sold=False, is_liquidated=False,).exclude(created_or_mod_by='system').order_by('trade_time')
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
                    # new_sys_rec.save()
                    system_gen_recs.append(new_sys_rec)
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
                    # new_sys_rec.save()
                    system_gen_recs.append(new_sys_rec)
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
                    # new_sys_rec.save()
                    system_gen_recs.append(new_sys_rec)
                    # allocate已有持仓，当前持仓已经满足卖出条件，需要卖出设置为0，退出循环。
                    quantity_to_sell = 0
                    break
        elif settings.STOCK_OUT_STRATEGY == 'LIFO':  # 后进先出
            pass
        else:
            pass
        return system_gen_recs
# First, define the Manager subclass.
