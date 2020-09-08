

import pandas as pd
import time
import logging
from datetime import date, datetime, timedelta
from investors.models import StockFollowing, TradeStrategy
from stockmarket.models import StockNameCodeMap
from .models import StockHistoryDaily, StockStrategyTestLog
from .utils import log_test_status, has_analysis_task, get_analysis_task
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


def test_mark(ts_code, start_date, end_date):
    try:
        hist_list = []
        end_date = date.today()
        df = hist_since_listed(ts_code, start_date, end_date)
        marked_df = pre_mark_jiuzhuan(df)
        for v in marked_df.values:
            hist_D = StockHistoryDaily(ts_code=v[0], trade_date=datetime.strptime(v[1], '%Y%m%d'), open=v[2], high=v[3],
                                       low=v[4], close=v[5], pre_close=v[6], change=v[7], pct_chg=v[8], vol=v[9],
                                       amount=v[10], chg4=v[11], jiuzhuan_count_b=v[12], jiuzhuan_count_s=v[13])
            '''
            ts_code	str	股票代码
            trade_date	str	交易日期
            open	float	开盘价
            high	float	最高价
            low	float	最低价
            close	float	收盘价
            pre_close	float	昨收价
            change	float	涨跌额
            pct_chg	float	涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
            vol	float	成交量 （手）
            amount	float	成交额 （千元）
            '''
            # hist_D.save()
            hist_list.append(hist_D)
        StockHistoryDaily.objects.bulk_create(hist_list)
    except Exception as e:
        logger.error(e)
        return False
    else:
        return True


def mark_jiuzhuan_listed(freq, ts_code_list=[]):
    '''
    对于未标注九转的上市股票运行一次九转序列标记，
    每次运行只是增量上市股票标记
    '''
    print(ts_code_list)
    run_date = date.today()
    if len(ts_code_list) == 0:
        listed_companies = StockNameCodeMap.objects.filter(
            is_marked_jiuzhuan=False, is_hist_downloaded=True)
    else:
        listed_companies = StockNameCodeMap.objects.filter(
            is_marked_jiuzhuan=False, is_hist_downloaded=True, ts_code__in=ts_code_list)
    print(len(listed_companies))
    hist_list = []
    if listed_companies is not None and len(listed_companies) > 0:
        for listed_company in listed_companies:
            if has_analysis_task(listed_company.ts_code, 'MARK_CP', 'jiuzhuan_bs', freq):
                print(' marked jiuzhuan on start code - ' + listed_company.ts_code +
                      ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                task = get_analysis_task(
                    listed_company.ts_code, 'MARK_CP', 'jiiuzhuan_bs', freq)
                # df = hist_since_listed(
                #     listed_company.ts_code, datetime.strptime(listed_company.list_date, '%Y%m%d'), end_date)
                df = pd.DataFrame.from_records(StockHistoryDaily.objects.filter(
                    ts_code=listed_company.ts_code, trade_date__gt=task.start_date - timedelta(days=4), trade_date__lt=task.end_date).order_by(
                    'trade_date').values('id', 'close', 'chg4', 'jiuzhuan_count_b', 'jiuzhuan_count_s'))

                df = pd.DataFrame()
                # if freq == 'D':
                # else:
                #     pass
                if df is not None and len(df) > 0:
                    marked_df = pre_mark_jiuzhuan(df)
                    # 确保处理后的数据只是更新需要更新的开始日期
                    marked_df = marked_df[df['trade_date'] >= task.start_date]
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
                        StockHistoryDaily.objects.bulk_update(
                            hist_list, ['chg4', 'jiuzhuan_count_b', 'jiuzhuan_count_s'])
                    else:
                        pass
                    log_test_status(listed_company.ts_code, 'MARK_CP',
                                    freq, ['jiuzhuan_bs'])
                    listed_company.is_marked_jiuzhuan = True
                    listed_company.save()
                    hist_list.clear()
                    print(' marked jiuzhuan on end code - ' + listed_company.ts_code +
                          ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return len(hist_list)


def pre_mark_jiuzhuan(df):
    '''
    标记股票的九转序列
    '''
    count_b = 0  # 九转买点
    count_s = 0  # 九转卖点
    jiuzhuan_diff_list = []
    jiuzhuan_diff_s_list = []
    try:
        # df = pro.daily(ts_code=stock_symbol, trade_date=trade_date)
        # 与4天前的收盘价比较
        df_close_diff4 = df['close'].diff(periods=4)
        if df_close_diff4 is not None and len(df_close_diff4) > 0:
            for stock_hist in df_close_diff4.values:
                if stock_hist is not None:
                    if stock_hist < 0:  # 股价与往前第四个交易日比较，如果<前值，那么开始计算九转买点，
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