from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from investmgr.models import Positions, TradeAccount, TradeProfitSnapshot
from users.models import User


class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--period',
            type=str,
            help='Which period you want to apply the snapshot',
        )
        pass

    def handle(self, *args, **options):
        period = options['period']
        if period == 'daily':
            pass
        elif period == 'weekly':
            pass
        elif period == 'monthly':
            pass
        investors = User.objects.filter(
            is_active=True).exclude(is_superuser=True)
        if investors is not None and len(investors):
            for investor in investors:
                # 2. 根据用户获得所有持仓（未清仓）
                # 3. 获得最新报价，更新持仓和交易记录
                self.sync_stock_position_for_investor(
                    investor)
                # 4. 根据最新持仓信息更新交易账户余额
                accounts = TradeAccount.objects.filter(trader=investor)
                for account in accounts:
                    account.update_account_balance()
                    # 5. 生成账户快照
                    self.take_account_snapshot(account)

    def sync_stock_position_for_investor(self, investor):
        '''
        根据stock_symbol更新最新的价格
        '''
        latest_positions = []
        in_stock_positions = Positions.objects.select_for_update().filter(
            trader=investor).exclude(is_liquidated=True,)
        with transaction.atomic():
            for entry in in_stock_positions:
                entry.calibrate_realtime_position()
                latest_positions.append(
                    {
                        'id': entry.pk,
                        'symbol': entry.stock_code,
                        'name': entry.stock_name,
                        'position_price': entry.position_price,
                        'realtime_price': entry.current_price,
                        'profit': entry.profit,
                        'profit_ratio': entry.profit_ratio,
                        'lots': entry.lots,
                        'target_position': entry.target_position,
                        'amount': entry.cash,
                    }
                )
        return latest_positions

    def take_account_snapshot(self, invest_account):
        today = date.today()
        # 判断是否存在snapshot
        snapshots = TradeProfitSnapshot.objects.filter(
            trade_account=invest_account, snap_date=today)
        if snapshots is not None and not snapshots.exists():
            snapshot = TradeProfitSnapshot(
                trade_account=invest_account, snap_date=today)
            snapshot.take_account_snapshot()
