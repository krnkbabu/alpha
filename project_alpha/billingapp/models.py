from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime

from django.core.validators import MaxValueValidator,RegexValidator
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.

# ======================= Invoice Data models =================================

pincode_regex = "^[1-9]{1}[0-9]{2}\\s{0,1}[0-9]{3}$"


class Vendor(models.Model):
	"""docstring for Vendor"""		
	vendor_id = models.AutoField(primary_key=True, editable=False, unique = True)
	vendor_name = models.CharField(unique = True, max_length=255, )
	vendor_poc = models.CharField(max_length=40)
	vendor_gst = models.CharField(unique = True, max_length=20, )
	vendor_address = models.TextField(verbose_name='Official Address', blank = True)
	# vendor_pincode = models.CharField(max_length=6)
	vendor_pincode = models.CharField(max_length=6, validators = [RegexValidator(regex=pincode_regex, message='Enter Valid Pincode!')], default='600006')
	vendor_phone1 = PhoneNumberField(verbose_name='Primary Contact Number')
	vendor_phone2 = PhoneNumberField(verbose_name='Secondary Contact Number', blank = True)

	def get_absolute_url(self):
		return reverse("billingapp:detail_vendor",kwargs={'pk':self.pk})

	def __str__(self):
		return f'{self.vendor_name}'
		

class Product(models.Model):
	"""docstring for Product"""
	product_id = models.AutoField(primary_key=True, editable=False, unique = True)
	vendors = models.ManyToManyField('Vendor', related_name='products')
	product_code = models.CharField(unique = True, max_length=20, )
	product_name = models.CharField(blank = True, max_length=50)
	product_hsn = models.CharField(max_length=50, null=True, blank=True)
	product_unit = models.CharField(max_length=50, default='Nos')
	# Inventory = 
	# product_category = 
	product_description = models.CharField(blank = True, max_length=100)
	product_cost_price = models.IntegerField(validators=[MaxValueValidator(20000)])
	product_gst_percentage = models.FloatField(default=5)
	product_remarks = models.TextField(blank = True, verbose_name='Remarks')
	
	def get_absolute_url(self):
		return reverse("billingapp:detail_product",kwargs={'pk':self.pk})

	def __str__(self):
		return f'{self.product_code}, {self.product_name},'


class Customer(models.Model):
	"""docstring for customer"""		
	customer_id = models.AutoField(primary_key=True, editable=False, unique = True)
	customer_name = models.CharField(unique = True, max_length=255, )
	customer_poc = models.CharField(max_length=40)
	customer_gst = models.CharField(unique = True, max_length=20, )
	customer_address = models.TextField(verbose_name='Official Address', blank = True)
	customer_pincode = models.CharField(max_length=6, validators = [RegexValidator(regex=pincode_regex, message='Enter Valid Pincode!')])
	customer_phone = PhoneNumberField(verbose_name='Primary Contact Number')
	customer_phone2 = PhoneNumberField(verbose_name='Secondary Contact Number', blank = True)

	def get_absolute_url(self):
		return reverse("billingapp:detail_customer",kwargs={'pk':self.pk})

	def __str__(self):
		return self.customer_name

class Invoice(models.Model):
	user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
	invoice_number = models.CharField(max_length=20, unique=True)
	invoice_date = models.DateField(auto_now_add=True)
	customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices')
	
	taxable_amount = models.DecimalField(max_digits=10, decimal_places=2)
	cgst = models.DecimalField(max_digits=5, decimal_places=2)
	sgst = models.DecimalField(max_digits=5, decimal_places=2)
	igst = models.DecimalField(max_digits=5, decimal_places=2)
	total_amount = models.DecimalField(max_digits=10, decimal_places=2)

	invoice_json = models.TextField()
	inventory_reflected = models.BooleanField(default=True)
	books_reflected = models.BooleanField(default=True)

	# def save(self, *args, **kwargs):
	#     if not self.invoice_number:
	#         # Auto-increment invoice number if not set
	#         last_invoice = Invoice.objects.all().order_by('invoice_number').last()
	#         if last_invoice:
	#             self.invoice_number = last_invoice.invoice_number + 1
	#         else:
	#             # If no previous invoices, start from 1
	#             self.invoice_number = 1
	#     super().save(*args, **kwargs)    

	def __str__(self):
		return f'{self.invoice_number} | {self.invoice_date}'


# ========================= Inventory Data models ====================================

class InventoryLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    change = models.IntegerField(default=0)
    CHANGE_TYPES = [
        (0, 'Other'),
        (1, 'Purchase'),
        (2, 'Production'),
        (4, 'Sales'),
    ]
    change_type = models.IntegerField(choices=CHANGE_TYPES, default=0)

    associated_invoice = models.ForeignKey(Invoice, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    description = models.TextField(max_length=600, blank=True, null=True)

    def __str__(self):
        return self.product.product_name + " | " + str(self.change) + " | " + self.description + " | " + str(self.date)


class Inventory(models.Model):
	inventory_id = models.AutoField(primary_key=True,editable=False,blank=True,)
	product = models.OneToOneField('Product',related_name='inventories', on_delete=models.CASCADE)
	inv_available = models.IntegerField(blank=True)
	inv_allocated = models.IntegerField(blank=True)

	def __str__(self):
		return f'{self.product.product_code}'



# ========================= Books Data models ======================================

class Book(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    current_balance = models.FloatField(default=0)
    last_log = models.ForeignKey('BookLog', null=True, blank=True, default=None, on_delete=models.SET_NULL)

    def __str__(self):
        return self.customer.customer_name


class BookLog(models.Model):
    parent_book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    CHANGE_TYPES = [
        (0, 'Paid'),
        (1, 'Purchased Items'),
        (2, 'Sold Items'),
        (4, 'Other'),
    ]
    change_type = models.IntegerField(choices=CHANGE_TYPES, default=0)
    change = models.FloatField(default=0.0)

    associated_invoice = models.ForeignKey(Invoice, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    description = models.TextField(max_length=600, blank=True, null=True)

    def __str__(self):
        return self.parent_book.customer.customer_name + " | " + str(self.change) + " | " + self.description + " | " + str(self.date)

