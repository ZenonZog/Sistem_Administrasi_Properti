from django.db import models
from decimal import Decimal

# Create your models here.

class Perumahan(models.Model):
    nama_perumahan = models.CharField(max_length=150, unique=True, verbose_name="Nama Perumahan")
    lokasi = models.TextField(blank=True, null=True, verbose_name="Lokasi / Alamat")
    desa_kelurahan = models.CharField(max_length=100, blank=True, null=True, verbose_name="Desa/Kelurahan")
    kecamatan = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kecamatan")
    
    def __str__(self):
        return self.nama_perumahan


class CompanyInfo(models.Model):
    """Singleton model for company information (only 1 row)"""
    nama_perusahaan = models.CharField(max_length=200, default="PT. Nama Perusahaan", verbose_name="Nama Perusahaan")
    alamat_perusahaan = models.TextField(blank=True, null=True, verbose_name="Alamat Perusahaan")
    rekening_1_bank = models.CharField(max_length=50, blank=True, null=True, verbose_name="Bank Rekening 1")
    rekening_1_nomor = models.CharField(max_length=50, blank=True, null=True, verbose_name="No. Rekening 1")
    rekening_1_cabang = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cabang Rekening 1")
    rekening_2_bank = models.CharField(max_length=50, blank=True, null=True, verbose_name="Bank Rekening 2")
    rekening_2_nomor = models.CharField(max_length=50, blank=True, null=True, verbose_name="No. Rekening 2")
    rekening_2_cabang = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cabang Rekening 2")
    catatan_surat = models.TextField(blank=True, null=True, verbose_name="Catatan di Surat Pesanan", help_text="Contoh: Free Smartlock, TV 43\", Sertifikat, AJB, BPHTB")

    class Meta:
        verbose_name = "Informasi Perusahaan"
        verbose_name_plural = "Informasi Perusahaan"

    def __str__(self):
        return self.nama_perusahaan

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton)
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

class Unit(models.Model):
    perumahan = models.ForeignKey(Perumahan, on_delete=models.CASCADE, related_name='units', null=True)
    STATUS_CHOICES = (
        ('Tersedia', 'Tersedia'),
        ('Booking', 'Booking'),
        ('Terjual', 'Terjual'),
    )
    TIPE_CHOICES = (
        ('Standard', 'Standard'),
        ('Hook', 'Hook'),
    )
    blok = models.CharField(max_length=10, verbose_name="Kode Blok", help_text="Contoh: A, B, C")
    nomor_rumah = models.CharField(max_length=10, verbose_name="Nomor Rumah", help_text="Contoh: 1, 2, 3")
    tipe_rumah = models.CharField(max_length=20, choices=TIPE_CHOICES, default='Standard', verbose_name="Tipe Rumah")
    luas_tanah = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Luas Tanah (m²)", null=True, blank=True)
    luas_bangunan = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Luas Bangunan (m²)", null=True, blank=True)
    harga_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Harga Total")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Tersedia')
    foto = models.ImageField(upload_to='unit_fotos/', blank=True, null=True)

    class Meta:
        unique_together = ('perumahan', 'blok', 'nomor_rumah')

    @property
    def kode_blok(self):
        """Property untuk backward-compatibility"""
        return f"{self.blok.upper()}{self.nomor_rumah}"

    def __str__(self):
        return f"{self.blok.upper()}{self.nomor_rumah} - {self.tipe_rumah}"


