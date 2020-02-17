import tushare as ts
# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .forms import TradeRecAdminForm
from .models import (Positions, StockFollowing, StockNameCodeMap, TradeRec,
                     TradeSettings, TradeStrategy, TradeAccount, TradeProfitSnapshot)

# Register your models here.


class TradeRecListFilter(admin.SimpleListFilter):
    title = _('交易者')
    parameter_name = 'trader'

    def lookups(self, request, model_admin):
        traders = list(set(map(lambda x: x.trader, TradeRec.objects.all())))
        for trader in traders:
            yield (trader.id, _(trader.username))

    def queryset(self, request, queryset):
        id = self.value()
        if id:
            return queryset.filter(trader__id__exact=id)
        else:
            return queryset


class TradeRecAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('stock_name', 'stock_code')
    list_display = (
        'trader', 'stock_name', 'stock_code', 'direction', 'price', 'board_lots', 'current_price', 'is_liquadated', 'created_time')
    list_display_links = ('stock_name', 'stock_code')
    list_filter = (TradeRecListFilter, 'strategy')
    exclude = ('created_time', 'last_mod_time')

    form = TradeRecAdminForm

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super(TradeRecAdmin, self).get_form(request, *args, **kwargs)
        setting_target_position = TradeSettings.objects.filter(
            creator=request.user.id, name='TARGET_POSITION')
        if setting_target_position.count() > 0:
            form.base_fields['target_position'].initial = setting_target_position[0].value
        return form


class StrategyAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')


class TradeSettingsAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')


# class TradePositionAdmin(admin.ModelAdmin):
#     exclude = ('last_mod_time', 'created_time')


class StockNameCodeMapAdmin(admin.ModelAdmin):
    list_display = (
        'stock_name', 'stock_code', 'ts_code', 'exchange', 'market', 'area', 'industry', 'list_status', 'list_date', 'delist_date', 'is_hs')

    exclude = ('last_mod_time', 'created_time')


class StockFollowingAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')


class TradeAccountAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')
    list_display = (
        'trader', 'account_name', 'account_provider', 'account_capital')


class PositionsAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('stock_name', 'stock_code')
    list_display = (
        'trader', 'stock_name', 'stock_code', 'position_price', 'current_price', 'profit', 'lots', 'target_position', 'is_liquadated', 'last_mod_time')
    ordering = ('-last_mod_time',)
    list_display_links = ('stock_name', 'stock_code')
    exclude = ('created_time', 'last_mod_time')


class TradeSnapshotAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')
    list_display = (
        'trader', 'account_name', 'profit', 'profit_ratio', 'snap_date')


# Register your models here.
admin.site.register(TradeRec, TradeRecAdmin)
admin.site.register(TradeStrategy, StrategyAdmin)
admin.site.register(TradeSettings, TradeSettingsAdmin)
admin.site.register(StockNameCodeMap, StockNameCodeMapAdmin)
admin.site.register(Positions, PositionsAdmin)
admin.site.register(StockFollowing, StockFollowingAdmin)
admin.site.register(TradeAccount, TradeAccountAdmin)
admin.site.register(TradeProfitSnapshot, TradeSnapshotAdmin)
