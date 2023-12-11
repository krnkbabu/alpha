from django.urls import path
from billingapp.views import (index, ProductCreateView, ProductListView, ProductDetailView, ProductUpdateView, productsjson,
	VendorCreateView, VendorListView, VendorDetailView, VendorUpdateView, VendorDeleteView,
	CustomerCreateView, CustomerListView, CustomerDetailView, CustomerUpdateView, customersjson,
	InventoryListView,
	invoice_create,
	)

app_name = 'billingapp'

urlpatterns = [
	path('',index, name='billing_home'),
	path('product-entry/',ProductCreateView.as_view(), name = 'entry_product'),
	path('product-list/', ProductListView.as_view(), name = 'list_product'),
	path('product-detail/<int:pk>',ProductDetailView.as_view(),name = 'detail_product'),
	path('product-update/<int:pk>',ProductUpdateView.as_view(),name = 'update_product'),
	path('productsjson', productsjson, name='productsjson'),

	path('vendor-list/',VendorListView.as_view(), name = 'list_vendor'),
	path('vendor-entry/',VendorCreateView.as_view(), name = 'entry_vendor'),
	path('vendor-detail/<int:pk>',VendorDetailView.as_view(),name = 'detail_vendor'),
	path('vendor-update/<int:pk>',VendorUpdateView.as_view(),name = 'update_vendor'),
	path('vendor-delete/<int:pk>',VendorDeleteView.as_view(),name = 'delete_vendor'),

	path('customer-entry/',CustomerCreateView.as_view(), name = 'entry_customer'),
	path('customer-list/',CustomerListView.as_view(), name = 'list_customer'),
	path('customer-detail/<int:pk>',CustomerDetailView.as_view(),name = 'detail_customer'),
	path('customer-update/<int:pk>',CustomerUpdateView.as_view(),name = 'update_customer'),
    path('customersjson', customersjson, name='customersjson'),
	
	path('inventory-list/', InventoryListView.as_view(), name = 'list_inventory'),
	
	path('invoices/new', invoice_create, name='create_invoice'),


	
    

	]