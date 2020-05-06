
import tushare as ts
import pandas as pd
import time
from datetime import date, datetime, timedelta
from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap

pro = ts.pro_api()


def trade_calendar(exchange, start_date, end_date):
    # 获取20200101～20200401之间所有有交易的日期
    df = pro.trade_cal(exchange=exchange, is_open='1',
                       start_date=start_date,
                       end_date=end_date,
                       fields='cal_date')
    return df
    # print(df.head())


def recon_strategy_usage():
    '''
    同步策略在交易中的使用情况
    '''
    pass


def mark_jiuzhuan_listed():
    '''
    对于未标注九转的上市股票运行一次九转序列标记，
    每次运行只是增量上市股票标记
    '''
    today = date.today()
    listed_companies = StockNameCodeMap.objects.filter(
        is_marked_jiuzhuan=False)
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            df = hist_since_listed(
                listed_company.ts_code, listed_company.list_date.strftime('%Y%m%d'))
            mark_jiuzhuan(df)


def split_trade_cal(start_date, end_date):
    '''
    如果取数的时间跨度大于10年，就需要对时间进行拆分
    譬如：
    1. 19910901 - 20050901，返回的是[(19910901,20010831),(20010901,20050901)]
    2. 19910901 - 20010901，返回的是[(19910901,20010901)]
    3. 19910901 - 20200501，返回的是[(19910901,20010831),(20010901,20110901),(20110902,20200501)]
    '''
    split_date_list = []
    start_year = start_date.year
    end_year = end_date.year
    if end_year - start_year <= 10:
        split_date_list.append([start_date, end_date])
    elif end_year - start_year <= 20:
        mid_date = end_year + timedelta(days=365 * 10)
        split_date_list.append(
            [start_date, mid_date],
            [mid_date + timedelta(days=1), start_date]
        )
    elif end_year - start_year <= 30:
        mid_date = end_year + timedelta(days=365*10)
        split_date_list.append(
            [start_date, mid_date],
            [mid_date + timedelta(days=1), mid_date +
             timedelta(days=365*10) + timedelta(days=1)],
            [mid_date + timedelta(days=365*10) + timedelta(days=1),
             end_date],
        )
    return split_date_list


def hist_since_listed(stock_symbol, start_date='', end_date='', freq='D'):
    '''
    将每次的收盘历史数据按照10年分隔从tushare接口获取
    再按照时间先后顺序拼接
    '''
    # pro = ts.pro_api()
    split_cal_list = split_trade_cal(start_date, end_date)
    df_list = []
    for trade_cal in split_cal_list:
        df = ts.pro_bar(ts_code=stock_symbol, adj=None, freq=freq,
                        start_date=trade_cal[0], end_date=trade_cal[1])
        df = df.iloc[::-1]  # 将数据按照时间顺序排列
        df_list.append(df)
    return pd.concat(df_list)


def mark_jiuzhuan(df):
    '''
    标记股票的九转序列
    '''
    count = 0
    jiuzhuan_diff_list = []
    try:
        # df = pro.daily(ts_code=stock_symbol, trade_date=trade_date)
        df_close_diff4 = df['close'].diff(periods=4)
        if df_close_diff4 is not None and len(df_close_diff4) > 0:
            for stock_hist in df_close_diff4.values:
                if stock_hist is not None:
                    if stock_hist < 0:
                        if count < 9:
                            count += 1
                        else:
                            count = 1
                    else:
                        count = 0
                    jiuzhuan_diff_list.append(count)
                else:
                    jiuzhuan_diff_list.append(0)
        df['diff'] = df_close_diff4
        df['diff_count'] = jiuzhuan_diff_list
    except:
        time.sleep(1)
    else:
        return df


def get_daily(self, ts_code='', trade_date='', start_date='', end_date=''):
    for _ in range(3):
        try:
            if trade_date:
                df = self.pro.daily(ts_code=ts_code, trade_date=trade_date)
            else:
                df = self.pro.daily(
                    ts_code=ts_code, start_date=start_date, end_date=end_date)
        except:
            time.sleep(1)
        else:
            return df
