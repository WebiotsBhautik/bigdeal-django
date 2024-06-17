from django.db import models
import uuid
from django.utils.text import slugify
from accounts.get_username import get_request
from accounts.models import CustomUser
from django.core.validators import MinValueValidator

# Create your models here.

class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cardType = models.CharField(max_length=255)
    
    def __str__(self):
        return self.cardType
    
    
    
class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    walletByUser = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='User')
    walletBalance = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='Balance',blank=True,null=True)
    walletCreatedAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    walletModifiedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')
    
    def __str__(self):
        return str(self.walletByUser)
    class Meta:
        verbose_name = 'Wallet'
        
        
class WalletHistory(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4 ,editable= False )
    walletHistoryByUser = models.ForeignKey(Wallet, on_delete=models.CASCADE,verbose_name='User')
    walletHistoryOfOrderId=models.CharField(max_length=255,blank=True,null=True,verbose_name='Order ID')
    walletHistoryOfOrderTransactionId=models.CharField(max_length = 255,editable=False,blank=True,null=True,verbose_name='Transaction Id')
    walletHistoryOfTrackingId=models.CharField(max_length=255,blank=True,null=True,verbose_name='Tracking ID')
    walletHistoryCredit=models.DecimalField(default=0,max_digits=10, decimal_places=2,verbose_name='Credited',blank=True,null=True)
    walletHistoryDebit=models.DecimalField(default=0,max_digits=10, decimal_places=2,verbose_name='Debited',blank=True,null=True)
    walletHistoryBalance=models.DecimalField(default=0,max_digits=10, decimal_places=2,verbose_name='Balance',blank=True,null=True)
    walletHistoryCreatedAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    walletHistoryModifiedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')
    
    def __str__(self):
        return str(self.walletHistoryByUser)
    
    class Meta:
        verbose_name ='Wallet History'
        verbose_name_plural = 'Wallet History'
        
        
class Withdrawal(models.Model):
    paymentOptionChoices = [('Bank', 'Bank'), ('PayPal', 'PayPal'), ('RazorPay', 'RazorPay')]
    statusOptionChoices = [('Pending', 'Pending'), ('Approve', 'Approve'), ('Rejected', 'Rejected')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    withdrawalByUser = models.ForeignKey(CustomUser, on_delete=models.CASCADE,verbose_name='User')
    withdrawalAmount = models.DecimalField(validators=[MinValueValidator(1,message='Amount must be greater then 0.')],max_digits=10, decimal_places=2,verbose_name='Amount')
    withdrawalPaymentOption = models.CharField(max_length=255,default='Bank',choices=paymentOptionChoices, verbose_name='Payment Option')
    withdrawalMessage = models.TextField(verbose_name='Note',blank=True)
    withdrawalStatus = models.CharField(max_length=255,default='Pending',choices=statusOptionChoices, verbose_name='Status')
    createdAt = models.DateTimeField(auto_now_add=True,verbose_name='Created At')
    modifiedAt = models.DateTimeField(auto_now=True,verbose_name='Updated At')
    
    def save(self, *args, **kwargs):
        req = get_request().user
        self.withdrawalByUser = req
        
        super(Withdrawal, self).save(*args, **kwargs)
        
    def __str__(self):
        return str(self.withdrawalAmount)
    
    class Meta:
        verbose_name = 'Withdrawal'