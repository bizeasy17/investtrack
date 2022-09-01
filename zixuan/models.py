from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

# Create your models here.


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField(_('创建时间'), default=now)
    last_mod_time = models.DateTimeField(_('更新时间'), default=now)

    class Meta:
        abstract = True

class BuySellStrategy(BaseModel):
    strategy_code = models.CharField(
        _('策略代码'), max_length=25, blank=False, null=False, db_index=True)
    strategy_name = models.CharField(
        _('策略名称'), max_length=25, blank=False, null=False)
    type = models.CharField(
        _('策略类型'), max_length=5, blank=False, null=False, default='D')

    class Meta:
        ordering = ['strategy_code']
        verbose_name = _('买卖策略')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.strategy_code
