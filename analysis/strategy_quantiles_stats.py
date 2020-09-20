import logging
import math
from datetime import date, datetime, timedelta

import pandas as pd

from stockmarket.models import StockNameCodeMap
from .utils import has_analysis_task1, log_test_status
from .models import (BStrategyOnFixedPctTest, StrategyTargetPctTestQuantiles,
                     StrategyTestLowHigh, StrategyUpDownTestQuantiles, StrategyUpDownTestRanking, StrategyTargetPctTestRanking)

logger = logging.getLogger(__name__)


def target_pct_quantiles_stat(strategy_code, ts_code, stock_name, freq='D'):
    # freq = 'D'
    target_pct_list = ['pct10_period', 'pct20_period', 'pct30_period',
                       'pct50_period', 'pct80_period', 'pct100_period', 'pct130_period']
    try:
        if not has_analysis_task1(ts_code, 'TGT_PCT_QTN', strategy_code, freq):
            print('target pct on start - ' + strategy_code + '/' + ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            quantile_list = []
            target_pct_qtiles_list = []
            # for target_pct in target_pct_list:
            results = BStrategyOnFixedPctTest.objects.filter(strategy_code=strategy_code, ts_code=ts_code,
                                                             test_freq=freq).order_by('trade_date')  # [:int(freq_count)]
            if results is not None and len(results) > 0:
                df = pd.DataFrame(results.values())
                for target_pct in target_pct_list:
                    # print(target_pct)
                    df = df[df[target_pct] != -1]
                    qtiles = df[target_pct].quantile(
                        [0.1, 0.25, 0.5, 0.75, 0.9])
                    # for qtile in qtiles.values():
                    for idx, value in qtiles.items():
                        quantile_list.append(round(value, 3))
                        # print(value)
                    quantile_list.append(round(df[target_pct].max(), 3))
                    quantile_list.append(round(df[target_pct].min(), 3))
                    quantile_list.append(round(df[target_pct].mean(), 3))
                    # print(quantile_list)
                    target_pct_qtiles = StrategyTargetPctTestQuantiles(
                        strategy_code=strategy_code, target_pct=target_pct, ts_code=ts_code, stock_name=stock_name,
                        qt_10pct=quantile_list[0], qt_25pct=quantile_list[1], qt_50pct=quantile_list[2],
                        qt_75pct=quantile_list[3], qt_90pct=quantile_list[4], max_val=quantile_list[5],
                        min_val=quantile_list[6], mean_val=quantile_list[7])
                    target_pct_qtiles_list.append(target_pct_qtiles)
                    quantile_list.clear()
            if len(target_pct_qtiles_list) > 0:
                StrategyTargetPctTestQuantiles.objects.bulk_create(
                    target_pct_qtiles_list)
                log_test_status(ts_code,
                                'TGT_PCT_QTN', freq, [strategy_code])
                print('target pct on end - ' + strategy_code + '/' + ts_code +
                      ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                print('no record for target pct on - ' + strategy_code + '/' + ts_code +
                      ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            print('already exist target pct on - ' + strategy_code + '/' + ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as err:
        print(err)
        logging.error(err)


def updown_pct_quantiles_stat(strategy_code, ts_code, stock_name, freq='D'):
    # test_period_list = [10,20,30,50,80,130,210,340,550] 正确的序列应该为340, 550
    test_period_list = [10, 20, 30, 50, 80, 130, 210, 350, 560]
    # strategy_codes = ['jiuzhuan_b', 'jiuzhuan_s', 'dibu_b', 'dingbu_s', 'w_di', 'm_ding', 'tupo_yali_b',
    #                      'diepo_zhicheng_s', 'ma25_zhicheng_b', 'ma25_tupo_b', 'ma25_diepo_s', 'ma25_yali_s']
    test_type = ['up_pct', 'down_pct']

    try:
        if not has_analysis_task1(ts_code, 'UPDN_PCT_QTN', strategy_code, freq):
            print('updown pct on start - ' + strategy_code + '/' + ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            updown_qtiles_list = []
            low_quantile_list = []
            high_quantile_list = []
            for test_period in test_period_list:
                results = StrategyTestLowHigh.objects.filter(
                    strategy_code=strategy_code, ts_code=ts_code, test_period=test_period)
                if results is not None and len(results) > 0:
                    df = pd.DataFrame(results.values(
                        'stage_high_pct', 'stage_low_pct'))
                    high_qtiles = df.stage_high_pct.quantile(
                        [0.1, 0.25, 0.5, 0.75, 0.9])
                    low_qtiles = df.stage_low_pct.quantile(
                        [0.1, 0.25, 0.5, 0.75, 0.9])
                    for qtile in high_qtiles:
                        high_quantile_list.append(round(qtile, 3))
                    high_quantile_list.append(
                        round(df.stage_high_pct.max(), 3))
                    high_quantile_list.append(
                        round(df.stage_high_pct.min(), 3))
                    high_quantile_list.append(
                        round(df.stage_high_pct.mean(), 3))
                    for qtile in low_qtiles:
                        low_quantile_list.append(round(qtile, 3))
                    low_quantile_list.append(round(df.stage_low_pct.max(), 3))
                    low_quantile_list.append(round(df.stage_low_pct.min(), 3))
                    low_quantile_list.append(round(df.stage_low_pct.mean(), 3))
                    strategy_up_qtiles = StrategyUpDownTestQuantiles(
                        strategy_code=strategy_code, test_type=test_type[
                            0], ts_code=ts_code, stock_name=stock_name, test_period=test_period,
                        qt_10pct=high_quantile_list[0], qt_25pct=high_quantile_list[1], qt_50pct=high_quantile_list[2],
                        qt_75pct=high_quantile_list[3], qt_90pct=high_quantile_list[4], max_val=high_quantile_list[5],
                        min_val=high_quantile_list[6], mean_val=high_quantile_list[7])
                    strategy_down_qtiles = StrategyUpDownTestQuantiles(
                        strategy_code=strategy_code, stock_name=stock_name, test_type=test_type[
                            1], ts_code=ts_code, test_period=test_period,
                        qt_10pct=low_quantile_list[0], qt_25pct=low_quantile_list[1], qt_50pct=low_quantile_list[2],
                        qt_75pct=low_quantile_list[3], qt_90pct=low_quantile_list[4], max_val=low_quantile_list[5],
                        min_val=low_quantile_list[6], mean_val=low_quantile_list[7])
                    updown_qtiles_list.append(strategy_up_qtiles)
                    updown_qtiles_list.append(strategy_down_qtiles)
                    high_quantile_list.clear()
                    low_quantile_list.clear()
            if len(updown_qtiles_list) > 0:
                StrategyUpDownTestQuantiles.objects.bulk_create(
                    updown_qtiles_list)
                log_test_status(ts_code,
                                'UPDN_PCT_QTN', freq, [strategy_code])
                print('updown pct on end - ' + strategy_code + '/' + ts_code +
                      ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                print('no record for updown pct on - ' + strategy_code + '/' + ts_code +
                      ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            print('already exist updown pct on end - ' + strategy_code + '/' + ts_code +
                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as err:
        logger.error(err)


def rank_updown_test(strategy_code, freq='D'):
    try:
        print('updown pct ranking on start - ' + strategy_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        test_period_list = [10, 20, 30, 50, 80, 130, 210, 350, 560]
        quantile_list = ['qt_10pct', 'qt_25pct', 'qt_50pct',
                         'qt_75pct', 'qt_90pct', 'mean_val', 'min_val', 'max_val']
        test_type_list = ['up_pct', 'down_pct']
        ranking_list = []
        ranking_tscode_list = []
        for test_type in test_type_list:
            for test_period in test_period_list:
                results = StrategyUpDownTestQuantiles.objects.filter(
                    strategy_code=strategy_code, test_type=test_type, test_period=test_period, test_freq=freq)
                if results is not None and len(results) > 0:
                    for quantile in quantile_list:
                        df = pd.DataFrame(results.values(
                            quantile, 'ts_code', 'stock_name'))
                        sorted_df = df.sort_values(
                            by=quantile, ascending=False, ignore_index=True)
                        for idx in sorted_df.index:
                            if not has_analysis_task1(sorted_df.iloc[idx][1], 'UPDN_PCT_RK', strategy_code, freq):
                                print('analyzing ' + sorted_df.iloc[idx][1] + ' qt is ' +
                                      quantile + ' period is, ' + str(test_period) + ' ranking is ' + str(idx))
                                ranking = StrategyUpDownTestRanking(strategy_code=strategy_code, test_type=test_type, ts_code=sorted_df.iloc[idx][1], stock_name=sorted_df.iloc[idx][2],
                                                                    test_period=test_period, qt_pct=quantile, qt_pct_val=sorted_df.iloc[idx][0], test_freq=freq, ranking=idx)
                                ranking_list.append(ranking)
                                if sorted_df.iloc[idx][1] not in ranking_tscode_list:
                                    ranking_tscode_list.append(
                                        sorted_df.iloc[idx][1])
                            else:
                                print('already exist updown pct ranking on - ' + strategy_code +
                                      ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        if len(ranking_list) > 0:
                            StrategyUpDownTestRanking.objects.bulk_create(
                                ranking_list)
                            ranking_list.clear()
                            print('updown pct ranking saving end - ' + strategy_code + ' ,quantile ' + quantile +
                                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            print('no record for updown pct ranking on end - ' + strategy_code + ' ,quantile ' + quantile +
                                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        for ts_code in ranking_tscode_list:
            log_test_status(ts_code,
                            'UPDN_PCT_RK', freq, [strategy_code])
        print('updown pct ranking on end - ' + strategy_code + ' ,quantile ' + quantile +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as err:
        logger.error(err)
        print(err)


def rank_target_pct_test(strategy_code, freq='D'):
    print('target pct ranking on start - ' + strategy_code +
          ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    target_pct_list = ['pct10_period', 'pct20_period', 'pct30_period',
                       'pct50_period', 'pct80_period', 'pct100_period', 'pct130_period']
    quantile_list = ['qt_10pct', 'qt_25pct', 'qt_50pct',
                     'qt_75pct', 'qt_90pct', 'mean_val', 'min_val', 'max_val']
    ranking_list = []
    ranking_tscode_list = []
    try:
        for target_pct in target_pct_list:
            results = StrategyTargetPctTestQuantiles.objects.filter(
                strategy_code=strategy_code, test_freq=freq, target_pct=target_pct)
            if results is not None and len(results) > 0:
                for quantile in quantile_list:
                    df = pd.DataFrame(results.values(
                        quantile, 'ts_code', 'stock_name'))
                    # 先获取所有能找到预期收益的记录，即target pct <> -1的记录
                    valid_df = df[df[quantile].notnull()]
                    sorted_df = valid_df.sort_values(
                        by=quantile, ignore_index=True)
                    for idx, row in sorted_df.iterrows():
                        # print(idx)
                        if not has_analysis_task1(row['ts_code'], 'TGT_PCT_RK', strategy_code, freq):
                            print('analyzing ' + row['ts_code'] + ' qt is ' + quantile +
                                  ' target pct is, ' + target_pct + ' ranking is ' + str(idx))

                            ranking = StrategyTargetPctTestRanking(strategy_code=strategy_code, ts_code=row['ts_code'], stock_name=row['stock_name'],
                                                                   target_pct=target_pct, qt_pct=quantile, qt_pct_val=row[quantile], test_freq=freq, ranking=idx)
                            ranking_list.append(ranking)
                            if row['ts_code'] not in ranking_tscode_list:
                                ranking_tscode_list.append(row['ts_code'])
                    # 先获取所有无法找到预期收益的记录，即target pct = -1的记录
                    invalid_df = df[df[quantile].isnull()]
                    # print(len(invalid_df))
                    for idx, row in invalid_df.iterrows():
                        # print(quantile)
                        # print(row['ts_code'])
                        if not has_analysis_task1(row['ts_code'], 'TGT_PCT_RK', strategy_code, freq):
                            ranking = StrategyTargetPctTestRanking(strategy_code=strategy_code, ts_code=row['ts_code'], stock_name=row['stock_name'],
                                                                   target_pct=target_pct, qt_pct=quantile, qt_pct_val=row[quantile], test_freq=freq, ranking=99999)
                            ranking_list.append(ranking)
                            ranking_tscode_list.append(row['ts_code'])
                            print('target pct ranking saving end - ' + strategy_code + ' ,quantile ' + quantile +
                                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            print('already exist target pct ranking on - ' + strategy_code + ' ,quantile ' + quantile +
                                  ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            # 先获取所有能找到预期收益的记录，即target pct <> -1的记录
                    # print(ranking_list)
                    if len(ranking_list) > 0:
                        StrategyTargetPctTestRanking.objects.bulk_create(
                            ranking_list)
                        ranking_list.clear()
                    else:
                        print('no record for target pct ranking on end - ' + strategy_code + ' ,quantile ' + quantile +
                              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        for ts_code in ranking_tscode_list:
            log_test_status(ts_code,
                            'TGT_PCT_RK', freq, [strategy_code])
        print('target pct ranking on end - ' + strategy_code +
              ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as err:
        logger.error(err)
        print(err)
