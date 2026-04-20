from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

class Wallet(models.fields.Field):
    pass # to satisfy linters before class def

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet - ${self.balance}"

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('WIN', 'Win'),
        ('LOSS', 'Loss'),
        ('BET', 'Bet'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ${self.amount}"

class Round(models.Model):
    STATUS_CHOICES = (
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
    )
    RESULT_CHOICES = (
        ('PENDING', 'Pending'),
        ('RED', 'Red'),
        ('GREEN', 'Green'),
        ('VIOLET', 'Violet'),
    )
    
    round_id = models.CharField(max_length=20, unique=True, blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='RUNNING')
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='PENDING')

    def save(self, *args, **kwargs):
        if not self.round_id:
            self.round_id = str(uuid.uuid4())[:8].upper()
        if not self.end_time:
            self.end_time = self.start_time + timezone.timedelta(seconds=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Round {self.round_id} - {self.status}"

class Trade(models.Model):
    COLOR_CHOICES = (
        ('RED', 'Red'),
        ('GREEN', 'Green'),
        ('VIOLET', 'Violet'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('WIN', 'Win'),
        ('LOSS', 'Loss'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.color} - ${self.amount}"
