from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(_('创建时间'), default=now)
    last_mod_time = models.DateTimeField(_('最后更新时间'), default=now)

    class Meta:
        abstract = True


class TradeStrategy(BaseModel):
    ST_CODE_CHOICES = {
        ('jiuzhuan_b', _('九转序列买点')),
        ('jiuzhuan_s', _('九转序列卖点')),
        ('shuangdi_b', _('双底买点')),
        ('shuangtou_s', _('双头卖点')),
        ('break_through', _('突破阻力位')),
        ('fall_below', _('跌破支撑位')),
        ('buy', _('买入')),
        ('sell', _('卖出')),
        ('add_positions', _('加仓')),
        ('stop_loss', _('止损')),
        ('take_profit', _('止盈')),
    }

    PERIOD_CHOICE = {
        ('mm', _('月线')),
        ('wk', _('周线')),
        ('dd', _('日线')),
        ('60', _('60分钟')),
        ('30', _('30分钟')),
        ('15', _('15分钟')),
    }
    applied_period = models.CharField(
        _('应用周期'), choices=PERIOD_CHOICE, max_length=2, blank=True, null=True, default='60')
    name = models.CharField(_('策略名'), max_length=30)
    parent_strategy = models.ForeignKey(
        'self', verbose_name=_('父级策略'), blank=True, null=True, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
                                on_delete=models.CASCADE)
    is_visible = models.BooleanField(
        _('是否可见'), blank=False, null=False, default=False)
    code = models.CharField(
        _('策略代码'), choices=ST_CODE_CHOICES, max_length=50, blank=False, null=False, default='buy')
    is_manual = models.BooleanField(
        _('手工创建？'), blank=True, null=True, default=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('交易策略')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        '''
        将生成的策略拷贝到不同时间周期
        '''
        super().save()
        if self.is_manual:
            freq_list = ['60','D','W','M']
            for freq in freq_list:
                strategy_freq = TradeStrategy()
                strategy_freq.applied_period = freq
                strategy_freq.name = self.name + '(' + freq + ')'
                strategy_freq.parent_strategy = self
                strategy_freq.creator = self.creator
                strategy_freq.code = self.code
                strategy_freq.is_manual = False
                strategy_freq.save()
        pass

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
