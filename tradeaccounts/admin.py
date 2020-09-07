
# Register your models here.
from django.contrib import admin

from tradeaccounts.models import Positions, TradeAccount, TradeAccountSnapshot, StockPositionSnapshot

# Register your models here.


class TradeAccountAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')
    list_display = (
        'trader', 'account_name', 'account_provider', 'account_capital')


class PositionsAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('stock_name', 'stock_code')
    list_display = (
        'trader', 'stock_name', 'stock_code', 'position_price', 'current_price', 'profit', 'lots', 'target_position', 'is_liquidated', 'last_mod_time')
    ordering = ('-last_mod_time',)
    list_display_links = ('stock_name', 'stock_code')
    exclude = ('created_time', 'last_mod_time')


class TradeAccountSnapshotAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')
    list_display = (
        'trader', 'trade_account', 'profit', 'profit_ratio', 'snap_date')


class StockPositionSnapshotAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')
    list_display = (
        'trader', 'trade_account', 'profit', 'profit_ratio', 'target_chg_pct', 'snap_date')


# Register your models here.
admin.site.register(Positions, PositionsAdmin)
admin.site.register(TradeAccount, TradeAccountAdmin)
admin.site.register(TradeAccountSnapshot, TradeAccountSnapshotAdmin)
admin.site.register(StockPositionSnapshot, StockPositionSnapshotAdmin)
