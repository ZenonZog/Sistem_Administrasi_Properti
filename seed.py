import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from properties.models import Unit, Customer, Cicilan

def seed():
    # Clear existing
    Cicilan.objects.all().delete()
    Unit.objects.all().delete()
    Customer.objects.all().delete()

    # Create Units
    u1, _ = Unit.objects.get_or_create(kode_blok='D1', tipe_rumah='Tipe 36', harga_total=250000000)
    u10, _ = Unit.objects.get_or_create(kode_blok='D10', tipe_rumah='Tipe 45', harga_total=350000000)
    u11, _ = Unit.objects.get_or_create(kode_blok='D11', tipe_rumah='Tipe 45', harga_total=350000000)

    # Create Customers
    c_adi, _ = Customer.objects.get_or_create(nama_lengkap='Adi Putra Utama')
    c_anita, _ = Customer.objects.get_or_create(nama_lengkap='Anita Yurida')
    c_asep, _ = Customer.objects.get_or_create(nama_lengkap='Asep Suherman')

    print("Units and Customers created.")

    today = timezone.now().date()

    # Create Cicilan (Simulating based on Excel but mapping dates around today for testing)
    cicilans = [
        # Past due (Terlewat)
        (c_adi, u10, 19250000, today - timedelta(days=2), 8, 2024, 'C1', 'BRI'),
        # Near due (Hampir tiba)
        (c_anita, u1, 8017000, today + timedelta(days=3), 8, 2024, 'C7', 'BRI'),
        # Future (Aman, > 7 hari)
        (c_asep, u11, 7507000, today + timedelta(days=15), 9, 2024, 'C9', '-'),
        # Another near due
        (c_anita, u1, 8017000, today + timedelta(days=6), 9, 2024, 'C8', '-'),
    ]

    for c, u, jml, tanggal, bulan, tahun, ket, rek in cicilans:
        Cicilan.objects.create(
            customer=c,
            unit=u,
            jumlah_cicilan=jml,
            tanggal_jatuh_tempo=tanggal,
            bulan=bulan,
            tahun=tahun,
            keterangan_cicilan=ket,
            rekening=rek,
            status_bayar='Belum Lunas'
        )
    print("Cicilan seeded successfully.")

if __name__ == '__main__':
    seed()
