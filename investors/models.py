from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
# Create your models here.


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(_('创建时间'), default=now)
    last_mod_time = models.DateTimeField(_('最后更新时间'), default=now)

    class Meta:
        abstract = True

# class StrategyCategory(BaseModel):
#     '''
#     1. 策略分类 （I)
#         建仓 - Open a Position - O
#         增仓 - Increase a Position - I
#         减仓 - Reduce a Position - R
#         清仓 - Liquidate - L
#         持仓 - Hold a Position - H
#     '''
#     name = models.CharField(_('分类名称'), max_length=30,
#                             blank=False, null=False, default='')
#     category_code = models.CharField(
#         _('分类编号'), max_length=25, blank=False, null=False, default='')
#     creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
#                                 on_delete=models.CASCADE)

#     class Meta:
#         verbose_name = _('策略分类')
#         verbose_name_plural = verbose_name
#     pass

class StrategyAnalysisCode(BaseModel):
    '''
    2. 交易策略 （II)
        建仓 - Open a Position - O
            九转买点 - jiuzhuan_b > O, I
            双底 - shuangdi > O, I
        增仓 - Increase a Position - I
            九转买点 - jiuzhuan_b > O, I
            MA25支撑 - ma25_zhicheng > O, I
        减仓 - Reduce a Position - R
            九转卖点 - jiuzhuan_s > R, L
            MA25跌破 - zhicheng_ma25 > R, L
            下跌% - xiadie% > R, L
        清仓 - Liquidate - L
            九转卖点 - jiuzhuan_s > R, L
            MA25跌破- zhicheng_ma25 > R, L
            下跌% - xiadie% > R, L
        持仓 - Hold a Position - H

        压力位 - tupo > O, I
        支撑位 - diepo > R, L
    '''
    name = models.CharField(_('代码名称'), max_length=30,
                            blank=False, null=False, default='')
    analysis_code = models.CharField(
        _('代码编号'), max_length=25, blank=False, null=False, default='')
    category = models.CharField(
        _('策略分类'), max_length=50, blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
                                on_delete=models.CASCADE)

    class Meta:
        ordering = ['analysis_code']
        verbose_name = _('策略分析代码')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
#     pass

class TradeStrategy(BaseModel):
    '''
    Option 1. 策略分类 （I)
        建仓 - Open a Position - O
        增仓 - Increase a Position - I
        减仓 - Reduce a Position - R
        清仓 - Liquidate - L
        持仓 - Hold a Position - H
    Option 2. 策略分类 （I)
        买 - Buy Stock - B
        卖 - Sell Stock - S
        持 - Hold a Position - H
    '''
    ST_CODE_CHOICES = {
        ('B', _('买')),
        ('S', _('卖')),
        ('H', _('持仓')),
        # ('sell', _('卖出')),
        # ('stop_loss', _('止损')),
        # ('take_profit', _('止盈')),
        # ('liquidation', _('平仓/清仓')),
        # ('jiuzhuan_b', _('九转序列买点')),
        # ('jiuzhuan_s', _('九转序列卖点')),
        # ('shuangdi_b', _('双底买点')),
        # ('shuangtou_s', _('双头卖点')),
        # ('tupo_b', _('突破阻力位')),
        # ('diepo_s', _('跌破支撑位')),
        # ('ma25_b', _('MA25支撑位')),
    }

    PERIOD_CHOICE = {
        ('M', _('月线')),
        ('W', _('周线')),
        ('D', _('日线')),
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
    category = models.CharField(
        _('策略分类'), choices=ST_CODE_CHOICES, max_length=50, blank=True, null=True)
    ana_code = models.ForeignKey('StrategyAnalysisCode',
                                      verbose_name=_('分析代码'), blank=True, null=True, on_delete=models.SET_NULL)
    # analysis_category = models.ForeignKey('StrategyCategory',
    #                               verbose_name=_('分析代码'), blank=True, null=True, on_delete=models.SET_NULL)

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
                strategy_freq.category = self.category
                strategy_freq.ana_code = self.ana_code
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
    ts_code = models.CharField(
        _('TS代码'), max_length=50, blank=True, null=False)  # e.g. 000001.SZ
    area = models.CharField(_('所在地域'), max_length=50,
                            blank=True, null=True)
    industry = models.CharField(
        _('所属行业'), max_length=50, blank=True, null=True)
    fullname = models.CharField(
        _('股票全称'), max_length=100, blank=True, null=True)
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
