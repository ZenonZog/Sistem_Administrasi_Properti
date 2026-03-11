from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('export-excel/', views.export_cicilan_excel, name='export_excel'),
    path('cicilan/<int:pk>/mark-lunas/', views.mark_lunas, name='mark_lunas'),
    path('status-konsumen/', views.status_konsumen, name='status_konsumen'),

    # Customer URLs
    path('customers/add/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # Unit URLs
    path('units/', views.unit_list, name='unit_list'),
    path('units/add/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/edit/', views.unit_update, name='unit_update'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),
]
