from django.contrib.auth.models import BaseUserManager,Group


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, is_vendor, is_customer, password=None):
        if not email:
            raise ValueError('User must have to enter email...')
        user = self.model(email=self.normalize_email(email))
        user.username = username
        user.is_vendor = is_vendor
        user.is_customer = is_customer
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,username,password=None):
        if not email:
            raise ValueError('User must have to enter email...')
        user = self.model(email=self.normalize_email(email))
        user.username=username
        user.set_password(password)
        user.is_admin = True
        user.role = None

        user.save(using=self._db)
        
        
        try:
            vendor_group = Group.objects.get(name='Vendor')
            customer_group = Group.objects.get(name='Customer')
            user.groups.add(vendor_group, customer_group)
        except Group.DoesNotExist:
            pass
        
        return user
