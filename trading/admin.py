from django.contrib import admin
from .models import Wallet, Transaction, Round, Trade
from django.utils import timezone
from decimal import Decimal

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username',)

    def save_model(self, request, obj, form, change):
        if change:
            old_wallet = Wallet.objects.get(pk=obj.pk)
            diff = obj.balance - old_wallet.balance
            if diff > 0:
                Transaction.objects.create(user=obj.user, amount=diff, transaction_type='DEPOSIT')
            elif diff < 0:
                Transaction.objects.create(user=obj.user, amount=abs(diff), transaction_type='WITHDRAW')
        super().save_model(request, obj, form, change)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'timestamp')
    list_filter = ('transaction_type',)
    search_fields = ('user__username',)

@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('round_id', 'start_time', 'end_time', 'status', 'result')
    list_filter = ('status', 'result')
    readonly_fields = ('round_id',)

    def save_model(self, request, obj, form, change):
        is_closing = False
        if change:
            old_round = Round.objects.get(pk=obj.pk)
            if old_round.status == 'RUNNING' and obj.result != 'PENDING':
                is_closing = True
                obj.status = 'COMPLETED'

        super().save_model(request, obj, form, change)

        if is_closing:
            # Resolve trades
            trades = Trade.objects.filter(round=obj, status='PENDING')
            for trade in trades:
                if trade.color == obj.result:
                    trade.status = 'WIN'
                    if trade.color in ['RED', 'GREEN']:
                        trade.payout = trade.amount * Decimal('2.0')
                    elif trade.color == 'VIOLET':
                        trade.payout = trade.amount * Decimal('4.5')
                    
                    # Credit wallet
                    wallet = trade.user.wallet
                    wallet.balance += trade.payout
                    wallet.save()
                    
                    # Record transaction
                    Transaction.objects.create(user=trade.user, amount=trade.payout, transaction_type='WIN')
                else:
                    trade.status = 'LOSS'
                    trade.payout = Decimal('0.00')
                trade.save()
            
            # Auto-create next round
            Round.objects.create(
                start_time=timezone.now(),
                end_time=timezone.now() + timezone.timedelta(seconds=30),
                status='RUNNING',
                result='PENDING'
            )

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('user', 'round', 'color', 'amount', 'status', 'payout')
    list_filter = ('status', 'color')
    search_fields = ('user__username', 'round__round_id')
