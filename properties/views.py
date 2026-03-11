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
    
    context = {
        'total_unit': total_unit,
        'unit_tersedia': unit_tersedia,
        'unit_terjual': unit_terjual_atau_booking,
        'cicilan_jatuh_tempo': cicilan_jatuh_tempo,
        'today': today,
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
    
    # Auto-generate cicilan bulan berikutnya
    # Mencari angka pada keterangan, misal "C1" atau "Cicilan Ke-10"
    match = re.search(r'(\d+)', old_ket)
    if match:
        num = int(match.group(1))
        # Mengubah jadi angka selanjutnya, misal C1 -> C2
        new_ket = old_ket[:match.start()] + str(num + 1) + old_ket[match.end():]
    else:
        new_ket = old_ket + " Lanjutan"
        
    next_jatuh_tempo = add_months(cicilan.tanggal_jatuh_tempo, 1)
    
    # Simpan instance baris cicilan baru untuk bulan depan (Belum Lunas)
    Cicilan.objects.create(
        customer=cicilan.customer,
        unit=cicilan.unit,
        jumlah_cicilan=cicilan.jumlah_cicilan,
        tanggal_jatuh_tempo=next_jatuh_tempo,
        bulan=next_jatuh_tempo.month,
        tahun=next_jatuh_tempo.year,
        keterangan_cicilan=new_ket,
        rekening=cicilan.rekening,
        status_bayar='Belum Lunas'
    )
    
    messages.success(request, f"Pembayaran {old_ket} a.n {cicilan.customer.nama_lengkap} divalidasi. Tagihan {new_ket} otomatis dibuat untuk bulan depan.")
    return redirect('dashboard')

# --- REKAP STATUS SEMUA KONSUMEN & CRUD CUSTOMER ---

def status_konsumen(request):
    # Mengambil tagihan berjalan setiap konsumen
    cicilans = Cicilan.objects.filter(status_bayar='Belum Lunas').select_related('customer', 'unit').order_by('customer__nama_lengkap', 'tanggal_jatuh_tempo')
    
    # Menghitung total terbayar dan sisa hutang untuk masing-masing cicilan berjalan
    for cicilan in cicilans:
        # Cari total yang sudah dibayar Lunas untuk unit dan customer ini
        terbayar_agg = Cicilan.objects.filter(
            customer=cicilan.customer, 
            unit=cicilan.unit, 
            status_bayar='Lunas'
        ).aggregate(total=Sum('jumlah_cicilan'))
        
        cicilan.total_terbayar = terbayar_agg['total'] or 0
        cicilan.harga_rumah = cicilan.unit.harga_total
        cicilan.sisa_hutang = cicilan.harga_rumah - cicilan.total_terbayar

    return render(request, 'properties/status_konsumen.html', {'cicilans': cicilans, 'title': 'Data Status Cicilan Konsumen'})

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
                
            # Otomatis ciptakan tagihan Cicilan pertama (C1)
            Cicilan.objects.create(
                customer=customer,
                unit=unit,
                jumlah_cicilan=jumlah_cicilan,
                tanggal_jatuh_tempo=tanggal_jatuh_tempo,
                bulan=tanggal_jatuh_tempo.month,
                tahun=tanggal_jatuh_tempo.year,
                keterangan_cicilan="C1",
                rekening="-",
                status_bayar="Belum Lunas"
            )

            messages.success(request, f"Pelanggan Baru {customer.nama_lengkap} berhasil mendaftar (Blok {unit.kode_blok}). Tagihan Cicilan Pertama (C1) telah dibuat.")
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
