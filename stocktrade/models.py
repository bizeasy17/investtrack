from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from tradeaccounts.models import Positions, TradeAccount
from investors.models import TradeStrategy
# Create your models here.


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
    is_liquadated = models.BooleanField(
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
        verbose_name = _('交易记录')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
