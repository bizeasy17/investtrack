
# Register your models here.
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Transactions


# Register your models here.
class TransactionListFilter(admin.SimpleListFilter):
    title = _('交易者')
    parameter_name = 'trader'

    def lookups(self, request, model_admin):
        traders = list(set(map(lambda x: x.trader, Transactions.objects.all())))
        for trader in traders:
            yield (trader.id, _(trader.username))

    def queryset(self, request, queryset):
        id = self.value()
        if id:
            return queryset.filter(trader__id__exact=id).exclude(created_or_mod_by='system')
        else:
            return queryset.filter().exclude(created_or_mod_by='system')

class TransactionAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('stock_name', 'stock_code')
    list_display = (
        'trader', 'stock_name', 'stock_code', 'direction', 'price', 'board_lots', 'current_price', 'is_liquidated', 'created_time')
    list_display_links = ('stock_name', 'stock_code')
    list_filter = (TransactionListFilter, 'strategy')
    exclude = ('created_time', 'last_mod_time')

# Register your models here.
admin.site.register(Transactions, TransactionAdmin)
