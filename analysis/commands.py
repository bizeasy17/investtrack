from datetime import date, datetime
import pandas as pd
from analysis.algorithm import enhanced_ema
from analysis.models import StockHistoryDaily, StockHistory, StockHistoryIndicators
from analysis.utils import days_to_now
from stockmarket.models import StockNameCodeMap


def pop_eema_indic(ts_code, freq='D', update_flag_p=0):
    ema_list = []
    update_flag = 0
    # exec_date = date.today()

    if ts_code is None:
        companies = StockNameCodeMap.objects.filter(
            asset='E').order_by('ts_code')
    else:
        companies = StockNameCodeMap.objects.filter(ts_code=ts_code)

    for company in companies:
        try:

            # force to calculate update - testing purpose only
            # if update_flag_p == 1:
            #     update_flag = update_flag_p

            if freq == 'D':
                # count = int(period)+int(2 * int(period)/7)
                # if period is not None:
                #     hist = StockHistoryDaily.objects.filter(
                #         ts_code=ts_code, freq=freq).values('close','high','low','ts_code','vol','trade_date').order_by('trade_date')[:int(period)]
                # else:
                if company.pop2eema_date is None:
                    hist = StockHistoryDaily.objects.filter(
                        ts_code=company.ts_code, freq=freq).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')
                    df = pd.DataFrame(hist)
                    df_ema = enhanced_ema(company.ts_code, df)

                else:
                    hist_new = StockHistoryDaily.objects.filter(
                        ts_code=company.ts_code, freq=freq, trade_date__lte=date.today(), trade_date__gt=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')
                    # 至少9条老的交易历史
                    hist_offset = StockHistoryDaily.objects.filter(
                        ts_code=company.ts_code, freq=freq, trade_date__lte=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')[:8]
                    
                    df_new = pd.DataFrame.from_records(hist_new)
                    df_offset = pd.DataFrame.from_records(hist_offset)
                    
                    df = pd.concat(df_offset, df_new)
                    update_flag = len(df)
                    df_ema = enhanced_ema(company.ts_code, df)

                    # print(hist)
            elif freq == 'W' or freq == 'M':
                if company.pop2eema_date is None:
                    hist = StockHistory.objects.filter(
                        ts_code=company.ts_code, freq=freq).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')
                    df = pd.DataFrame(hist)
                    df_ema = enhanced_ema(company.ts_code, df)
                else:
                    hist_new = StockHistory.objects.filter(
                        ts_code=company.ts_code, freq=freq, trade_date__lte=date.today(), trade_date__gt=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')
                    # 至少9条老的交易历史
                    hist_offset = StockHistoryDaily.objects.filter(
                        ts_code=company.ts_code, freq=freq, trade_date__lte=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')[:8]
                    
                    df_new = pd.DataFrame.from_records(hist_new)
                    df_offset = pd.DataFrame.from_records(hist_offset)
                    
                    df = pd.concat(df_offset, df_new)
                    update_flag = len(df)
                    df_ema = enhanced_ema(company.ts_code, df)

            # print(df.head())

            for idx, row in df_ema.iterrows():
                # print(row['close'])

                indic = StockHistoryIndicators(ts_code=company.ts_code, close=row['close'], high=row['high'], low=row['low'],
                                               vol=row['vol'], amount=row['amount'], trade_date=row[
                                                   'trade_date'], var1=row['var1'], var2=row['var2'],
                                               var3=row['var3'], rsv=row['rsv'], eema_b=row['b'], eema_s=row['s'], freq=freq, company=company)
                ema_list.append(indic)

            StockHistoryIndicators.objects.bulk_create(ema_list)
            company.pop2eema_date = date.today()
            company.save()
            ema_list.clear()
        except Exception as err:
            print(err)
