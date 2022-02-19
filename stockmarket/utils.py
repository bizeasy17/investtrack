import ast
import decimal
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import tushare as ts
from analysis.models import (AnalysisDateSeq, IndustryBasicQuantileStat,
                             StockHistoryDaily)

from stockmarket.models import CompanyFinIndicators, StockNameCodeMap

from .models import CompanyBalanceSheet, StockNameCodeMap


def get_single_realtime_quote(symbol):
    # 保持向前兼容
    code = symbol.split('.')
    symbol = code[0]
    # 获得实时报价
    realtime_df = ts.get_realtime_quotes(symbol)  # 需要再判断一下ts_code
    realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                               'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
    realtime_price_dict = {}
    if len(realtime_df) > 0:
        if realtime_df['price'].mean() != 0:
            realtime_quote = realtime_df['price'].mean()
        elif realtime_df['pre_close'].mean() != 0:
            realtime_quote = realtime_df['pre_close'].mean()
        elif realtime_df['open'].mean() != 0:
            realtime_quote = realtime_df['open'].mean()
        t = datetime.strptime(str(
            realtime_df['date'][0]) + ' ' + str(realtime_df['time'][0]), "%Y-%m-%d %H:%M:%S")
        realtime_price_dict = {
            't': t, 'o': realtime_df['open'].mean(), 'h': realtime_df['high'].mean(),
            'l': realtime_df['low'].mean(),
            'c': realtime_quote, 'p': realtime_df['pre_close'].mean(),
        }
    return realtime_price_dict


def get_realtime_quote(stock_symbols=[]):
    realtime_quotes = {}
    if stock_symbols is not None and len(stock_symbols) >= 1:
        realtime_df = ts.get_realtime_quotes(stock_symbols)
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
        if realtime_df is not None and len(realtime_df) > 0:
            for realtime_quote in realtime_df.values:
                price = round(decimal.Decimal(realtime_quote[3]), 2)
                bid = round(decimal.Decimal(realtime_quote[6]), 2)
                pre_close = round(decimal.Decimal(realtime_quote[2]), 2)
                if price != decimal.Decimal(0.00):
                    price = price
                elif bid != decimal.Decimal(0.00):
                    price = bid
                else:
                    price = pre_close
                realtime_quotes[realtime_quote[0]] = price
    return realtime_quotes


def get_realtime_quotes(stock_symbols=[]):
    realtime_quotes = {}
    if stock_symbols is not None and len(stock_symbols) >= 1:
        realtime_df = ts.get_realtime_quotes(stock_symbols)
        realtime_df = realtime_df[['code', 'open', 'pre_close', 'price',
                                   'high', 'low', 'bid', 'ask', 'volume', 'amount', 'date', 'time']]
        if realtime_df is not None and len(realtime_df) > 0:
            for realtime_quote in realtime_df.values:
                price = round(decimal.Decimal(realtime_quote[3]), 2)
                bid = round(decimal.Decimal(realtime_quote[6]), 2)
                pre_close = round(decimal.Decimal(realtime_quote[2]), 2)
                if price != decimal.Decimal(0.00):
                    price = price
                elif bid != decimal.Decimal(0.00):
                    price = bid
                else:
                    price = pre_close
                realtime_quotes[realtime_quote[0]] = str(price) + ',' + str(round(
                    (price - pre_close) / pre_close, 2) * 100)
    return realtime_quotes


def get_stocknames(stock_symbols=[]):
    stocknames = {}
    if stock_symbols is not None and len(stock_symbols) >= 1:
        for stock_symbol in stock_symbols:
            map = StockNameCodeMap.objects.get(ts_code=stock_symbol)
            stocknames[stock_symbol] = map.stock_name
    return stocknames


def str_eval(str):
    '''
    逗号分隔，转成dict
    '''
    dict = ast.literal_eval(str)
    return dict


def get_ind_basic(industry, type=[]):
    ind_dict = {}

    try:
        last_analysis = AnalysisDateSeq.objects.filter(
            applied=True, seq_type='INDUSTRY_BASIC_QUANTILE').order_by('-analysis_date').first()

        ibqs = IndustryBasicQuantileStat.objects.filter(industry=industry,
                                                        basic_type__in=type, snap_date=last_analysis.analysis_date).exclude(
            quantile=.25).exclude(quantile=.75).order_by('-snap_date')

        if ibqs is not None and len(ibqs) > 0:
            for ibq in ibqs:
                ind_dict[ibq.basic_type+str(ibq.quantile)] = ibq.quantile_val if not np.isnan(
                    ibq.quantile_val) else 0

        return ind_dict
    except Exception as e:
        print(e)


