from django.contrib import admin
from django import forms
from accounts.get_username import get_request
from accounts.models import Admin, Vendor
from .models import Card,Wallet,WalletHistory,Withdrawal
# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class WalletAdmin(BaseModelAdmin):
    list_display = ['walletByUser','walletBalance','walletModifiedAt']
    ordering = ['-walletCreatedAt']
    
    def get_queryset(self,request):
        if request.user.is_vendor:
            queryset = super(WalletAdmin, self).get_queryset(request)
            return queryset.filter(walletByUser=request.user)
        else:
            queryset = super(WalletAdmin, self).get_queryset(request)
            return queryset
        
admin.site.register(Wallet,WalletAdmin)

class WalletHistoryAdmin(BaseModelAdmin):
    list_display=['walletHistoryByUser','walletHistoryCredit','walletHistoryDebit','walletHistoryBalance','walletHistoryOfOrderId','walletHistoryOfOrderTransactionId','walletHistoryOfTrackingId','walletHistoryModifiedAt']
    ordering=['-walletHistoryCreatedAt']
    
    def get_queryset(self, request):
        if request.user.is_vendor:  
            queryset = super(WalletHistoryAdmin, self).get_queryset(request)
            return queryset.filter(walletHistoryByUser__walletByUser=request.user)
        else:
            queryset = super(WalletHistoryAdmin, self).get_queryset(request)
            return queryset.filter(walletHistoryByUser__walletByUser=request.user)

admin.site.register(WalletHistory,WalletHistoryAdmin)



class WithdrawalAdminForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = '__all__'

    def clean_withdrawalAmount(self):
        withdrawal_amount = self.cleaned_data['withdrawalAmount']
        user = get_request().user
        wallet = Wallet.objects.get(walletByUser=user)
        adminUser=Admin.objects.get(admin__email="admin@gmail.com")
        
        if withdrawal_amount > wallet.walletBalance:
            raise forms.ValidationError('Insufficient wallet balance to withdraw')
        
        if withdrawal_amount < adminUser.minimumWithdrawalAmount:
            raise forms.ValidationError('Amount must be greater than minimum withdrawal amount.')
        return withdrawal_amount
        
    def clean_withdrawalPaymentOption(self):
        user = get_request().user
        withdrawalPaymentOption = self.cleaned_data['withdrawalPaymentOption']
        vendorProfile = Vendor.objects.get(vendor=user)
        
        if withdrawalPaymentOption == 'Bank':
            if vendorProfile.bankName=="" or vendorProfile.bankAccountName=="" or vendorProfile.bankAccountNumber=="" or vendorProfile.bankIFSCCode=="" or vendorProfile.bankSWIFTCode=="":
                raise forms.ValidationError('Please fill all bank details in your profile.')
        if withdrawalPaymentOption == 'RazorPay':
            if vendorProfile.razorPayEmailId == "":
                raise forms.ValidationError('Please fill RazorPay details in your profile.')
        if withdrawalPaymentOption == 'PayPal':
            if vendorProfile.payPalEmailId == "":
                raise forms.ValidationError('Please fill PayPal details in your profile.')
        return withdrawalPaymentOption

class WithdrawalAdmin(BaseModelAdmin):
    form = WithdrawalAdminForm
    exclude = ['withdrawalByUser']
    list_display=['withdrawalByUser','withdrawalPaymentOption','withdrawalAmount','withdrawalStatus','withdrawalMessage',]
    ordering=['-createdAt']

    def get_queryset(self, request):
       
        if request.user.is_vendor:  
            queryset = super(WithdrawalAdmin, self).get_queryset(request)
            return queryset.filter(withdrawalByUser=request.user)
        else:
            queryset = super(WithdrawalAdmin, self).get_queryset(request)
            return queryset
            
    def get_exclude(self, request, obj=None):
        if request.user.is_vendor:
            return ['withdrawalByUser', 'withdrawalStatus']
        else:
            return super().get_exclude(request, obj)
   
admin.site.register(Withdrawal,WithdrawalAdmin)


        


