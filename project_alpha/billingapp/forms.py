from django.forms import ModelForm
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from .models import Vendor, Customer, Inventory, Product

class VendorForm(ModelForm):
	class Meta:
       		model =	Vendor
       		fields='__all__'
	        widgets = {
	            'vendor_phone1': PhoneNumberPrefixWidget(initial='IN'),
	            'vendor_phone2': PhoneNumberPrefixWidget(initial='IN'),
            }


class CustomerForm(ModelForm):
	class Meta:
       		model =	Customer
       		fields='__all__'
	        widgets = {
	            'customer_phone': PhoneNumberPrefixWidget(initial='IN'),
	            'customer_phone2': PhoneNumberPrefixWidget(initial='IN'),
            }

class InventoryForm(ModelForm):
	class Meta:
		model = Inventory
		exclude = ['product']


class ProductInventoryForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
