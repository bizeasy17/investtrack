

import pandas as pd
import time
import logging
from datetime import date, datetime, timedelta
from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap
from .models import StockHistoryDaily, StockStrategyTestLog
from .utils import log_test_status
from .stock_hist import hist_since_listed

logger = logging.getLogger(__name__)

# def trade_calendar(exchange, start_date, end_date):
#     # 获取20200101～20200401之间所有有交易的日期
#     pro = ts.pro_api()
#     df = pro.trade_cal(exchange=exchange, is_open='1',
#                        start_date=start_date,
#                        end_date=end_date,
#                        fields='cal_date')
#     return df
#     # print(df.head())


def recon_strategy_usage():
    '''
    同步策略在交易中的使用情况
    '''
    pass

def mark_tupo_yali_listed(freq, ts_code_list=[]):
    '''
    对于未标注九转的上市股票运行一次九转序列标记，
    每次运行只是增量上市股票标记
    '''
    print(ts_code_list)
    # end_date = date.today()
    if len(ts_code_list) == 0 :
        listed_companies = StockNameCodeMap.objects.filter(
            is_marked_jiuzhuan=False, is_hist_downloaded=True)
    else:
        listed_companies = StockNameCodeMap.objects.filter(
            is_marked_jiuzhuan=False, is_hist_downloaded=True, ts_code__in=ts_code_list)
    print(len(listed_companies))
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            hist_list = []
            print(' marked jiuzhuan on start code - ' + listed_company.ts_code + ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            # df = hist_since_listed(
            #     listed_company.ts_code, datetime.strptime(listed_company.list_date, '%Y%m%d'), end_date)
            df = pd.DataFrame()
            if freq == 'D':
                df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(ts_code=listed_company.ts_code).order_by('trade_date').values('id','close','chg4','jiuzhuan_count_b','jiuzhuan_count_s'))
            else:
                pass
            if df is not None and len(df) > 0:
                marked_df = pre_mark_jiuzhuan(df)
                for index, row in marked_df.iterrows():
                    hist = object
                    if freq == 'D':
                        hist = StockHistoryDaily(pk=row['id'])
                    else:
                        pass
                    hist.chg4 = round(row['chg4'], 3)
                    hist.jiuzhuan_count_b = row['jiuzhuan_count_b']
                    hist.jiuzhuan_count_s = row['jiuzhuan_count_s']
                    hist_list.append(hist)
                if freq == 'D':
                    StockHistoryDaily.objects.bulk_update(hist_list, ['chg4', 'jiuzhuan_count_b', 'jiuzhuan_count_s'])
                else:
                    pass
                log_test_status(listed_company.ts_code, 'MARK_CP', freq, ['jiuzhuan_b', 'jiuzhuan_s'])
                listed_company.is_marked_jiuzhuan = True
                listed_company.save()
                print(' marked jiuzhuan on end code - ' + listed_company.ts_code + ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)  

def pre_mark_tupo_yali(df):
    '''
    标记股票的九转序列
    '''
    count_b = 0 # 九转买点
    count_s = 0 # 九转卖点
    jiuzhuan_diff_list = []
    jiuzhuan_diff_s_list = []
    try:
        # df = pro.daily(ts_code=stock_symbol, trade_date=trade_date)
        # 与4天前的收盘价比较
        df_close_diff4 = df['close'].diff(periods=4)
        if df_close_diff4 is not None and len(df_close_diff4) > 0:
            for stock_hist in df_close_diff4.values:
                if stock_hist is not None:
                    if stock_hist < 0: # 股价与往前第四个交易日比较，如果<前值，那么开始计算九转买点，
                        # 同时九转卖点设置为0
                        if count_b < 9:
                            count_b += 1
                        else:
                            count_b = 1
                        count_s = 0
                    else:  # 股价与往前第四个交易日比较，如果>前值，那么开始计算九转卖点，
                        # 同时九转买点设置为0
                        if count_s < 9:
                            count_s += 1
                        else:
                            count_s = 1
                        count_b = 0
                    jiuzhuan_diff_list.append(count_b)
                    jiuzhuan_diff_s_list.append(count_s)
                else:
                    jiuzhuan_diff_list.append(0)
                    jiuzhuan_diff_s_list.append(0)
        # df['diff'] = df_close_diff4
        # df['diff_count'] = jiuzhuan_diff_list
        # df['diff_count_s'] = jiuzhuan_diff_s_list
        df['chg4'] = df_close_diff4
        df['jiuzhuan_count_b'] = jiuzhuan_diff_list
        df['jiuzhuan_count_s'] = jiuzhuan_diff_s_list
    except:
        time.sleep(1)
    else:
        return df