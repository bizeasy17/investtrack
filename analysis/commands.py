from datetime import date, datetime
import pandas as pd
from analysis.algorithm import calc_enhanced_rsv,calc_enhanced_rsv_diff
from analysis.models import StockHistoryDaily, StockHistory, StockHistoryIndicators
from analysis.utils import days_to_now
from stockmarket.models import StockNameCodeMap


def pop_rsv_indic(ts_code, freq='D', ):
    ema_list = []
    update_flag = 0
    df_ema = pd.DataFrame({})
    # exec_date = date.today()

    if ts_code is None:
        companies = StockNameCodeMap.objects.filter(
            asset='E').order_by('ts_code')
    else:
        companies = StockNameCodeMap.objects.filter(ts_code=ts_code)

    for company in companies:
        try:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + company.ts_code +
                ' pop RSV enahnced Indicator started.')
            # force to calculate update - testing purpose only
            # if update_flag_p == 1:
            #     update_flag = update_flag_p

            # if freq == 'D':
                # count = int(period)+int(2 * int(period)/7)
                # if period is not None:
                #     hist = StockHistoryDaily.objects.filter(
                #         ts_code=ts_code, freq=freq).values('close','high','low','ts_code','vol','trade_date').order_by('trade_date')[:int(period)]
                # else:
            if company.pop2eema_date is None: # 全新计算RSV
                if freq == 'D':
                    hist = StockHistoryDaily.objects.filter(
                        ts_code=company.ts_code, freq=freq).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')
                else:
                    hist = StockHistory.objects.filter(
                        ts_code=company.ts_code, freq=freq).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')
                
                if len(hist) > 0:
                    df_hist = pd.DataFrame(hist)
                    df_ema = calc_enhanced_rsv(df_var=df_hist, )
                else:
                    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + company.ts_code +
                        ' pop RSV enahnced Indicator ended.')
                    continue
            else: # 更新指标
                if freq == 'D':
                    # 从上次运行开始到今天的交易历史
                    var_hist = StockHistoryDaily.objects.filter(
                        ts_code=company.ts_code, freq=freq, trade_date__lte=date.today(), trade_date__gt=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')

                    # 至少9条老的交易历史?
                    rsv_hist = StockHistoryDaily.objects.filter(
                        ts_code=company.ts_code, freq=freq, trade_date__lte=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('-trade_date')[:8]
                    
                    hist_count = StockHistoryDaily.objects.filter(ts_code=company.ts_code).count()
                else:
                    # 从上次运行开始到今天的交易历史
                    var_hist = StockHistory.objects.filter(
                        ts_code=company.ts_code, freq=freq, trade_date__lte=date.today(), trade_date__gt=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')
                    
                    # 至少9条老的交易历史?
                    rsv_hist = StockHistory.objects.filter(
                        ts_code=company.ts_code, freq=freq, trade_date__lte=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('-trade_date')[:8]
                    
                    hist_count = StockHistory.objects.filter(ts_code=company.ts_code).count()

                if len(var_hist) > 0:
                    df_var = pd.DataFrame.from_records(var_hist)
                    df_rsv_hist = pd.DataFrame.from_records(rsv_hist)

                    df_rsv = pd.concat([df_rsv_hist[::-1], df_var ]) # df[::-1]
                    # update_flag = len(df_var) 
                    df_ema = calc_enhanced_rsv_diff(company.ts_code, df_var, df_rsv, hist_count) # reverse dataframe
                else:
                    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + company.ts_code +
                        ' pop RSV enahnced Indicator ended.')
                    continue
                    # print(hist)
            # elif freq == 'W' or freq == 'M':
            #     if company.pop2eema_date is None:
            #         hist = StockHistory.objects.filter(
            #             ts_code=company.ts_code, freq=freq).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('trade_date')
            #         df_hist = pd.DataFrame(hist)
            #         df_ema = calc_enhanced_rsv(company.ts_code, df_hist)
            #     else:
            #         var_hist = StockHistory.objects.filter(
            #             ts_code=company.ts_code, freq=freq, trade_date__lte=date.today(), trade_date__gt=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('-trade_date')
            #         # 至少9条老的交易历史
            #         rsv_hist = StockHistoryDaily.objects.filter(
            #             ts_code=company.ts_code, freq=freq, trade_date__lte=company.pop2eema_date).values('close', 'high', 'low', 'ts_code', 'vol', 'amount', 'trade_date').order_by('-trade_date')[:9]
                    
            #         if len(var_hist) > 0:
            #             df_var = pd.DataFrame.from_records(var_hist)
            #             df_rsv = pd.DataFrame.from_records(rsv_hist)
                        
            #             df_hist = pd.concat([df_rsv, df_var])
            #             update_flag = len(df_hist)
            #             df_ema = calc_enhanced_rsv(company.ts_code, df_hist.loc[::-1], update_flag=update_flag,)

            # print(df.head())

            for idx, row in df_ema.iterrows():
                # print(row['close'])

                indic = StockHistoryIndicators(ts_code=company.ts_code, close=row['close'], high=row['high'], low=row['low'],
                                               vol=row['vol'], amount=row['amount'], trade_date=row[
                                                   'trade_date'], var1=row['var1'], var2=row['var2'],
                                               var3=row['var3'], rsv=row['rsv'], eema_b=row['b'], eema_s=row['s'], freq=freq, company=company)
                ema_list.append(indic)

            if len(ema_list) > 0:
                StockHistoryIndicators.objects.bulk_create(ema_list)
                company.pop2eema_date = ema_list[-1].trade_date #date.today()
                company.save()
                ema_list.clear()
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ':' + company.ts_code +
                ' pop RSV enahnced Indicator ended.')
        except Exception as err:
            print(err)
