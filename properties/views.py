from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Unit, Customer, Cicilan
from .forms import CustomerForm, UnitForm, CustomerRegistrationForm
from django.db.models import Sum
from django.http import HttpResponse
from django.contrib import messages
import openpyxl
import re
import calendar

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return sourcedate.replace(year=year, month=month, day=day)

def dashboard(request):
    # Statistik Keseluruhan
    total_unit = Unit.objects.count()
    unit_tersedia = Unit.objects.filter(status='Tersedia').count()
    unit_terjual_atau_booking = total_unit - unit_tersedia
    
    # Pengingat Jatuh Tempo (H+7 atau lewat)
    today = timezone.now().date()
    batas_waktu = today + timedelta(days=7)
    
    # Menampilkan cicilan yang belum lunas dan tanggal jatuh temponya kurang dari atau sama dengan 7 hari dari sekarang
    cicilan_jatuh_tempo = Cicilan.objects.filter(
        status_bayar='Belum Lunas',
        tanggal_jatuh_tempo__lte=batas_waktu
    ).order_by('tanggal_jatuh_tempo')
    
    import json
    # Data Pemasukan per Bulan untuk Chart.js (Tahun Ini)
    months_revenue = [0] * 12
    lunas_this_year = Cicilan.objects.filter(
        status_bayar='Lunas',
        tahun=today.year
    )
    for c in lunas_this_year:
        # Bulan di python bernilai 1-12
        if 1 <= c.bulan <= 12:
            months_revenue[c.bulan - 1] += int(c.jumlah_cicilan)
            
    months_revenue_json = json.dumps(months_revenue)
    
    context = {
        'total_unit': total_unit,
        'unit_tersedia': unit_tersedia,
        'unit_terjual': unit_terjual_atau_booking,
        'cicilan_jatuh_tempo': cicilan_jatuh_tempo,
        'today': today,
        'revenue_data': months_revenue_json,
        'current_year': today.year,
    }
    return render(request, 'properties/dashboard.html', context)

