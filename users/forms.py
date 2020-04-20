from django import forms
from django.utils.translation import ugettext_lazy as _
from stocktrade.models import Transactions
from .models import User

class UserTradeForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = ['strategy', 'trade_time', 'stock_name', 'current_price', 'price', 'cash', 'target_position', ]
        labels = {
            'stock_name': _('股票名称或代码'),
        }





