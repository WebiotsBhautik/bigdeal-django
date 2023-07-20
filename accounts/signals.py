from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_protect

from accounts.models import Admin, Customer, CustomUser, TemporaryData, Vendor


@receiver(post_save, sender=CustomUser)
def customer_update_profile_signal(sender, instance, created, **kwargs):
    # Signal handler for creating a Customer profile when a CustomUser is saved.
    if instance.is_customer == True:
        if created:
            Customer.objects.create(customer=instance, customerName=instance.username).save()


@receiver(post_save, sender=CustomUser)
def vendor_update_profile_signal(sender, instance, created, **kwargs):
    # Signal handler for creating a Vendor profile when a CustomUser is saved.
    if instance.is_vendor == True:
        if created:
            Vendor.objects.create(vendor=instance, vendorName=instance.username).save()


@receiver(post_save, sender=CustomUser)
def signal_for_temporary_data_creation(sender, instance, created, **kwargs):
    # Signal handler for creating TemporaryData when a CustomUser is saved.
    if created:
        TemporaryData.objects.create(TemporaryDataByUser=instance).save()


@receiver(post_save, sender=CustomUser)
def admin_update_profile_signal(sender, instance, created, **kwargs):
    # Signal handler for creating an Admin profile when a CustomUser is saved and is_superuser is True.
    if instance.is_superuser == True:
        if created:
            Admin.objects.create(admin=instance, adminName=instance.username).save()

