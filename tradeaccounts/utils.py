from decimal import Decimal
from datetime import datetime
from stocktrade.models import Transactions


def calibrate_realtime_position(p):
    '''
    传入参数为持仓Position对象
    非清仓股持仓成本和利润算法
    1. 获取当前实时报价
    2. 查询所有与该持仓相关的交易记录（除系统生成之外）
    3. 循环步骤2中得到的交易记录
    3.1 计算首次建仓
    3.2 计算买入
    3.3 计算卖出
    4. 用实时报价最后计算实时仓位利润

    1. 利润 = 原持仓利润 + (如果未收盘tushare取当前股票价格/收盘价c - 交易价格) * 本次交易量(手) * 100 (1手=100股)
    2. 持仓价格 =
    2.1 如果利润是(负-)的
        每手亏损 = 利润 / (已有持仓-卖出量(手)）
        持仓价格 = 当前股票价格：如果未收盘/收盘价 + 每手亏损
    2.2 如果利润是(正+)的
        每手利润 = 利润 / (已有持仓-卖出量(手)）
        持仓价格 = 当前股票价格：如果未收盘/收盘价 - 每手利润

    调用时需要判断是否已经synchronize，并且
    '''
    count = 0
    profit = Decimal()
    position_price = Decimal()
    # profit_margin = ''
    # trade_fee = Decimal()
    total_shares = 0
    realtime_quote = p.get_realtime_quote(p.stock_code)
    if p.is_sychronized:
        transaction_recs = Transactions.objects.filter(in_stock_positions=p.id, last_mod_time__gte=p.sychronized_datetime).exclude(
            created_or_mod_by='system').order_by('trade_time')
    # 只有在有新交易后才会重新计算
    if not p.is_sychronized or (transaction_recs is not None and transaction_recs.count() > 0):
        transaction_recs = Transactions.objects.filter(in_stock_positions=p.id).exclude(
            created_or_mod_by='system').order_by('trade_time')
        # 对所有之前买入的改股票交易，按照卖出价重新计算利润
        if transaction_recs is not None and transaction_recs.count() > 0:
            for transaction_rec in transaction_recs:
                if count == 0:
                    # 首次建仓
                    if transaction_rec.direction == 'b':
                        profit -= p.calculate_misc_trade_fee(
                            'b', p.trade_account, transaction_rec.board_lots, transaction_rec.price)
                        total_shares = transaction_rec.board_lots
                        position_price = transaction_rec.price - profit / total_shares
                else:
                    if transaction_rec.direction == 'b':
                        profit = (transaction_rec.price - position_price) * total_shares - p.calculate_misc_trade_fee(
                            'b', p.trade_account, transaction_rec.board_lots, transaction_rec.price)
                        total_shares += transaction_rec.board_lots
                        position_price = transaction_rec.price - profit / total_shares
                    elif transaction_rec.direction == 's':
                        profit = (transaction_rec.price - position_price) * total_shares - \
                            p.calculate_misc_trade_fee(
                                's', p.trade_account, transaction_rec.board_lots, transaction_rec.price)
                        total_shares -= transaction_rec.board_lots
                        position_price = transaction_rec.price - profit / total_shares
                    else:
                        pass
                count += 1
    # 重新计算持仓后，更新持仓价
    if count > 0:
        p.position_price = round(position_price, 2)
    # 根据实时报价更新持仓
    p.profit = round(
        (realtime_quote - p.position_price) * p.lots, 2)
    p.profit_ratio = str(round(p.profit / p.cash * 100, 2)) + '%'
    p.current_price = realtime_quote
    p.is_sychronized = True
    p.sychronized_datetime = datetime.now()
    p.save()
    pass
