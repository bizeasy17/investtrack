import logging
from abc import ABCMeta, abstractmethod, abstractproperty

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.timezone import now
from django.conf import settings


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
    lots = models.PositiveIntegerField(_('交易量(手)'), default=100)
    cash = models.FloatField(_('投入现金额'), blank=True, null=True)
    position = models.CharField(
        _('交易仓位'), max_length=50, blank=False, null=False)
    visible = models.CharField(_('可见性'), max_length=1,
                               choices=VISIBLE_CHOICES, default='s')
    comment_status = models.CharField(
        _('评论状态'), max_length=1, choices=COMMENT_STATUS, default='c')
    views = models.PositiveIntegerField(_('浏览量'), default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('创建者'), blank=False, null=False,
                               on_delete=models.CASCADE)
    strategy = models.ForeignKey(
        'TradeStrategy', verbose_name=_('策略'), on_delete=models.SET_NULL, blank=True, null=True)
    # tags = models.ManyToManyField('Tag', verbose_name=_('标签集合'), blank=True)
    featured_image = models.ImageField(
        _('特色图片'), upload_to='investmgr_pictures/%Y/%m/%d/', blank=True, null=True)
    stock_positions_master = models.ForeignKey('Positions', verbose_name=_('股票持仓'), blank=False, null=True,
                                               on_delete=models.CASCADE)
    is_deleted = models.CharField(
        _('是否被删除'), max_length=1, blank=False, null=False, default='n', editable=False)

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
        
