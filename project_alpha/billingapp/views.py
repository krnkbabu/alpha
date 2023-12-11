import datetime
import json
# import num2words

from django.shortcuts import (render, get_object_or_404, redirect)
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Max
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumber

from .utils import (
                    invoice_data_validator,
                    invoice_data_processor,
                    add_customer_book,
                    auto_deduct_book_from_invoice,
                    update_inventory,
                    update_products_from_invoice
                    )

from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from .models import Product, Vendor, Inventory, Invoice, Customer
from .forms import	(VendorForm, CustomerForm, InventoryForm)


# Create your views here.

def index(req):
	return render(req, 'billingapp/billingapp_base.html')


#Product CRUDs

class ProductCreateView(CreateView):
    model = Product
    # template_name = "product_form.html" (By default)
    # form_class = ProductForm
    fields = '__all__'
    success_url = reverse_lazy('billingapp:list_product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['product_form'] = context['form'] OR
        context['product_form'] = self.get_form()
        context['inventory_form'] = InventoryForm()
        return context

    def form_valid(self, form):
        inventory_form = InventoryForm(self.request.POST)
        if inventory_form.is_valid():
            p = form.save()
            i = inventory_form.save(commit=False)
            i.product = p
            i.save()
        return super().form_valid(form)

    # def form_valid(self, p_form):
    #     inventory_form = InventoryForm()

    #     if inventory_form.is_valid():
    #         p_id = p_form.save()
    #         inv_id = inventory_form.save(commit=False)
    #         inv_id.product = p_id
    #         inv_id.save()

    #     return super().form_valid(p_form)


class ProductListView(ListView):
    model = Product
    # template_name = "product_list.html" (By default)


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product' #default is also same:<model_name>

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_obj = context['product']
        context['vendiz'] = product_obj.vendors.all()
        return context


class ProductUpdateView(UpdateView):
    model = Product
    fields = '__all__'
    success_url = reverse_lazy('billingapp:list_product')
    # forms = [InventoryForm,]
    # template_name = "billingapp/productinventoryupdate_form.html"
     # template_name = "product_form.html" (By default)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['product_form'] = context['form'] OR
        context['product_form'] = self.get_form()
        context['inventory_form'] = InventoryForm(instance=self.object.inventories)
        return context

    def form_valid(self, form):
        x = super().form_valid(form)
        inventory_form = InventoryForm(self.request.POST, instance=self.object.inventories)
        if inventory_form.is_valid():
            inventory_form.save()
        return x

    # def form_valid(self, p_form):
    #     p_id = p_form.save()
    #     inv_id = Inventory.objects.get(product = p_id)
    #     inv_id.inv_available = p_id['inv_available']
    #     inv_id.inv_allocated = p_id['inv_allocated']      
    #     return super().form_valid(p_form)


#Vendor  CRUDs

class VendorCreateView(CreateView):
    model = Vendor
    form_class = VendorForm
    success_url = reverse_lazy('billingapp:list_vendor')
   # template_name = "vendor_form.html" (By default)

class VendorListView(ListView):
    model = Vendor
   # template_name = "vendor_list.html" (By default)


class VendorDetailView(DetailView):
    model = Vendor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor_obj = context['vendor']
        context['productz'] = vendor_obj.products.all()
        return context


class VendorUpdateView(UpdateView):
    model = Vendor
    fields = '__all__'
    success_url = reverse_lazy('billingapp:list_vendor')


class VendorDeleteView(DeleteView):
    model = Vendor
    success_url = reverse_lazy('billingapp:list_vendor')
    # template_name = "vendor_confirm_delete.html"(Default)


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy('billingapp:list_customer')
   # template_name = "customer_form.html" (By default)


class CustomerListView(ListView):
    model = Customer
   # template_name = "customer_list.html" (By default)


class CustomerDetailView(DetailView):
    model = Customer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_obj = context['customer']
        context['invoicez'] = customer_obj.invoices.all()
        return context


class CustomerUpdateView(UpdateView):
    model = Customer
    fields = '__all__'
    success_url = reverse_lazy('billingapp:list_customer')

#Inventory CRUD
class InventoryListView(ListView):
    model = Inventory
    #template_name = 'inventory_list.html'(Default)


class InventoryCreateView(CreateView):
    model = Inventory
    fields = '__all__'
    success_url = reverse_lazy('billingapp:list_inventory')
    # template_name = "inventory_form.html" (By default)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['product_form'] = context['form'] OR
        context['inventory_form'] = self.get_form()
        return context




# Invoice, products and customers ===============================================

def invoice_create(request):
    # if business info is blank redirect to update it
   
    # user_profile = get_object_or_404(User, user=request.user)
    # if not user_profile.business_title:
    #     return redirect('user_profile_edit')

    context = {}
    context['default_invoice_number'] = int(Invoice.objects.aggregate(Max('invoice_number'))['invoice_number__max'])
    if not context['default_invoice_number']:
        context['default_invoice_number'] = 1
    else:
        context['default_invoice_number'] += 1

    context['default_invoice_date'] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')

    if request.method == 'POST':
        print("POST received - Invoice Data")

        invoice_data = request.POST

        validation_error = invoice_data_validator(invoice_data)

        if validation_error:
            context["error_message"] = validation_error
            return render(request, 'billingapp/invoice_create.html', context)

        # valid invoice data
        print("Valid Invoice Data")

        invoice_data_processed = invoice_data_processor(invoice_data)
        # save customer
        customer = None

        try:
            customer = Customer.objects.get(
                                            # user=request.user,
                                            customer_name=invoice_data['customer-name'],
                                            customer_address=invoice_data['customer-address'],
                                            customer_phone=invoice_data['customer-phone'],
                                            customer_gst=invoice_data['customer-gst'])
        except:
            print("===============> customer not found")
            print(invoice_data['customer-name'])
            print(invoice_data['customer-address'])
            print(invoice_data['customer-phone'])
            print(invoice_data['customer-gst'])

        if not customer:
            print("CREATING CUSTOMER===============>")
            customer = Customer(
                # user=request.user,
                customer_name=invoice_data['customer-name'],
                customer_address=invoice_data['customer-address'],
                customer_phone=invoice_data['customer-phone'],
                customer_gst=invoice_data['customer-gst'])
            # create customer book
            customer.save()
            add_customer_book(customer)

        # save product
        update_products_from_invoice(invoice_data_processed, 
                                    # request
                                    )


        # save invoice
        invoice_data_processed_json = json.dumps(invoice_data_processed)
        new_invoice = Invoice(
                              # user=request.user,
                              invoice_number=int(invoice_data['invoice-number']),
                              invoice_date=datetime.datetime.strptime(invoice_data['invoice-date'], '%Y-%m-%d'),
                              customer=customer, invoice_json=invoice_data_processed_json)
        new_invoice.save()
        print("INVOICE SAVED")

        # update_inventory(new_invoice, request)
        # print("INVENTORY UPDATED")

        auto_deduct_book_from_invoice(new_invoice)
        print("CUSTOMER BOOK UPDATED")

        return redirect('billingapp/product_list.html')
        # return redirect('invoice_viewer', invoice_id=new_invoice.id)

    return render(request, 'billingapp/invoice_create.html', context)



def invoices(request):
    context = {}
    context['invoices'] = Invoice.objects.filter(user=request.user).order_by('-id')
    return render(request, 'gstbillingapp/invoices.html', context)



# def invoice_viewer(request, invoice_id):
#     invoice_obj = get_object_or_404(Invoice, user=request.user, id=invoice_id)
#     user_profile = get_object_or_404(UserProfile, user=request.user)

#     context = {}
#     context['invoice'] = invoice_obj
#     context['invoice_data'] = json.loads(invoice_obj.invoice_json)
#     print(context['invoice_data'])
#     context['currency'] = "₹"
#     context['total_in_words'] = num2words.num2words(int(context['invoice_data']['invoice_total_amt_with_gst']), lang='en_IN').title()
#     context['user_profile'] = user_profile
#     return render(request, 'gstbillingapp/invoice_printer.html', context)



def customersjson(request):
    # Retrieve customers from the model and convert PhoneNumber objects to strings
    customers = [
        {key: str(value) if isinstance(value, PhoneNumber) else value for key, value in customer.items()}
        for customer in Customer.objects.all().values()
    ]

    # Return JsonResponse with proper formatting
    return JsonResponse(customers, safe=False, json_dumps_params={'ensure_ascii': False})



def productsjson(request):
    products = list(Product.objects.all().values())
    return JsonResponse(products, safe=False)