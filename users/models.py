from abc import ABCMeta, abstractmethod, abstractproperty

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
# from django.utils.translation import ugettext_lazy as _ depreciated in Django 4.0
from django.utils.translation import gettext_lazy as _



class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(_('创建时间'), default=now)
    last_mod_time = models.DateTimeField(_('更新时间'), default=now)

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass

# Create your models here.


class User(AbstractUser):
    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField(_('姓名'), blank=True, max_length=255)
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

    class Meta:
        verbose_name = _('网站用户')


# Create your models here.
class UserActionTrace(BaseModel):
    # First Name and Last Name do not cover name patterns around the globe.
    action_name = models.CharField(_('操作名称'), blank=True, max_length=255)
    request_url = models.CharField(_('请求的url'), blank=True, max_length=255)
    ip_addr = models.CharField(
        _('访问ip'), max_length=50, null=True, blank=True)
    uid = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('用户id'), blank=True, null=True,
                            on_delete=models.CASCADE)

# Create your models here.


class UserQueryTrace(BaseModel):
    # First Name and Last Name do not cover name patterns around the globe.
    query_string = models.CharField(_('查询内容'), blank=True, max_length=255)
    request_url = models.CharField(_('请求的url'), blank=True, max_length=255)
    ip_addr = models.CharField(
        _('访问ip'), max_length=50, null=True, blank=True)
    uid = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('用户id'), blank=True, null=True,
                            on_delete=models.CASCADE)


class UserBackTestTrace(BaseModel):
    # First Name and Last Name do not cover name patterns around the globe.
    ts_code = models.CharField(_('股票代码'), blank=True, max_length=255)
    strategy_code = models.CharField(_('策略代码'), blank=True, max_length=255)
    btest_type = models.CharField(_('回测类型'), blank=True, max_length=255)
    btest_param = models.CharField(_('回测参数'), blank=True, max_length=255)
    request_url = models.CharField(_('请求的url'), blank=True, max_length=255)
    ip_addr = models.CharField(
        _('访问ip'), max_length=50, null=True, blank=True)
    uid = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('用户id'), blank=True, null=True,
                            on_delete=models.CASCADE)


class UserBackTestFilterTrace(BaseModel):
    # First Name and Last Name do not cover name patterns around the globe.
    ts_code = models.CharField(_('股票代码'), blank=True, max_length=255)
    backtest_id = models.ForeignKey(
        UserBackTestTrace, verbose_name=_('回测id'), blank=False, null=False,
        on_delete=models.DO_NOTHING)
    filter_category = models.CharField(_('过滤器类别'), blank=True, max_length=255)
    filter_name = models.CharField(_('过滤器名称'), blank=True, max_length=255)
    filter_val = models.CharField(_('过滤器值'), blank=True, max_length=255)
    uid = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('用户id'), blank=True, null=True,
                            on_delete=models.CASCADE)
