from stockmarket.models import StockNameCodeMap
from tradeaccounts.models import TradeAccount, Positions
from investors.models import TradeStrategy


def get_stockinfo_for_chart(stock_symbol='sh',):
    stock_info_list = []
    if not stock_symbol.isdigit():
        # 默认上证指数，如果不指定股票编号
        show_code = '1A0001'
        market = 'ZB'
        stock_name = '上证指数'
    else:
        symbol_map = StockNameCodeMap.objects.get(stock_code=stock_symbol)
        stock_name = symbol_map.stock_name
        if stock_symbol[0] == '3':
            market = 'CYB'
            show_code = stock_symbol + '.SZ'
        elif stock_symbol[0] == '0':
            market = 'ZXB'
            show_code = stock_symbol + '.SZ'
        else:
            if stock_symbol[:3] == '688':
                market = 'KCB'
            else:
                market = 'ZB'
            show_code = stock_symbol + '.SH'
    stock_info_list = [stock_symbol, stock_name,  show_code, market]
    return stock_info_list


def get_stock_queryset_for_trade(user, account_id, stock_symbol='sh',):
    trade_account = TradeAccount.objects.get(id=account_id)
    trade_accounts = TradeAccount.objects.filter(trader=user)
    position = Positions.objects.filter(
        trader=user, stock_code=stock_symbol, trade_account=account_id)
    strategies = TradeStrategy.objects.filter(parent_strategy=None)
    trade_type = 'b'  # default trade type is buy. self.kwargs['type']
    stock_info_list = get_stockinfo_for_chart(stock_symbol)
    queryset = {
        'type': trade_type,
        'account_id': account_id,
        'stock_symbol': stock_symbol,
        'stock_name': stock_info_list[1],
        'show_code': stock_info_list[2],
        'market': stock_info_list[3],
        'trade_account': trade_account,
        'accounts': trade_accounts,
        'strategies': strategies,
        'position': position[0] if position.count() > 0 else None,
    }
    return queryset
