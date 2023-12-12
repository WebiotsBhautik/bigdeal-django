import random
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete,pre_delete
import faker
from accounts.models import CustomUser
from order.models import Order, OrderPayment, OrderTracking, ProductOrder
from product.models import ProBrand, ProCategory, ProUnit, ProVideoProvider
from bigdealapp.models import ContactUs

fake = faker.Faker()
vendors = CustomUser.objects.filter(is_vendor=True)
proCategorys=ProCategory.objects.all()
productBrands=ProBrand.objects.all()
productUnits=ProUnit.objects.all()
productVideoProviders=ProVideoProvider.objects.all()
productTypes = ['Simple']
productStatuss=[True]


# Signal for to delete all order related objects | Use only for developement purpose 
@receiver(pre_delete, sender=ContactUs)
def contact_us_pre_delete(sender, instance, **kwargs):
    order= Order.objects.all()
    order.delete()
    porder=ProductOrder.objects.all()
    porder.delete()
    orderTracking=OrderTracking.objects.all()
    orderTracking.delete()
    orderPayment=OrderPayment.objects.all()
    orderPayment.delete()