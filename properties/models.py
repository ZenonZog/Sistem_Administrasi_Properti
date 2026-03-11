from django.db import models

# Create your models here.

class Unit(models.Model):
    STATUS_CHOICES = (
        ('Tersedia', 'Tersedia'),
        ('Booking', 'Booking'),
        ('Terjual', 'Terjual'),
    )
    kode_blok = models.CharField(max_length=20, unique=True, verbose_name="Kode Blok")
    tipe_rumah = models.CharField(max_length=50, verbose_name="Tipe Rumah")
    harga_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Harga Total")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Tersedia')
    foto = models.ImageField(upload_to='unit_fotos/', blank=True, null=True)

    def __str__(self):
        return f"{self.kode_blok} - {self.tipe_rumah}"

class Customer(models.Model):
    nama_lengkap = models.CharField(max_length=150, verbose_name="Nama Lengkap")
    no_telepon = models.CharField(max_length=20, blank=True, null=True, verbose_name="No Telepon")
    alamat = models.TextField(blank=True, null=True)

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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cicilan')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='cicilan')
    jumlah_cicilan = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Jumlah Cicilan")
    tanggal_jatuh_tempo = models.DateField(verbose_name="Tanggal Jatuh Tempo")
    bulan = models.IntegerField(verbose_name="Bulan", help_text="Bulan jatuh tempo (Contoh: 8, 9, 10)")
    tahun = models.IntegerField(verbose_name="Tahun", help_text="Tahun jatuh tempo (Contoh: 2024)")
    keterangan_cicilan = models.CharField(max_length=50, verbose_name="Keterangan", help_text="Contoh: C1, C7")
    denda = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Denda")
    rekening = models.CharField(max_length=20, choices=REKENING_CHOICES, default='-', blank=True)
    status_bayar = models.CharField(max_length=20, choices=STATUS_BAYAR_CHOICES, default='Belum Lunas')

    def __str__(self):
        return f"{self.customer} - {self.unit} ({self.tanggal_jatuh_tempo} | {self.keterangan_cicilan})"

    class Meta:
        verbose_name_plural = "Cicilan"
