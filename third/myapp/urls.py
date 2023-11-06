from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
	path('',views.sample_view, name='sample_view'),
	path('school/', views.SchoolView.as_view(), name = 'school_view'),
	path('list/',views.SchoolListView.as_view(), name = 'list'),
	path('school_detail/<int:pk>',views.SchoolDetailView.as_view(), name = 'detail')
	]