from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Round, Trade, Wallet, Transaction
from decimal import Decimal, InvalidOperation

@login_required
def home(request):
    # Ensure a wallet exists securely
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    # Get the current running round, if multiple take first
    current_round = Round.objects.filter(status='RUNNING').order_by('-start_time').first()
    
    if not current_round:
        # Auto start a round if none exists
        current_round = Round.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(seconds=30),
            status='RUNNING'
        )

    time_remaining = 0
    if current_round.end_time:
        diff = (current_round.end_time - timezone.now()).total_seconds()
        time_remaining = max(0, int(diff))

    context = {
        'round': current_round,
        'time_remaining': time_remaining,
        'wallet': wallet,
    }
    return render(request, 'home.html', context)

@login_required
def place_trade(request):
    if request.method == 'POST':
        round_id = request.POST.get('round_id')
        color = request.POST.get('color')
        amount_str = request.POST.get('amount')

        if not color or not amount_str:
            messages.error(request, "Missing color or amount.")
            return redirect('home')

        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            messages.error(request, "Invalid amount.")
            return redirect('home')

        if amount <= 0:
            messages.error(request, "Amount must be greater than zero.")
            return redirect('home')

        wallet = request.user.wallet
        if wallet.balance < amount:
            messages.error(request, "Insufficient balance.")
            return redirect('home')

        current_round = get_object_or_404(Round, id=round_id)
        if current_round.status != 'RUNNING' or timezone.now() >= current_round.end_time:
            messages.error(request, "This round has already closed.")
            return redirect('home')

        # Deduct balance
        wallet.balance -= amount
        wallet.save()

        # Create record
        Trade.objects.create(
            user=request.user,
            round=current_round,
            color=color,
            amount=amount
        )
        Transaction.objects.create(
            user=request.user,
            amount=amount,
            transaction_type='BET'
        )

        messages.success(request, f"Successfully placed custom bet of ${amount} on {color}.")
    return redirect('home')

@login_required
def wallet_view(request):
    wallet = request.user.wallet
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'wallet.html', context)

@login_required
def history_view(request):
    trades = Trade.objects.filter(user=request.user).order_by('-timestamp')
    context = {
        'trades': trades,
    }
    return render(request, 'history.html', context)

@login_required
def account_view(request):
    wallet = request.user.wallet
    return render(request, 'account.html', {'wallet': wallet})

@login_required
def agency_view(request):
    return render(request, 'agency.html')

@login_required
def subordinate_data_view(request):
    return render(request, 'subordinate_data.html')

@login_required
def commission_detail_view(request):
    return render(request, 'commission_detail.html')

@login_required
def invitation_rules_view(request):
    return render(request, 'invitation_rules.html')

@login_required
def withdraw_history_view(request):
    return render(request, 'withdraw_history.html')