def export_cicilan_excel(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Laporan_Cicilan_Jatuh_Tempo.xlsx"'

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Cicilan Jatuh Tempo'

    # Define headers
    columns = ['Nomor', 'Blok / Unit', 'Nama Customer', 'No. HP', 'Jumlah Cicilan (Rp)', 'Jatuh Tempo', 'Periode', 'Keterangan', 'Status']
    row_num = 1

    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title

    today = timezone.now().date()
    batas_waktu = today + timedelta(days=7)
    
    cicilan_jatuh_tempo = Cicilan.objects.filter(
        status_bayar='Belum Lunas',
        tanggal_jatuh_tempo__lte=batas_waktu
    ).order_by('tanggal_jatuh_tempo')

    for idx, item in enumerate(cicilan_jatuh_tempo, 1):
        row_num += 1
        status = "Terlewat" if item.tanggal_jatuh_tempo < today else "Hampir Tiba"
        no_hp = item.customer.no_telepon if item.customer.no_telepon else "-"
        
        row = [
            idx,
            item.unit.kode_blok,
            item.customer.nama_lengkap,
            no_hp,
            float(item.jumlah_cicilan),
            item.tanggal_jatuh_tempo.strftime('%d-%m-%Y'),
            f"{item.bulan}/{item.tahun}",
            item.keterangan_cicilan,
            status
        ]
        
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    workbook.save(response)
    return response

# --- AKSI PEMBAYARAN CICILAN ---

def mark_lunas(request, pk):
    cicilan = get_object_or_404(Cicilan, pk=pk)
    
    old_ket = cicilan.keterangan_cicilan
    
    # Tandai saat ini sebagai lunas
    cicilan.status_bayar = 'Lunas'
    if not cicilan.keterangan_cicilan.endswith("(Lunas)"):
        cicilan.keterangan_cicilan = f"{cicilan.keterangan_cicilan} (Lunas)"
    cicilan.save()
    
    messages.success(request, f"Pembayaran {old_ket} a.n {cicilan.customer.nama_lengkap} berhasil divalidasi lunas.")
    return redirect('dashboard')

# --- REKAP STATUS SEMUA KONSUMEN & CRUD CUSTOMER ---

def status_konsumen(request):
    customers = Customer.objects.prefetch_related('cicilan__unit').all().order_by('nama_lengkap')
    
    cicilans_to_display = []
    
    for customer in customers:
        # Get the first unpaid installment for this customer chronologically
        next_unpaid = customer.cicilan.filter(status_bayar='Belum Lunas').order_by('tanggal_jatuh_tempo').first()
        
        # Calculate totals across all their installments for the associated unit
        if next_unpaid:
            terbayar_agg = customer.cicilan.filter(
                unit=next_unpaid.unit,
                status_bayar='Lunas'
            ).aggregate(total=Sum('jumlah_cicilan'))
            
            next_unpaid.total_terbayar = terbayar_agg['total'] or 0
            next_unpaid.harga_rumah = next_unpaid.unit.harga_total
            next_unpaid.sisa_hutang = next_unpaid.harga_rumah - next_unpaid.total_terbayar
            
            cicilans_to_display.append(next_unpaid)
        else:
            # If no unpaid bills, perhaps fully paid off or no bills created
            first_paid = customer.cicilan.filter(status_bayar='Lunas').order_by('tanggal_jatuh_tempo').last()
            if first_paid:
                first_paid.keterangan_cicilan = "LUNAS SEMUA"
                first_paid.total_terbayar = first_paid.unit.harga_total
                first_paid.harga_rumah = first_paid.unit.harga_total
                first_paid.sisa_hutang = 0
                first_paid.status_bayar = 'Lunas'
                cicilans_to_display.append(first_paid)

    return render(request, 'properties/status_konsumen.html', {'cicilans': cicilans_to_display, 'title': 'Data Status Cicilan Konsumen'})

def customer_create(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save()
            unit = form.cleaned_data['unit']
            harga_rumah = form.cleaned_data['harga_rumah']
            lama_cicilan = form.cleaned_data['lama_cicilan']
            tanggal_jatuh_tempo = form.cleaned_data['tanggal_jatuh_tempo']
            
            # Hitung jumlah tagihan bulanan
            jumlah_cicilan = harga_rumah / lama_cicilan if lama_cicilan > 0 else harga_rumah
            
            # Ubah status unit jika belum terjual
            if unit.status == 'Tersedia':
                unit.status = 'Booking'
                unit.save()
                
            # Otomatis ciptakan SEKUMPULAN tagihan Cicilan (bulk create)
            cicilan_bulk = []
            for i in range(lama_cicilan):
                tgl_jatuh_tempo_berjalan = add_months(tanggal_jatuh_tempo, i)
                cicilan_bulk.append(Cicilan(
                    customer=customer,
                    unit=unit,
                    jumlah_cicilan=jumlah_cicilan,
                    tanggal_jatuh_tempo=tgl_jatuh_tempo_berjalan,
                    bulan=tgl_jatuh_tempo_berjalan.month,
                    tahun=tgl_jatuh_tempo_berjalan.year,
                    keterangan_cicilan=f"C{i+1}",
                    rekening="-",
                    status_bayar="Belum Lunas"
                ))
            
            if cicilan_bulk:
                Cicilan.objects.bulk_create(cicilan_bulk)

            messages.success(request, f"Pelanggan Baru {customer.nama_lengkap} divalidasi. Simulasi Tagihan dari C1 -> C{lama_cicilan} sukses dibuat otomatis ke database.")
            return redirect('status_konsumen')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'properties/customer_form.html', {'form': form, 'title': 'Register Pelanggan Baru & Cicilan'})

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    # Mengambil properti (Unit) yang terkait dengan customer ini melalui tabel Cicilan
    cicilans = customer.cicilan.select_related('unit').all()
    # Gunakan set agar unit tidak duplikat apabila dia mencicil bulan yang banyak
    units_owned = list(set([c.unit for c in cicilans]))
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Data Customer {customer.nama_lengkap} berhasil diperbarui.")
            return redirect('status_konsumen')
    else:
        # Jika alamatnya kosong, kita bantu isikan otomatis dari kode blok yang dia beli
        initial_data = {}
        if not customer.alamat and units_owned:
            bloks = ", ".join([u.kode_blok for u in units_owned])
            initial_data['alamat'] = f"Blok {bloks}"
            
        form = CustomerForm(instance=customer, initial=initial_data)
        
    return render(request, 'properties/customer_form.html', {'form': form, 'title': 'Edit Customer', 'units_owned': units_owned})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        nama = customer.nama_lengkap
        customer.delete()
        messages.success(request, f"Data Customer {nama} berhasil dihapus beserta seluruh cicilannya.")
        return redirect('status_konsumen')
    return render(request, 'properties/customer_confirm_delete.html', {'customer': customer})

# --- CRUD PROPERTI / UNIT ---

def unit_list(request):
    units = Unit.objects.all().order_by('kode_blok')
    return render(request, 'properties/unit_list.html', {'units': units})

def unit_create(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Data Properti/Unit berhasil ditambahkan.")
            return redirect('unit_list')
    else:
        form = UnitForm()
    return render(request, 'properties/unit_form.html', {'form': form, 'title': 'Tambah Properti/Unit'})

def unit_update(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Data Properti/Unit {unit.kode_blok} berhasil diperbarui.")
            return redirect('unit_list')
    else:
        form = UnitForm(instance=unit)
    return render(request, 'properties/unit_form.html', {'form': form, 'title': 'Edit Properti/Unit'})

def unit_delete(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        kode = unit.kode_blok
        unit.delete()
        messages.success(request, f"Data Properti/Unit {kode} berhasil dihapus.")
        return redirect('unit_list')
    return render(request, 'properties/unit_confirm_delete.html', {'unit': unit})
