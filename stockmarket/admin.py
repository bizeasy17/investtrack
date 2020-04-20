from django.contrib import admin

from stockmarket.models import StockNameCodeMap

# Register your models here.

class StockNameCodeMapAdmin(admin.ModelAdmin):
    list_display = (
        'stock_name', 'stock_code', 'ts_code', 'exchange', 'market', 'area', 'industry', 'list_status', 'list_date', 'delist_date', 'is_hs')

    exclude = ('last_mod_time', 'created_time')

# Register your models here.
admin.site.register(StockNameCodeMap, StockNameCodeMapAdmin)
