from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Positions, TradeRec


class StockNameWidget(forms.TextInput):
        class Media:
            js = ('js/admin/admin_usr_func.js',)

class TradeRecAdminForm(forms.ModelForm):
    stock_name = forms.CharField(label=_('股票名称或代码'), max_length=50,)# widget=StockNameWidget)

    class Meta:
        model = TradeRec
        fields = ('direction', 'strategy', 'stock_name', #'stock_code', 
                  'trade_time', 'current_price', 'price', 'target_position', 'board_lots', 'cash', 'target_position', 'trader', )

    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     department = cleaned_data.get('department')
    #     isDepartmentSuggested = cleaned_data.get('isDepartmentSuggested')
    #     if department == None and not isDepartmentSuggested:
    #         raise forms.ValidationError(
    #             u"You haven't set a valid department. Do you want to continue?")
    #     return cleaned_data
