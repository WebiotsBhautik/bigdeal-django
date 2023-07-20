from datetime import datetime, timedelta
# import datetime
import uuid
from django import forms
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from accounts.managers import CustomUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group
from django.utils.html import mark_safe


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    email = models.EmailField(
        max_length=255, unique=True, verbose_name='Email')
    username = models.CharField(
        max_length=200, verbose_name='Name')
    profilePicture = models.ImageField(
        verbose_name='Avtar', blank=True, null=True, upload_to='fashion/user')
    is_active = models.BooleanField(default=True, verbose_name='Status')
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_vendor = models.BooleanField(default=False,editable=False)
    is_customer = models.BooleanField(default=False,editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_superuser(self):
        return self.is_admin
        


    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):   
        selected_groups = self.groups.all()
        if selected_groups:
            for grp in selected_groups:
                # grpList.append(str(grp.name))
                if grp.name == "Customer":
                    self.is_customer=True
                if grp.name == "Vendor":
                    self.is_vendor=True
        
        if self.is_customer:
            self.is_staff=False
        super(CustomUser, self).save(*args, **kwargs)

# Two Vendor and Customer user models =========================================================

class Vendor(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    vendor = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, verbose_name='Email')
    # ,related_name='ven'
    vendorName = models.CharField(max_length=200, verbose_name='Name')
    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    vendorContact = models.CharField(
        validators=[phoneNumberRegex], max_length=16, unique=False, verbose_name='Contact')
    vendorGst = models.CharField(max_length=15, verbose_name='GST No.')
    vendorAddress = models.TextField(
        blank=True, null=True, verbose_name='Address')
    vendorWalletBalance=models.DecimalField(default=0,max_digits=10, decimal_places=2,verbose_name='Wallet Balance',blank=True,null=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    # def __str__(self):
    #     return str(self.vendor)


class Customer(models.Model):   
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    customer = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, verbose_name='Email')
    # related_name='cust',
    customerName = models.CharField(
        max_length=200, blank=True, null=True, verbose_name='Name')
    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    customerContact = models.CharField(
        validators=[phoneNumberRegex], max_length=16, unique=False, verbose_name='Contact')
    customerAddress = models.TextField(
        blank=True, null=True, verbose_name='Address')
    customerWalletBalance=models.DecimalField(default=0,max_digits=10, decimal_places=2,verbose_name='Wallet Balance',blank=True,null=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    # def __str__(self):
    #     return str(self.customers)

class Admin(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    admin = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, verbose_name='Email')
    # related_name='cust',
    adminName = models.CharField(
        max_length=200, blank=True, null=True, verbose_name='Name')
    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    adminContact = models.CharField(
        validators=[phoneNumberRegex], max_length=16, unique=False, verbose_name='Contact')
    adminAddress = models.TextField(blank=True, null=True, verbose_name='Address')
    adminWalletBalance=models.DecimalField(default=0,max_digits=10, decimal_places=2,verbose_name='Wallet Balance',blank=True,null=True)
    adminCommissionProfit=models.DecimalField(default=0,max_digits=10, decimal_places=2,verbose_name='Commission Profit',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        verbose_name_plural = 'Admin Profiles'


class TemporaryData(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    TemporaryDataByUser = models.ForeignKey(CustomUser,on_delete=models.CASCADE, verbose_name='User')
    otpNumber = models.CharField(max_length=50, blank=False, null=True)
    otpExpiryTime = models.DateTimeField(blank=True,null=True)
    
    def __str__(self):
        return str(self.TemporaryDataByUser) 
    
    class Meta:
        verbose_name_plural = 'Temporary Data'