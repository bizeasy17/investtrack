from django.contrib import admin
from .models import TradeRec, TradeStrategy, Positions, StockNameCodeMap

# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import TradeRec, TradeStrategy, Positions, StockNameCodeMap

# Register your models here.
class TradeRecListFilter(admin.SimpleListFilter):
    title = _('交易者')
    parameter_name = 'trader'

    def lookups(self, request, model_admin):
        authors = list(set(map(lambda x: x.author, TradeRec.objects.all())))
        for author in authors:
            yield (author.id, _(author.username))

    def queryset(self, request, queryset):
        id = self.value()
        if id:
            return queryset.filter(author__id__exact=id)
        else:
            return queryset

class TradeRecAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('stock_name', 'stock_code')
    list_display = (
        'trader', 'stock_name', 'stock_code', 'direction', 'price', 'created_time')
    list_display_links = ('stock_name', 'stock_code')
    list_filter = (TradeRecListFilter, 'strategy')
    exclude = ('created_time', 'last_mod_time')

class StrategyAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')

class TradePositionAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')

class StockNameCodeMapAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')

# Register your models here.
admin.site.register(TradeRec, TradeRecAdmin)
admin.site.register(TradeStrategy, StrategyAdmin)
admin.site.register(Positions, TradePositionAdmin)
admin.site.register(StockNameCodeMap, StockNameCodeMapAdmin)



