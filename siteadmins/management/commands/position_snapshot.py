from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tradeaccounts.models import Positions, TradeAccount, StockPositionSnapshot
from tradeaccounts.utils import calibrate_realtime_position
from users.models import User


class Command(BaseCommand):
    help = 'Taking snapshot for investors stock position'

    def handle(self, *args, **options):
        investors = User.objects.filter(
            is_active=True).exclude(is_superuser=True)
        if investors is not None and len(investors):
            for investor in investors:
                # 2. 根据用户获得所有持仓（未清仓）
                # 3. 获得最新报价，更新持仓和交易记录
                self.sync_stock_position_for_investor(
                    investor)
                # 4. 根据最新持仓信息更新交易账户余额
                stock_positions = Positions.objects.filter(trader=investor).exclude(is_liquidated=True)
                for position in stock_positions:
                    # position.update_account_balance()
                    # 5. 生成账户快照
                    self.take_position_snapshot(position)

    def sync_stock_position_for_investor(self, investor):
        '''
        根据stock_symbol更新最新的价格
        '''
        latest_positions = []
        in_stock_positions = Positions.objects.select_for_update().filter(
            trader=investor).exclude(is_liquidated=True,)
        with transaction.atomic():
            for entry in in_stock_positions:
                calibrate_realtime_position(entry)
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

    def take_position_snapshot(self, position):
        today = date.today()
        # 判断是否存在snapshot
        snapshots = StockPositionSnapshot.objects.filter(p_id=position.id, snap_date=today)
        if snapshots is not None and not snapshots.exists():
            snapshot = StockPositionSnapshot()
            snapshot.take_snapshot(position)
