from django.contrib import admin
from .models import TradeStrategyStat, BStrategyTestResultOnDays, BStrategyOnPctTest
# Register your models here.

class TradeStrategyStatAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')

class BStrategyTestRstAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')

class BStrategyOnPctTestAdmin(admin.ModelAdmin):
    exclude = ('last_mod_time', 'created_time')


# Register your models here.
admin.site.register(TradeStrategyStat, TradeStrategyStatAdmin)
admin.site.register(BStrategyTestResultOnDays, BStrategyTestRstAdmin)
admin.site.register(BStrategyOnPctTest, BStrategyOnPctTestAdmin)
