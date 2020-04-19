from abc import ABCMeta, abstractmethod, abstractproperty

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
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

    class Meta:
        ordering = ['name']
        verbose_name = _('交易策略')
        verbose_name_plural = verbose_name

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


class User(AbstractUser):
    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField(_("姓名"), blank=True, max_length=255)
    picture = models.ImageField(
        _('个人头像'), upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(
        _('所在地区'), max_length=50, null=True, blank=True)
    job_title = models.CharField(
        _('头衔'), max_length=50, null=True, blank=True)
    personal_url = models.URLField(
        _('个人网址'), max_length=555, blank=True, null=True)
    linkedin_account = models.URLField(
        _('LinkedIn账号'), max_length=255, blank=True, null=True)
    weibo_account = models.URLField(
        _('Weibo账号'), max_length=255, blank=True, null=True)
    weixin_account = models.URLField(
        _('Weixin账号'), max_length=255, blank=True, null=True)
    qq_account = models.URLField(
        _('QQ账号'), max_length=255, blank=True, null=True)
    short_bio = models.CharField(
        _('描述下你自己'), max_length=60, blank=True, null=True)
    bio = models.CharField(
        _('个人简介'), max_length=280, blank=True, null=True)

    # trade_account = models.ForeignKey('TradeAccount', verbose_name=_(
    #     '交易账户'), on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def get_profile_name(self):
        if self.name:
            return self.name

        return self.username
