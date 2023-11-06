from django.shortcuts import render
from django.views.generic import View, TemplateView, ListView, DetailView
from django.http import HttpResponse
from . import models

# Create your views here.

def sample_view(request):
	return render(request,'myapp/example.html')

class SchoolView(TemplateView):
	template_name = 'index.html'

	def get_context_data(self,**kwargs):
		context = super().get_context_data(**kwargs)
		context['injectme'] = 'INJECTED!!'
		return context

class SchoolListView(ListView):
	model = models.School 	# returns school_list by default


class SchoolDetailView(DetailView):
	model = models.School 	# returns school by default 
	template_name = 'myapp/school_detail.html' # Looks for school_detail.html by default

class 


