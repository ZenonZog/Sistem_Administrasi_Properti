from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('export-excel/', views.export_cicilan_excel, name='export_excel'),
    path('cicilan/<int:pk>/konfirmasi-bayar/', views.konfirmasi_bayar, name='konfirmasi_bayar'),
    path('riwayat-cicilan/', views.riwayat_cicilan, name='riwayat_cicilan'),
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
    
    # Export URLs
    path('export-konsumen/', views.export_konsumen_excel, name='export_konsumen_excel'),
    path('export-properti/', views.export_properti_excel, name='export_properti_excel'),
    
    # Settings
    path('settings/company/', views.company_settings, name='company_settings'),
    
    # Surat Pesanan
    path('customers/<int:pk>/surat-pesanan/', views.generate_surat_pesanan, name='generate_surat_pesanan'),
]