def collect_fin_indicators(ts_code):
    try:
        pro = ts.pro_api()

        # 查询当前所有正常上市交易的股票列表
        fina_indicator_list = []
        end_year = date.today().year
        end_date = None
        if ts_code is None:
            companies = StockNameCodeMap.objects.filter(
                asset='E').order_by('ts_code')
        else:
            companies = StockNameCodeMap.objects.filter(ts_code=ts_code)

        for company in companies:
            print('starting for ' + company.ts_code +
                  ':' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            list_year = company.list_date.year

            if company.fin_indicator_date is None:
                if end_year - list_year <= 20:
                    data = pro.fina_indicator(
                        ts_code=company.ts_code, start_date=str(list_year)+'0101', end_date=str(end_year)+'1231', fields=get_fina_indicator_fields())
                else:
                    temp_year = end_year - 20
                    data1 = pro.fina_indicator(
                        ts_code=company.ts_code, start_date=str(temp_year)+'0101', end_date=str(end_year)+'1231', fields=get_fina_indicator_fields())
                    data2 = pro.fina_indicator(
                        ts_code=company.ts_code, start_date=str(list_year)+'0101', end_date=str(temp_year-1)+'1231', fields=get_fina_indicator_fields())
                    data = pd.concat([data1, data2])
            else:
                data = pro.fina_indicator(
                    ts_code=company.ts_code, start_date=company.fin_indicator_date.strftime('%Y%m%d'), end_date=str(end_year)+'1231', fields=get_fina_indicator_fields())

            # old_indicators = CompanyFinIndicators.objects.filter(
            #     ts_code=company.ts_code)

            # print(len(data))

            if len(data) > 0:
                for index, row in data.iterrows():
                    # try:
                    # print(datetime.strptime(
                    #     row['ann_date'], '%Y%m%d'))
                    # print(datetime.strptime(row['end_date'], '%Y%m%d'))
                    indicators = CompanyFinIndicators.objects.filter(
                        ts_code=company.ts_code, announce_date=datetime.strptime(
                            row['ann_date'], '%Y%m%d'), end_date=datetime.strptime(row['end_date'], '%Y%m%d'))
                    if len(indicators) <= 0:
                        cfi = CompanyFinIndicators(ts_code=company.ts_code,
                                                   announce_date=datetime.strptime(
                                                       row['ann_date'], '%Y%m%d'),
                                                   end_date=datetime.strptime(
                                                       row['end_date'], '%Y%m%d'), company=company)
                        # top10_holder.save()
                        cfi.eps = row['eps']  # float	Y	基本每股收益
                        cfi.dt_eps = row['dt_eps']  # float	Y	稀释每股收益
                        # float	Y	每股营业总收入
                        cfi.total_revenue_ps = row['total_revenue_ps']
                        cfi.revenue_ps = row['revenue_ps']  # float	Y	每股营业收入
                        # float	Y	每股资本公积
                        cfi.capital_rese_ps = row['capital_rese_ps']
                        # float	Y	每股盈余公积
                        cfi.surplus_rese_ps = row['surplus_rese_ps']
                        # float	Y	每股未分配利润
                        cfi.undist_profit_ps = row['undist_profit_ps']
                        cfi.extra_item = row['extra_item']  # float	Y	非经常性损益
                        # float	Y	扣除非经常性损益后的净利润（扣非净利润）
                        cfi.profit_dedt = row['profit_dedt']
                        cfi.gross_margin = row['gross_margin']  # float	Y	毛利
                        # float	Y	流动比率
                        cfi.current_ratio = row['current_ratio']
                        cfi.quick_ratio = row['quick_ratio']  # float	Y	速动比率
                        cfi.cash_ratio = row['cash_ratio']  # float	Y	保守速动比率
                        # float	N	存货周转天数
                        cfi.invturn_days = row['invturn_days']
                        # float	N	应收账款周转天数
                        cfi.arturn_days = row['arturn_days']
                        cfi.inv_turn = row['inv_turn']  # float	N	存货周转率
                        cfi.ar_turn = row['ar_turn']  # float	Y	应收账款周转率
                        cfi.ca_turn = row['ca_turn']  # float	Y	流动资产周转率
                        cfi.fa_turn = row['fa_turn']  # float	Y	固定资产周转率
                        cfi.assets_turn = row['assets_turn']  # float	Y	总资产周转率
                        cfi.op_income = row['op_income']  # float	Y	经营活动净收益
                        # float	N	价值变动净收益
                        cfi.valuechange_income = row['valuechange_income']
                        # float	N	利息费用
                        cfi.interst_income = row['interst_income']
                        cfi.daa = row['daa']  # float	N	折旧与摊销
                        cfi.ebit = row['ebit']  # float	Y	息税前利润
                        cfi.ebitda = row['ebitda']  # float	Y	息税折旧摊销前利润
                        cfi.fcff = row['fcff']  # float	Y	企业自由现金流量
                        cfi.fcfe = row['fcfe']  # float	Y	股权自由现金流量
                        # float	Y	无息流动负债
                        cfi.current_exint = row['current_exint']
                        # float	Y	无息非流动负债
                        cfi.noncurrent_exint = row['noncurrent_exint']
                        cfi.interestdebt = row['interestdebt']  # float	Y	带息债务
                        cfi.netdebt = row['netdebt']  # float	Y	净债务
                        # float	Y	有形资产
                        cfi.tangible_asset = row['tangible_asset']
                        # float	Y	营运资金
                        cfi.working_capital = row['working_capital']
                        # float	Y	营运流动资本
                        cfi.networking_capital = row['networking_capital']
                        # float	Y	全部投入资本
                        cfi.invest_capital = row['invest_capital']
                        # float	Y	留存收益
                        cfi.retained_earnings = row['retained_earnings']
                        # float	Y	期末摊薄每股收益
                        cfi.diluted2_eps = row['diluted2_eps']
                        cfi.bps = row['bps']  # float	Y	每股净资产
                        cfi.ocfps = row['ocfps']  # float	Y	每股经营活动产生的现金流量净额
                        cfi.retainedps = row['retainedps']  # float	Y	每股留存收益
                        cfi.cfps = row['cfps']  # float	Y	每股现金流量净额
                        cfi.ebit_ps = row['ebit_ps']  # float	Y	每股息税前利润
                        cfi.fcff_ps = row['fcff_ps']  # float	Y	每股企业自由现金流量
                        cfi.fcfe_ps = row['fcfe_ps']  # float	Y	每股股东自由现金流量
                        # float	Y	销售净利率
                        cfi.netprofit_margin = row['netprofit_margin']
                        # float	Y	销售毛利率
                        cfi.grossprofit_margin = row['grossprofit_margin']
                        # float	Y	销售成本率
                        cfi.cogs_of_sales = row['cogs_of_sales']
                        # float	Y	销售期间费用率
                        cfi.expense_of_sales = row['expense_of_sales']
                        # float	Y	净利润/营业总收入
                        cfi.profit_to_gr = row['profit_to_gr']
                        # float	Y	销售费用/营业总收入
                        cfi.saleexp_to_gr = row['saleexp_to_gr']
                        # float	Y	管理费用/营业总收入
                        cfi.adminexp_of_gr = row['adminexp_of_gr']
                        # float	Y	财务费用/营业总收入
                        cfi.finaexp_of_gr = row['finaexp_of_gr']
                        # float	Y	资产减值损失/营业总收入
                        cfi.impai_ttm = row['impai_ttm']
                        cfi.gc_of_gr = row['gc_of_gr']  # float	Y	营业总成本/营业总收入
                        cfi.op_of_gr = row['op_of_gr']  # float	Y	营业利润/营业总收入
                        # float	Y	息税前利润/营业总收入
                        cfi.ebit_of_gr = row['ebit_of_gr']
                        cfi.roe = row['roe']  # float	Y	净资产收益率
                        cfi.roe_waa = row['roe_waa']  # float	Y	加权平均净资产收益率
                        cfi.roe_dt = row['roe_dt']  # float	Y	净资产收益率(扣除非经常损益)
                        cfi.roa = row['roa']  # float	Y	总资产报酬率
                        cfi.npta = row['npta']  # float	Y	总资产净利润
                        cfi.roic = row['roic']  # float	Y	投入资本回报率
                        cfi.roe_yearly = row['roe_yearly']  # float	Y	年化净资产收益率
                        # float	Y	年化总资产报酬率
                        cfi.roa2_yearly = row['roa2_yearly']
                        cfi.roe_avg = row['roe_avg']  # float	N	平均净资产收益率(增发条件)
                        # float	N	经营活动净收益/利润总额
                        cfi.opincome_of_ebt = row['opincome_of_ebt']
                        # float	N	价值变动净收益/利润总额
                        cfi.investincome_of_ebt = row['investincome_of_ebt']
                        # float	N	营业外收支净额/利润总额
                        cfi.n_op_profit_of_ebt = row['n_op_profit_of_ebt']
                        cfi.tax_to_ebt = row['tax_to_ebt']  # float	N	所得税/利润总额
                        # float	N	扣除非经常损益后的净利润/净利润
                        cfi.dtprofit_to_profit = row['dtprofit_to_profit']
                        # float	N	销售商品提供劳务收到的现金/营业收入
                        cfi.salescash_to_or = row['salescash_to_or']
                        # float	N	经营活动产生的现金流量净额/营业收入
                        cfi.ocf_to_or = row['ocf_to_or']
                        # float	N	经营活动产生的现金流量净额/经营活动净收益
                        cfi.ocf_to_opincome = row['ocf_to_opincome']
                        # float	N	资本支出/折旧和摊销
                        cfi.capitalized_to_da = row['capitalized_to_da']
                        # float	Y	资产负债率
                        cfi.debt_to_assets = row['debt_to_assets']
                        # float	Y	权益乘数
                        cfi.assets_to_eqt = row['assets_to_eqt']
                        # float	Y	权益乘数(杜邦分析)
                        cfi.dp_assets_to_eqt = row['dp_assets_to_eqt']
                        # float	Y	流动资产/总资产
                        cfi.ca_to_assets = row['ca_to_assets']
                        # float	Y	非流动资产/总资产
                        cfi.nca_to_assets = row['nca_to_assets']
                        # float	Y	有形资产/总资产
                        cfi.tbassets_to_totalassets = row['tbassets_to_totalassets']
                        # float	Y	带息债务/全部投入资本
                        cfi.int_to_talcap = row['int_to_talcap']
                        # float	Y	归属于母公司的股东权益/全部投入资本
                        cfi.eqt_to_talcapital = row['eqt_to_talcapital']
                        # float	Y	流动负债/负债合计
                        cfi.currentdebt_to_debt = row['currentdebt_to_debt']
                        # float	Y	非流动负债/负债合计
                        cfi.longdeb_to_debt = row['longdeb_to_debt']
                        # float	Y	经营活动产生的现金流量净额/流动负债
                        cfi.ocf_to_shortdebt = row['ocf_to_shortdebt']
                        cfi.debt_to_eqt = row['debt_to_eqt']  # float	Y	产权比率
                        # float	Y	归属于母公司的股东权益/负债合计
                        cfi.eqt_to_debt = row['eqt_to_debt']
                        # float	Y	归属于母公司的股东权益/带息债务
                        cfi.eqt_to_interestdebt = row['eqt_to_interestdebt']
                        # float	Y	有形资产/负债合计
                        cfi.tangibleasset_to_debt = row['tangibleasset_to_debt']
                        # float	Y	有形资产/带息债务
                        cfi.tangasset_to_intdebt = row['tangasset_to_intdebt']
                        # float	Y	有形资产/净债务
                        cfi.tangibleasset_to_netdebt = row['tangibleasset_to_netdebt']
                        # float	Y	经营活动产生的现金流量净额/负债合计
                        cfi.ocf_to_debt = row['ocf_to_debt']
                        # float	N	经营活动产生的现金流量净额/带息债务
                        cfi.ocf_to_interestdebt = row['ocf_to_interestdebt']
                        # float	N	经营活动产生的现金流量净额/净债务
                        cfi.ocf_to_netdebt = row['ocf_to_netdebt']
                        # float	N	已获利息倍数(EBIT/利息费用)
                        cfi.ebit_to_interest = row['ebit_to_interest']
                        # float	N	长期债务与营运资金比率
                        cfi.longdebt_to_workingcapital = row['longdebt_to_workingcapital']
                        # float	N	息税折旧摊销前利润/负债合计
                        cfi.ebitda_to_debt = row['ebitda_to_debt']
                        cfi.turn_days = row['turn_days']  # float	Y	营业周期
                        cfi.roa_yearly = row['roa_yearly']  # float	Y	年化总资产净利率
                        cfi.roa_dp = row['roa_dp']  # float	Y	总资产净利率(杜邦分析)
                        # float	Y	固定资产合计
                        cfi.fixed_assets = row['fixed_assets']
                        # float	N	扣除财务费用前营业利润
                        cfi.profit_prefin_exp = row['profit_prefin_exp']
                        # float	N	非营业利润
                        cfi.non_op_profit = row['non_op_profit']
                        cfi.op_to_ebt = row['op_to_ebt']  # float	N	营业利润／利润总额
                        # float	N	非营业利润／利润总额
                        cfi.nop_to_ebt = row['nop_to_ebt']
                        # float	N	经营活动产生的现金流量净额／营业利润
                        cfi.ocf_to_profit = row['ocf_to_profit']
                        # float	N	货币资金／流动负债
                        cfi.cash_to_liqdebt = row['cash_to_liqdebt']
                        # float	N	货币资金／带息流动负债
                        cfi.cash_to_liqdebt_withinterest = row['cash_to_liqdebt_withinterest']
                        # float	N	营业利润／流动负债
                        cfi.op_to_liqdebt = row['op_to_liqdebt']
                        cfi.op_to_debt = row['op_to_debt']  # float	N	营业利润／负债合计
                        # float	N	年化投入资本回报率
                        cfi.roic_yearly = row['roic_yearly']
                        # float	N	固定资产合计周转率
                        cfi.total_fa_trun = row['total_fa_trun']
                        # float	Y	利润总额／营业收入
                        cfi.profit_to_op = row['profit_to_op']
                        # float	N	经营活动单季度净收益
                        cfi.q_opincome = row['q_opincome']
                        # float	N	价值变动单季度净收益
                        cfi.q_investincome = row['q_investincome']
                        # float	N	扣除非经常损益后的单季度净利润
                        cfi.q_dtprofit = row['q_dtprofit']
                        cfi.q_eps = row['q_eps']  # float	N	每股收益(单季度)
                        # float	N	销售净利率(单季度)
                        cfi.q_netprofit_margin = row['q_netprofit_margin']
                        # float	N	销售毛利率(单季度)
                        cfi.q_gsprofit_margin = row['q_gsprofit_margin']
                        # float	N	销售期间费用率(单季度)
                        cfi.q_exp_to_sales = row['q_exp_to_sales']
                        # float	N	净利润／营业总收入(单季度)
                        cfi.q_profit_to_gr = row['q_profit_to_gr']
                        # float	Y	销售费用／营业总收入 (单季度)
                        cfi.q_saleexp_to_gr = row['q_saleexp_to_gr']
                        # float	N	管理费用／营业总收入 (单季度)
                        cfi.q_adminexp_to_gr = row['q_adminexp_to_gr']
                        # float	N	财务费用／营业总收入 (单季度)
                        cfi.q_finaexp_to_gr = row['q_finaexp_to_gr']
                        # float	N	资产减值损失／营业总收入(单季度)
                        cfi.q_impair_to_gr_ttm = row['q_impair_to_gr_ttm']
                        # float	Y	营业总成本／营业总收入 (单季度)
                        cfi.q_gc_to_gr = row['q_gc_to_gr']
                        # float	N	营业利润／营业总收入(单季度)
                        cfi.q_op_to_gr = row['q_op_to_gr']
                        cfi.q_roe = row['q_roe']  # float	Y	净资产收益率(单季度)
                        # float	Y	净资产单季度收益率(扣除非经常损益)
                        cfi.q_dt_roe = row['q_dt_roe']
                        cfi.q_npta = row['q_npta']  # float	Y	总资产净利润(单季度)
                        # float	N	经营活动净收益／利润总额(单季度)
                        cfi.q_opincome_to_ebt = row['q_opincome_to_ebt']
                        # float	N	价值变动净收益／利润总额(单季度)
                        cfi.q_investincome_to_ebt = row['q_investincome_to_ebt']
                        # float	N	扣除非经常损益后的净利润／净利润(单季度)
                        cfi.q_dtprofit_to_profit = row['q_dtprofit_to_profit']
                        # float	N	销售商品提供劳务收到的现金／营业收入(单季度)
                        cfi.q_salescash_to_or = row['q_salescash_to_or']
                        # float	Y	经营活动产生的现金流量净额／营业收入(单季度)
                        cfi.q_ocf_to_sales = row['q_ocf_to_sales']
                        # float	N	经营活动产生的现金流量净额／经营活动净收益(单季度)
                        cfi.q_ocf_to_or = row['q_ocf_to_or']
                        # float	Y	基本每股收益同比增长率(%)
                        cfi.basic_eps_yoy = row['basic_eps_yoy']
                        # float	Y	稀释每股收益同比增长率(%)
                        cfi.dt_eps_yoy = row['dt_eps_yoy']
                        # float	Y	每股经营活动产生的现金流量净额同比增长率(%)
                        cfi.cfps_yoy = row['cfps_yoy']
                        cfi.op_yoy = row['op_yoy']  # float	Y	营业利润同比增长率(%)
                        cfi.ebt_yoy = row['ebt_yoy']  # float	Y	利润总额同比增长率(%)
                        # float	Y	归属母公司股东的净利润同比增长率(%)
                        cfi.netprofit_yoy = row['netprofit_yoy']
                        # float	Y	归属母公司股东的净利润-扣除非经常损益同比增长率(%)
                        cfi.dt_netprofit_yoy = row['dt_netprofit_yoy']
                        # float	Y	经营活动产生的现金流量净额同比增长率(%)
                        cfi.ocf_yoy = row['ocf_yoy']
                        # float	Y	净资产收益率(摊薄)同比增长率(%)
                        cfi.roe_yoy = row['roe_yoy']
                        cfi.bps_yoy = row['bps_yoy']  # float	Y	每股净资产相对年初增长率(%)
                        # float	Y	资产总计相对年初增长率(%)
                        cfi.assets_yoy = row['assets_yoy']
                        # float	Y	归属母公司的股东权益相对年初增长率(%)
                        cfi.eqt_yoy = row['eqt_yoy']
                        cfi.tr_yoy = row['tr_yoy']  # float	Y	营业总收入同比增长率(%)
                        cfi.or_yoy = row['or_yoy']  # float	Y	营业收入同比增长率(%)
                        # float	N	营业总收入同比增长率(%)(单季度)
                        cfi.q_gr_yoy = row['q_gr_yoy']
                        # float	N	营业总收入环比增长率(%)(单季度)
                        cfi.q_gr_qoq = row['q_gr_qoq']
                        # float	Y	营业收入同比增长率(%)(单季度)
                        cfi.q_sales_yoy = row['q_sales_yoy']
                        # float	N	营业收入环比增长率(%)(单季度)
                        cfi.q_sales_qoq = row['q_sales_qoq']
                        # float	N	营业利润同比增长率(%)(单季度)
                        cfi.q_op_yoy = row['q_op_yoy']
                        # float	Y	营业利润环比增长率(%)(单季度)
                        cfi.q_op_qoq = row['q_op_qoq']
                        # float	N	净利润同比增长率(%)(单季度)
                        cfi.q_profit_yoy = row['q_profit_yoy']
                        # float	N	净利润环比增长率(%)(单季度)
                        cfi.q_profit_qoq = row['q_profit_qoq']
                        # float	N	归属母公司股东的净利润同比增长率(%)(单季度)
                        cfi.q_netprofit_yoy = row['q_netprofit_yoy']
                        # float	N	归属母公司股东的净利润环比增长率(%)(单季度)
                        cfi.q_netprofit_qoq = row['q_netprofit_qoq']
                        cfi.equity_yoy = row['equity_yoy']  # float	Y	净资产同比增长率
                        cfi.rd_exp = row['rd_exp']  # float	N	研发费用
                        cfi.update_flag = row['update_flag']  # str	N	更新标识
                        fina_indicator_list.append(cfi)

                    # except CompanyFinIndicators.DoesNotExist:

                        # cn_tz = pytz.timezone("Asia/Shanghai")
                        # end_date = row['end_date']
                        # print(company.ts_code + ' created new object')
                if len(fina_indicator_list) > 0:
                    CompanyFinIndicators.objects.bulk_create(
                        fina_indicator_list)
                    # if company.top10_holder_date != datetime.strptime(row['end_date'], '%Y%m%d'):
                    # company.top10_holder_date = datetime.strptime(row['end_date'], '%Y%m%d')
                    # company.save()
                    company.fin_indicator_date = fina_indicator_list[0].end_date
                    fina_indicator_list.clear()
                    company.save()
                # time.sleep(0.3)
            print('end for ' + company.ts_code +
                  ':' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # StockNameCodeMap.objects.bulk_update(companies, ['top10_holder_date'])
    except Exception as e:
        print(e)


def get_fina_indicator_fields():
    fields = 'ts_code,ann_date,end_date,eps,dt_eps,total_revenue_ps,' \
        'revenue_ps,capital_rese_ps,surplus_rese_ps,undist_profit_ps,extra_item,profit_dedt,' \
        'gross_margin,current_ratio,quick_ratio,cash_ratio,invturn_days,arturn_days,inv_turn,' \
        'ar_turn,ca_turn,fa_turn,assets_turn,op_income,valuechange_income,interst_income,daa,ebit,' \
        'ebitda,fcff,fcfe,current_exint,noncurrent_exint,interestdebt,netdebt,tangible_asset,working_capital,' \
        'networking_capital,invest_capital,retained_earnings,diluted2_eps,bps,ocfps,retainedps,cfps,ebit_ps,' \
        'fcff_ps,fcfe_ps,netprofit_margin,grossprofit_margin,cogs_of_sales,expense_of_sales,profit_to_gr,' \
        'saleexp_to_gr,adminexp_of_gr,finaexp_of_gr,impai_ttm,gc_of_gr,op_of_gr,ebit_of_gr,roe,roe_waa,roe_dt,' \
        'roa,npta,roic,roe_yearly,roa2_yearly,roe_avg,opincome_of_ebt,investincome_of_ebt,n_op_profit_of_ebt,' \
        'tax_to_ebt,dtprofit_to_profit,salescash_to_or,ocf_to_or,ocf_to_opincome,capitalized_to_da,debt_to_assets,' \
        'assets_to_eqt,dp_assets_to_eqt,ca_to_assets,nca_to_assets,tbassets_to_totalassets,int_to_talcap,' \
        'eqt_to_talcapital,currentdebt_to_debt,longdeb_to_debt,ocf_to_shortdebt,debt_to_eqt,eqt_to_debt,' \
        'eqt_to_interestdebt,tangibleasset_to_debt,tangasset_to_intdebt,tangibleasset_to_netdebt,ocf_to_debt,' \
        'ocf_to_interestdebt,ocf_to_netdebt,ebit_to_interest,longdebt_to_workingcapital,ebitda_to_debt,' \
        'turn_days,roa_yearly,roa_dp,fixed_assets,profit_prefin_exp,non_op_profit,op_to_ebt,nop_to_ebt,' \
        'ocf_to_profit,cash_to_liqdebt,cash_to_liqdebt_withinterest,op_to_liqdebt,op_to_debt,roic_yearly,' \
        'total_fa_trun,profit_to_op,q_opincome,q_investincome,q_dtprofit,q_eps,q_netprofit_margin,q_gsprofit_margin,' \
        'q_exp_to_sales,q_profit_to_gr,q_saleexp_to_gr,q_adminexp_to_gr,q_finaexp_to_gr,q_impair_to_gr_ttm,' \
        'q_gc_to_gr,q_op_to_gr,q_roe,q_dt_roe,q_npta,q_opincome_to_ebt,q_investincome_to_ebt,q_dtprofit_to_profit,' \
        'q_salescash_to_or,q_ocf_to_sales,q_ocf_to_or,basic_eps_yoy,dt_eps_yoy,cfps_yoy,op_yoy,ebt_yoy,netprofit_yoy,' \
        'dt_netprofit_yoy,ocf_yoy,roe_yoy,bps_yoy,assets_yoy,eqt_yoy,tr_yoy,or_yoy,q_gr_yoy,q_gr_qoq,q_sales_yoy,' \
        'q_sales_qoq,q_op_yoy,q_op_qoq,q_profit_yoy,q_profit_qoq,q_netprofit_yoy,q_netprofit_qoq,' \
        'equity_yoy,rd_exp,update_flag'
    return fields


def collect_balance_sheet(ts_code):
    try:
        pro = ts.pro_api()

        # 查询当前所有正常上市交易的股票列表
        balance_sheet_list = []
        end_year = date.today().year
        end_date = None
        if ts_code is None:
            companies = StockNameCodeMap.objects.filter(
                asset='E').order_by('ts_code')
        else:
            companies = StockNameCodeMap.objects.filter(ts_code=ts_code)

        for company in companies:
            print('starting for ' + company.ts_code +
                  ':' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            list_year = company.list_date.year

            if company.balance_sheet_date is None:
                if end_year - list_year <= 20:
                    data = pro.balancesheet(
                        ts_code=company.ts_code, start_date=str(list_year)+'0101', end_date=str(end_year)+'1231', fields=get_balance_sheet_fields())
                else:
                    temp_year = end_year - 20
                    data1 = pro.balancesheet(
                        ts_code=company.ts_code, start_date=str(temp_year)+'0101', end_date=str(end_year)+'1231', fields=get_balance_sheet_fields())
                    data2 = pro.balancesheet(
                        ts_code=company.ts_code, start_date=str(list_year)+'0101', end_date=str(temp_year-1)+'1231', fields=get_balance_sheet_fields())
                    data = pd.concat([data1, data2])
            else:
                data = pro.balancesheet(
                    ts_code=company.ts_code, start_date=company.fin_indicator_date.strftime('%Y%m%d'), end_date=str(end_year)+'1231', fields=get_balance_sheet_fields())

            # old_indicators = CompanyFinIndicators.objects.filter(
            #     ts_code=company.ts_code)

            # print(len(data))

            if len(data) > 0:
                for index, row in data.iterrows():
                    # try:
                    # print(datetime.strptime(
                    #     row['ann_date'], '%Y%m%d'))
                    # print(datetime.strptime(row['end_date'], '%Y%m%d'))
                    balance_sheet = CompanyBalanceSheet.objects.filter(
                        ts_code=company.ts_code, announce_date=datetime.strptime(
                            row['ann_date'], '%Y%m%d'), f_announce_date=datetime.strptime(
                            row['f_ann_date'], '%Y%m%d'), end_date=datetime.strptime(row['end_date'], '%Y%m%d'))
                    if len(balance_sheet) <= 0:
                        cbs = CompanyBalanceSheet(ts_code=company.ts_code,
                                                  announce_date=datetime.strptime(
                                                      row['ann_date'], '%Y%m%d'),
                                                  f_announce_date=datetime.strptime(
                                                      row['f_ann_date'], '%Y%m%d'),
                                                  end_date=datetime.strptime(
                                                      row['end_date'], '%Y%m%d'), company=company)
                        # cbs.ts_code = row['ts_code']  # str	Y	TS股票代码
                        # cbs.announce_date = row['ann_date']  # s	str	Y	公告日期
                        # s	str	Y	实际公告日期
                        # cbs.f_announce_date = row['f_ann_date']
                        # cbs.end_date = row['end_date']  # s	str	Y	报告期
                        cbs.report_type = row['report_type']  # sstr	Y	报表类型
                        # s	str	Y	公司类型(1一般工商业2银行3保险4证券)
                        cbs.comp_type = row['comp_type']
                        cbs.end_type = row['end_type']  # s	str	Y	报告期类型
                        cbs.total_share = row['total_share']  # s	float	Y	期末总股本
                        cbs.cap_rese = row['cap_rese']  # s	float	Y	资本公积金
                        # s	float	Y	未分配利润
                        cbs.undistr_porfit = row['undistr_porfit']
                        # s	float	Y	盈余公积金
                        cbs.surplus_rese = row['surplus_rese']
                        # s	float	Y	专项储备
                        cbs.special_rese = row['special_rese']
                        cbs.money_cap = row['money_cap']  # s	float	Y	货币资金
                        cbs.trad_asset = row['trad_asset']  # s	float	Y	交易性金融资产
                        # s	float	Y	应收票据
                        cbs.notes_receiv = row['notes_receiv']
                        # s	float	Y	应收账款
                        cbs.accounts_receiv = row['accounts_receiv']
                        cbs.oth_receiv = row['oth_receiv']  # s	float	Y	其他应收款
                        cbs.prepayment = row['prepayment']  # s	float	Y	预付款项
                        cbs.div_receiv = row['div_receiv']  # s	float	Y	应收股利
                        cbs.int_receiv = row['int_receiv']  # s	float	Y	应收利息
                        cbs.inventories = row['inventories']  # s	float	Y	存货
                        cbs.amor_exp = row['amor_exp']  # s	float	Y	长期待摊费用
                        # s	float	Y	一年内到期的非流动资产
                        cbs.nca_within_1y = row['nca_within_1y']
                        cbs.sett_rsrv = row['sett_rsrv']  # s	float	Y	结算备付金
                        # s	float	Y	拆出资金
                        cbs.loanto_oth_bank_fi = row['loanto_oth_bank_fi']
                        # s	float	Y	应收保费
                        cbs.premium_receiv = row['premium_receiv']
                        # s	float	Y	应收分保账款
                        cbs.reinsur_receiv = row['reinsur_receiv']
                        # s	float	Y	应收分保合同准备金
                        cbs.reinsur_res_receiv = row['reinsur_res_receiv']
                        # s	float	Y	买入返售金融资产
                        cbs.pur_resale_fa = row['pur_resale_fa']
                        # s	float	Y	其他流动资产
                        cbs.oth_cur_assets = row['oth_cur_assets']
                        # s	float	Y	流动资产合计
                        cbs.total_cur_assets = row['total_cur_assets']
                        # s	float	Y	可供出售金融资产
                        cbs.fa_avail_for_sale = row['fa_avail_for_sale']
                        cbs.htm_invest = row['htm_invest']  # s	float	Y	持有至到期投资
                        # s	float	Y	长期股权投资
                        cbs.lt_eqt_invest = row['lt_eqt_invest']
                        # s	float	Y	投资性房地产
                        cbs.invest_real_estate = row['invest_real_estate']
                        # s	float	Y	定期存款
                        cbs.time_deposits = row['time_deposits']
                        cbs.oth_assets = row['oth_assets']  # s	float	Y	其他资产
                        cbs.lt_rec = row['lt_rec']  # s	float	Y	长期应收款
                        cbs.fix_assets = row['fix_assets']  # s	float	Y	固定资产
                        cbs.cip = row['cip']  # sfloat	Y	在建工程
                        # sfloat	Y	工程物资
                        cbs.const_materials = row['const_materials']
                        # s	float	Y	固定资产清理
                        cbs.fixed_assets_disp = row['fixed_assets_disp']
                        # s	float	Y	生产性生物资产
                        cbs.produc_bio_assets = row['produc_bio_assets']
                        # s	float	Y	油气资产
                        cbs.oil_and_gas_assets = row['oil_and_gas_assets']
                        cbs.intan_assets = row['intan_assets']  # float	Y	无形资产
                        cbs.r_and_d = row['r_and_d']  # float	Y	研发支出
                        cbs.goodwill = row['goodwill']  # float	Y	商誉
                        cbs.lt_amor_exp = row['lt_amor_exp']  # float	Y	长期待摊费用
                        # float	Y	递延所得税资产
                        cbs.defer_tax_assets = row['defer_tax_assets']
                        # float	Y	发放贷款及垫款
                        cbs.decr_in_disbur = row['decr_in_disbur']
                        cbs.oth_nca = row['oth_nca']  # float	Y	其他非流动资产
                        cbs.total_nca = row['total_nca']  # float	Y	非流动资产合计
                        # float	Y	现金及存放中央银行款项
                        cbs.cash_reser_cb = row['cash_reser_cb']
                        # float	Y	存放同业和其它金融机构款项
                        cbs.depos_in_oth_bfi = row['depos_in_oth_bfi']
                        cbs.prec_metals = row['prec_metals']  # float	Y	贵金属
                        # float	Y	衍生金融资产
                        cbs.deriv_assets = row['deriv_assets']
                        # float	Y	应收分保未到期责任准备金
                        cbs.rr_reins_une_prem = row['rr_reins_une_prem']
                        # float	Y	应收分保未决赔款准备金
                        cbs.rr_reins_outstd_cla = row['rr_reins_outstd_cla']
                        # float	Y	应收分保寿险责任准备金
                        cbs.rr_reins_lins_liab = row['rr_reins_lins_liab']
                        # float	Y	应收分保长期健康险责任准备金
                        cbs.rr_reins_lthins_liab = row['rr_reins_lthins_liab']
                        cbs.refund_depos = row['refund_depos']  # float	Y	存出保证金
                        # float	Y	保户质押贷款
                        cbs.ph_pledge_loans = row['ph_pledge_loans']
                        # float	Y	存出资本保证金
                        cbs.refund_cap_depos = row['refund_cap_depos']
                        # float	Y	独立账户资产
                        cbs.indep_acct_assets = row['indep_acct_assets']
                        # float	Y	其中：客户资金存款
                        cbs.client_depos = row['client_depos']
                        # float	Y	其中：客户备付金
                        cbs.client_prov = row['client_prov']
                        # float	Y	其中:交易席位费
                        cbs.transac_seat_fee = row['transac_seat_fee']
                        # float	Y	应收款项类投资
                        cbs.invest_as_receiv = row['invest_as_receiv']
                        cbs.total_assets = row['total_assets']  # float	Y	资产总计
                        cbs.lt_borr = row['lt_borr']  # float	Y	长期借款
                        cbs.st_borr = row['st_borr']  # float	Y	短期借款
                        cbs.cb_borr = row['cb_borr']  # float	Y	向中央银行借款
                        # float	Y	吸收存款及同业存放
                        cbs.depos_ib_deposits = row['depos_ib_deposits']
                        # float	Y	拆入资金
                        cbs.loan_oth_bank = row['loan_oth_bank']
                        cbs.trading_fl = row['trading_fl']  # float	Y	交易性金融负债
                        # float	Y	应付票据
                        cbs.notes_payable = row['notes_payable']
                        cbs.acct_payable = row['acct_payable']  # float	Y	应付账款
                        cbs.adv_receipts = row['adv_receipts']  # float	Y	预收款项
                        # float	Y	卖出回购金融资产款
                        cbs.sold_for_repur_fa = row['sold_for_repur_fa']
                        # float	Y	应付手续费及佣金
                        cbs.comm_payable = row['comm_payable']
                        # float	Y	应付职工薪酬
                        cbs.payroll_payable = row['payroll_payable']
                        # float	Y	应交税费
                        cbs.taxes_payable = row['taxes_payable']
                        cbs.int_payable = row['int_payable']  # float	Y	应付利息
                        cbs.div_payable = row['div_payable']  # float	Y	应付股利
                        cbs.oth_payable = row['oth_payable']  # float	Y	其他应付款
                        cbs.acc_exp = row['acc_exp']  # float	Y	预提费用
                        cbs.deferred_inc = row['deferred_inc']  # float	Y	递延收益
                        # float	Y	应付短期债券
                        cbs.st_bonds_payable = row['st_bonds_payable']
                        # float	Y	应付分保账款
                        cbs.payable_to_reinsurer = row['payable_to_reinsurer']
                        # float	Y	保险合同准备金
                        cbs.rsrv_insur_cont = row['rsrv_insur_cont']
                        # float	Y	代理买卖证券款
                        cbs.acting_trading_sec = row['acting_trading_sec']
                        # float	Y	代理承销证券款
                        cbs.acting_uw_sec = row['acting_uw_sec']
                        # float	Y	一年内到期的非流动负债
                        cbs.non_cur_liab_due_1y = row['non_cur_liab_due_1y']
                        # float	Y	其他流动负债
                        cbs.oth_cur_liab = row['oth_cur_liab']
                        # float	Y	流动负债合计
                        cbs.total_cur_liab = row['total_cur_liab']
                        cbs.bond_payable = row['bond_payable']  # float	Y	应付债券
                        cbs.lt_payable = row['lt_payable']  # float	Y	长期应付款
                        # float	Y	专项应付款
                        cbs.specific_payables = row['specific_payables']
                        # float	Y	预计负债
                        cbs.estimated_liab = row['estimated_liab']
                        # float	Y	递延所得税负债
                        cbs.defer_tax_liab = row['defer_tax_liab']
                        # float	Y	递延收益-非流动负债
                        cbs.defer_inc_non_cur_liab = row['defer_inc_non_cur_liab']
                        cbs.oth_ncl = row['oth_ncl']  # float	Y	其他非流动负债
                        cbs.total_ncl = row['total_ncl']  # float	Y	非流动负债合计
                        # float	Y	同业和其它金融机构存放款项
                        cbs.depos_oth_bfi = row['depos_oth_bfi']
                        cbs.deriv_liab = row['deriv_liab']  # float	Y	衍生金融负债
                        cbs.depos = row['depos']  # float	Y	吸收存款
                        # float	Y	代理业务负债
                        cbs.agency_bus_liab = row['agency_bus_liab']
                        cbs.oth_liab = row['oth_liab']  # float	Y	其他负债
                        # float	Y	预收保费
                        cbs.prem_receiv_adva = row['prem_receiv_adva']
                        # float	Y	存入保证金
                        cbs.depos_received = row['depos_received']
                        cbs.ph_invest = row['ph_invest']  # float	Y	保户储金及投资款
                        # float	Y	未到期责任准备金
                        cbs.reser_une_prem = row['reser_une_prem']
                        # float	Y	未决赔款准备金
                        cbs.reser_outstd_claims = row['reser_outstd_claims']
                        # float	Y	寿险责任准备金
                        cbs.reser_lins_liab = row['reser_lins_liab']
                        # float	Y	长期健康险责任准备金
                        cbs.reser_lthins_liab = row['reser_lthins_liab']
                        # float	Y	独立账户负债
                        cbs.indept_acc_liab = row['indept_acc_liab']
                        cbs.pledge_borr = row['pledge_borr']  # float	Y	其中:质押借款
                        # float	Y	应付赔付款
                        cbs.indem_payable = row['indem_payable']
                        # float	Y	应付保单红利
                        cbs.policy_div_payable = row['policy_div_payable']
                        cbs.total_liab = row['total_liab']  # float	Y	负债合计
                        # float	Y	减:库存股
                        cbs.treasury_share = row['treasury_share']
                        # float	Y	一般风险准备
                        cbs.ordin_risk_reser = row['ordin_risk_reser']
                        # float	Y	外币报表折算差额
                        cbs.forex_differ = row['forex_differ']
                        # float	Y	未确认的投资损失
                        cbs.invest_loss_unconf = row['invest_loss_unconf']
                        # float	Y	少数股东权益
                        cbs.minority_int = row['minority_int']
                        # float	Y	股东权益合计(不含少数股东权益)
                        cbs.total_hldr_eqy_exc_min_int = row['total_hldr_eqy_exc_min_int']
                        # float	Y	股东权益合计(含少数股东权益)
                        cbs.total_hldr_eqy_inc_min_int = row['total_hldr_eqy_inc_min_int']
                        # float	Y	负债及股东权益总计
                        cbs.total_liab_hldr_eqy = row['total_liab_hldr_eqy']
                        # float	Y	长期应付职工薪酬
                        cbs.lt_payroll_payable = row['lt_payroll_payable']
                        # float	Y	其他综合收益
                        cbs.oth_comp_income = row['oth_comp_income']
                        # float	Y	其他权益工具
                        cbs.oth_eqt_tools = row['oth_eqt_tools']
                        # float	Y	其他权益工具(优先股)
                        cbs.oth_eqt_tools_p_shr = row['oth_eqt_tools_p_shr']
                        # float	Y	融出资金
                        cbs.lending_funds = row['lending_funds']
                        # float	Y	应收款项
                        cbs.acc_receivable = row['acc_receivable']
                        # float	Y	应付短期融资款
                        cbs.st_fin_payable = row['st_fin_payable']
                        cbs.payables = row['payables']  # float	Y	应付款项
                        cbs.hfs_assets = row['hfs_assets']  # float	Y	持有待售的资产
                        cbs.hfs_sales = row['hfs_sales']  # float	Y	持有待售的负债
                        # float	Y	以摊余成本计量的金融资产
                        cbs.cost_fin_assets = row['cost_fin_assets']
                        # float	Y	以公允价值计量且其变动计入其他综合收益的金融资产
                        cbs.fair_value_fin_assets = row['fair_value_fin_assets']
                        cbs.cip_total = row['cip_total']  # float	Y	在建工程(合计)(元)
                        # float	Y	其他应付款(合计)(元)
                        cbs.oth_pay_total = row['oth_pay_total']
                        # float	Y	长期应付款(合计)(元)
                        cbs.long_pay_total = row['long_pay_total']
                        cbs.debt_invest = row['debt_invest']  # float	Y	债权投资(元)
                        # float	Y	其他债权投资(元)
                        cbs.oth_debt_invest = row['oth_debt_invest']
                        # float	N	其他权益工具投资(元)
                        cbs.oth_eq_invest = row['oth_eq_invest']
                        # float	N	其他非流动金融资产(元)
                        cbs.oth_illiq_fin_assets = row['oth_illiq_fin_assets']
                        # float	N	其他权益工具:永续债(元)
                        cbs.oth_eq_ppbond = row['oth_eq_ppbond']
                        # float	N	应收款项融资
                        cbs.receiv_financing = row['receiv_financing']
                        # float	N	使用权资产
                        cbs.use_right_assets = row['use_right_assets']
                        cbs.lease_liab = row['lease_liab']  # float	N	租赁负债
                        # float	Y	合同资产
                        cbs.contract_assets = row['contract_assets']
                        # float	Y	合同负债
                        cbs.contract_liab = row['contract_liab']
                        # float	Y	应收票据及应收账款
                        cbs.accounts_receiv_bill = row['accounts_receiv_bill']
                        # float	Y	应付票据及应付账款
                        cbs.accounts_pay = row['accounts_pay']
                        # float	Y	其他应收款(合计)（元）
                        cbs.oth_rcv_total = row['oth_rcv_total']
                        # float	Y	固定资产(合计)(元)
                        cbs.fix_assets_total = row['fix_assets_total']
                        cbs.update_flag = row['update_flag']  # str	N	更新标识
                        balance_sheet_list.append(cbs)

                    # except CompanyFinIndicators.DoesNotExist:

                        # cn_tz = pytz.timezone("Asia/Shanghai")
                        # end_date = row['end_date']
                        # print(company.ts_code + ' created new object')
                if len(balance_sheet_list) > 0:
                    CompanyBalanceSheet.objects.bulk_create(
                        balance_sheet_list)
                    # if company.top10_holder_date != datetime.strptime(row['end_date'], '%Y%m%d'):
                    # company.top10_holder_date = datetime.strptime(row['end_date'], '%Y%m%d')
                    # company.save()
                    company.balance_sheet_date = balance_sheet_list[0].end_date
                    balance_sheet_list.clear()
                    company.save()
                # time.sleep(0.3)
            print('end for ' + company.ts_code +
                  ':' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # StockNameCodeMap.objects.bulk_update(companies, ['top10_holder_date'])
    except Exception as e:
        print(e)


def get_balance_sheet_fields():
    fields = 'ts_code,ann_date,f_ann_date,end_date,report_type,'\
        'comp_type,end_type,total_share,cap_rese,undistr_porfit,'\
        'surplus_rese,special_rese,money_cap,trad_asset,notes_receiv,'\
        'accounts_receiv,oth_receiv,prepayment,div_receiv,int_receiv,inventories,'\
        'amor_exp,nca_within_1y,sett_rsrv,loanto_oth_bank_fi,premium_receiv,reinsur_receiv,'\
        'reinsur_res_receiv,pur_resale_fa,oth_cur_assets,total_cur_assets,fa_avail_for_sale,htm_invest,'\
        'lt_eqt_invest,invest_real_estate,time_deposits,oth_assets,lt_rec,fix_assets,cip,const_materials,'\
        'fixed_assets_disp,produc_bio_assets,oil_and_gas_assets,intan_assets,r_and_d,goodwill,lt_amor_exp,'\
        'defer_tax_assets,decr_in_disbur,oth_nca,total_nca,cash_reser_cb,depos_in_oth_bfi,prec_metals,deriv_assets,'\
        'rr_reins_une_prem,rr_reins_outstd_cla,rr_reins_lins_liab,rr_reins_lthins_liab,refund_depos,ph_pledge_loans,'\
        'refund_cap_depos,indep_acct_assets,client_depos,client_prov,transac_seat_fee,invest_as_receiv,total_assets,'\
        'lt_borr,st_borr,cb_borr,depos_ib_deposits,loan_oth_bank,trading_fl,notes_payable,acct_payable,adv_receipts,sold_for_repur_fa,'\
        'comm_payable,payroll_payable,taxes_payable,int_payable,div_payable,oth_payable,acc_exp,deferred_inc,st_bonds_payable,'\
        'payable_to_reinsurer,rsrv_insur_cont,acting_trading_sec,acting_uw_sec,non_cur_liab_due_1y,oth_cur_liab,total_cur_liab,'\
        'bond_payable,lt_payable,specific_payables,estimated_liab,defer_tax_liab,defer_inc_non_cur_liab,oth_ncl,'\
        'total_ncl,depos_oth_bfi,deriv_liab,depos,agency_bus_liab,oth_liab,prem_receiv_adva,depos_received,ph_invest,reser_une_prem,'\
        'reser_outstd_claims,reser_lins_liab,reser_lthins_liab,indept_acc_liab,pledge_borr,indem_payable,policy_div_payable,'\
        'total_liab,treasury_share,ordin_risk_reser,forex_differ,invest_loss_unconf,minority_int,total_hldr_eqy_exc_min_int,'\
        'total_hldr_eqy_inc_min_int,total_liab_hldr_eqy,lt_payroll_payable,oth_comp_income,oth_eqt_tools,oth_eqt_tools_p_shr,'\
        'lending_funds,acc_receivable,st_fin_payable,payables,hfs_assets,hfs_sales,cost_fin_assets,fair_value_fin_assets,'\
        'cip_total,oth_pay_total,long_pay_total,debt_invest,oth_debt_invest,oth_eq_invest,oth_illiq_fin_assets,oth_eq_ppbond,'\
        'receiv_financing,use_right_assets,lease_liab,contract_assets,contract_liab,accounts_receiv_bill,accounts_pay,'\
        'oth_rcv_total,fix_assets_total,update_flag'
    return fields