class Customer(models.Model):
    METODE_CHOICES = (
        ('KPR', 'KPR'),
        ('Cash Bertahap', 'Cash Bertahap'),
        ('Cash Keras', 'Cash Keras'),
    )
    nama_lengkap = models.CharField(max_length=150, verbose_name="Nama Lengkap")
    nik = models.CharField(max_length=16, blank=True, null=True, verbose_name="NIK")
    no_telepon = models.CharField(max_length=20, blank=True, null=True, verbose_name="No Telepon")
    alamat_ktp = models.TextField(blank=True, null=True, verbose_name="Alamat KTP")
    alamat_sekarang = models.TextField(blank=True, null=True, verbose_name="Alamat Sekarang")
    nama_kontak_darurat = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nama Kontak Darurat")
    no_kontak_darurat = models.CharField(max_length=20, blank=True, null=True, verbose_name="No. Kontak Darurat")
    hubungan_kontak_darurat = models.CharField(max_length=50, blank=True, null=True, verbose_name="Hubungan Kontak Darurat", help_text="Contoh: Adik, Kakak, Orang Tua")
    alamat_kontak_darurat = models.TextField(blank=True, null=True, verbose_name="Alamat Kontak Darurat")
    # Informasi pembelian
    metode_pembelian = models.CharField(max_length=20, choices=METODE_CHOICES, blank=True, null=True, verbose_name="Metode Pembelian")
    utj = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="UTJ (Uang Tanda Jadi)")
    dp = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="DP (Down Payment)")
    bunga_per_tahun = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Bunga Per Tahun (%)", help_text="Khusus KPR. Isi 0 jika bukan KPR.")
    # Saldo kredit dari kelebihan bayar
    saldo_kredit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Saldo Kredit")

    def __str__(self):
        return self.nama_lengkap


class Cicilan(models.Model):
    STATUS_BAYAR_CHOICES = (
        ('Lunas', 'Lunas'),
        ('Belum Lunas', 'Belum Lunas'),
    )
    REKENING_CHOICES = (
        ('BRI', 'BRI'),
        ('BCA', 'BCA'),
        ('Mandiri', 'Mandiri'),
        ('BNI', 'BNI'),
        ('Lainnya', 'Lainnya'),
        ('-', 'Belum Tersedia'),
    )
    METODE_BAYAR_CHOICES = (
        ('Cash', 'Cash'),
        ('Transfer', 'Transfer'),
    )
    SP_CHOICES = (
        ('-', '-'),
        ('SP1', 'SP1'),
        ('SP2', 'SP2'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cicilan')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='cicilan')
    jumlah_cicilan = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Jumlah Cicilan")
    jumlah_dibayar = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Jumlah Dibayar Aktual")
    tanggal_jatuh_tempo = models.DateField(verbose_name="Tanggal Jatuh Tempo")
    tanggal_batas_bayar = models.DateField(blank=True, null=True, verbose_name="Batas Tanggal Bayar")
    bulan = models.IntegerField(verbose_name="Bulan", help_text="Bulan jatuh tempo (Contoh: 8, 9, 10)")
    tahun = models.IntegerField(verbose_name="Tahun", help_text="Tahun jatuh tempo (Contoh: 2024)")
    keterangan_cicilan = models.CharField(max_length=50, verbose_name="Keterangan", help_text="Contoh: C1, C7")
    denda = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Denda")
    denda_persen = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Denda (%/bulan)")
    rekening = models.CharField(max_length=20, choices=REKENING_CHOICES, default='-', blank=True)
    metode_bayar = models.CharField(max_length=10, choices=METODE_BAYAR_CHOICES, blank=True, null=True, verbose_name="Metode Bayar")
    status_bayar = models.CharField(max_length=20, choices=STATUS_BAYAR_CHOICES, default='Belum Lunas')
    status_sp = models.CharField(max_length=5, choices=SP_CHOICES, default='-', verbose_name="Status SP")

    @property
    def denda_terhitung(self):
        """Hitung denda otomatis berdasarkan denda_persen jika belum lunas dan lewat batas bayar"""
        from django.utils import timezone
        if self.status_bayar == 'Belum Lunas' and self.tanggal_batas_bayar:
            today = timezone.now().date()
            if today > self.tanggal_batas_bayar and self.denda_persen > 0:
                return self.jumlah_cicilan * (self.denda_persen / 100)
        return Decimal('0')

    def __str__(self):
        return f"{self.customer} - {self.unit} ({self.tanggal_jatuh_tempo} | {self.keterangan_cicilan})"

    class Meta:
        verbose_name_plural = "Cicilan"
