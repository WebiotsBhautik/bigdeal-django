from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save
from accounts.models import CustomUser
from .models import Wallet,Withdrawal


@receiver(post_save, sender=CustomUser)
def signal_to_create_wallet(sender,instance,created,**kwargs):
    if created:
        Wallet.objects.create(walletByUser=instance).save()
        
        
@receiver(pre_save, sender=Withdrawal)
def withdrawal_status_changed(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        currentInstance = instance
        try:
            previusInstance = Withdrawal.objects.get(id=instance.id)
            if currentInstance.withdrawalStatus=="Rejected" and currentInstance.withdrawalStatus != previusInstance.withdrawalStatus:
                user = instance.withdrawalByUser
                wallet = Wallet.objects.get(walletByUser=user)
                wallet.walletBalance = wallet.walletBalance + instance.withdrawalAmount
                wallet.save()
        except Withdrawal.DoesNotExist:
            # Handle the case where the previous instance doesn't exist
            pass
        
        
@receiver(post_save, sender=Withdrawal)
def signal_manage_wallet_amount_after_new_withdrawal_request_creation(sender, instance, created, **kwargs):
    if created:
        user = instance.withdrawalByUser
        wallet = Wallet.objects.get(walletByUser=user)
        wallet.walletBalance = wallet.walletBalance - instance.withdrawalAmount
        wallet.save()
        
        
        
        
    
        
        