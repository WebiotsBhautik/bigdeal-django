from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from bigdeal.settings import MESSAGE_TAGS
from .models import CustomUser, TemporaryData
from django.http import HttpResponseRedirect
from django.urls import path
from .models import Admin, CustomUser
from accounts.models import Vendor, Customer, CustomUser
from django.utils.safestring import mark_safe
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import admin, messages


# admin.site.register(Permission)
# admin.site.register(Group)

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password*', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation*', widget=forms.PasswordInput)
    # is_vendor = forms.BooleanField(
    #     label='Vendor', widget=forms.CheckboxInput, required=False)
    # is_customer = forms.BooleanField(
    #     label='Customer', widget=forms.CheckboxInput, required=False)
    is_active = forms.BooleanField(label='Status', widget=forms.CheckboxInput, required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'username')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Password does Not Match")
        return password2
    
    def clean(self):
        cleaned_data = super().clean()
        groups = self.cleaned_data.get('groups')       
        self.cleaned_groups = groups
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        groups = self.cleaned_groups
        if groups:
            for grp in groups:
                if grp.name == "Vendor":
                    user.is_vendor=True
                if grp.name == "Customer":
                    user.is_customer=True
        if commit:
            user.save()
        return user
    

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    is_active = forms.BooleanField(label='Status', widget=forms.CheckboxInput, required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'username')
        
    def clean(self):
        cleaned_data = super().clean()     
        return cleaned_data

class CustomUserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('username', 'email','is_vendor', 'is_customer','is_admin','is_superuser','is_staff',
                    'get_role', 'is_active', 'created_at')
    ordering=['-created_at']
    # show_full_result_count=True
    
    # Display on Creating New Object   
    fieldsets = (
        (None, {'fields': ('username', 'email', 'profilePicture', 'is_active', 'groups',)}),)
        # (None, {'fields': ('username', 'email', 'profilePicture', 'is_active', 'is_vendor', 'is_customer', 'groups',)}),)
    
    # Display on Edting Existing Object
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'profilePicture', 'password1', 'password2', 'is_active', 'groups',),
            # 'fields': ('username', 'email', 'profilePicture', 'password1', 'password2', 'is_active', 'is_vendor', 'is_customer', 'groups',),
        }),
    )
    list_filter = ()
    list_per_page=10
   
    search_fields = ['username', 'email']
    # list_editable = ('is_active',) 

    @admin.display(description='Role')
    def get_role(self, obj):
        role=" | ".join([str(gp) for gp in obj.groups.all()])
        return "Staff User" if role=="" else role        

    @mark_safe
    def user_avtar(self, obj):
        return f'<img src="{obj.profilePicture.url}" height="30px" width="30px"/>'
    user_avtar.short_description = 'Avtar'

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
        }
        return super().get_form(request, obj, **kwargs)
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('delete_selected_user/', self.delete_selected_user),
        ]
        return my_urls + urls

    def delete_selected_user(self, request):
        self.model.objects.all().update(is_active=True)
        self.message_user(request, "Selected Users are deleted.")
        return HttpResponseRedirect("../")
    
    # New Code Added Start =================================================================
    
    def response_add(self, request, obj, post_url_continue=None):
        if '_addanother' not in request.POST:
            return self.response_post_save_add(request, obj)
        else:
            return super().response_add(request, obj, post_url_continue)

    def response_post_save_add(self, request, obj):
        return HttpResponseRedirect('../')   
    
    def delete_queryset(self, request, queryset):
        if queryset.filter(is_admin=True).exists():
            print('=================================================>NOT DELETED ')
            messages.error(request, "Superuser cannot be deleted.")
            self.message_user(request, "You cannot delete a Super Admin", level=messages.ERROR)
        

        else:
            super().delete_queryset(request, queryset)
    
    def delete_model(self, request, obj):
        if obj.is_admin:
            # messages.error(request, "Superuser cannot be deleted.")
            self.message_user(request, "You cannot delete a Super Admin", level=messages.ERROR)
        else:
            super().delete_model(request, obj)
    
    # New Code Added End =================================================================


    
admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('adminName','admin','adminContact','adminWalletBalance','created_at')
    
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendorName','vendor','vendorContact','vendorGst','vendorWalletBalance','created_at')

@admin.register(TemporaryData)
class TemporaryDataAdmin(admin.ModelAdmin):
    list_display = ('TemporaryDataByUser','otpNumber','otpExpiryTime')
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customerName','customer','customerContact','customerWalletBalance','created_at')
