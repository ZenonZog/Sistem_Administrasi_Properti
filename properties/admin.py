from django.contrib import admin
from .models import Unit, Customer, Cicilan

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('kode_blok', 'tipe_rumah', 'harga_total', 'status')
    list_filter = ('status', 'tipe_rumah')
    search_fields = ('kode_blok', 'tipe_rumah')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'no_telepon')
    search_fields = ('nama_lengkap',)

@admin.register(Cicilan)
class CicilanAdmin(admin.ModelAdmin):
    list_display = ('customer', 'unit', 'jumlah_cicilan', 'tanggal_jatuh_tempo', 'keterangan_cicilan', 'status_bayar')
    list_filter = ('status_bayar', 'rekening', 'bulan', 'tahun')
    search_fields = ('customer__nama_lengkap', 'unit__kode_blok', 'keterangan_cicilan')
    date_hierarchy = 'tanggal_jatuh_tempo'
