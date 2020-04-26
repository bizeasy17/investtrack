from django.contrib import admin

from investors.models import StockFollowing, TradeStrategy

# Register your models here.


class StrategyAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')

class StockFollowingAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')


# Register your models here.
admin.site.register(TradeStrategy, StrategyAdmin)
admin.site.register(StockFollowing, StockFollowingAdmin)
