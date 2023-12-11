from django.contrib import admin
from billingapp.models import (Product, Vendor, Inventory, Customer, Invoice, InventoryLog, Book, BookLog)

# Register your models here.

admin.site.register(Product)
admin.site.register(Vendor)
admin.site.register(Inventory)
admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(InventoryLog)
admin.site.register(Book)
admin.site.register(BookLog)