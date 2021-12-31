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

from .models import StockNameCodeMap


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
