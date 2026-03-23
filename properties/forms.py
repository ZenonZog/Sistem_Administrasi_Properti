from django import forms
from .models import Customer, Unit, Perumahan, Cicilan, CompanyInfo

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['nama_lengkap', 'nik', 'no_telepon', 'alamat_ktp', 'alamat_sekarang', 
                  'nama_kontak_darurat', 'no_kontak_darurat', 'hubungan_kontak_darurat', 'alamat_kontak_darurat']
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Lengkap'}),
            'nik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 3201234567890001 (16 digit)'}),
            'no_telepon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 08123456789 (Opsional)'}),
            'alamat_ktp': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat sesuai KTP'}),
            'alamat_sekarang': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat tempat tinggal saat ini'}),
            'nama_kontak_darurat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Kontak Darurat (Opsional)'}),
            'no_kontak_darurat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'No. HP Kontak Darurat (Opsional)'}),
            'hubungan_kontak_darurat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Adik Kandung, Kakak, dll'}),
            'alamat_kontak_darurat': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat Kontak Darurat (Opsional)'}),
        }

class CustomerRegistrationForm(forms.ModelForm):
    perumahan = forms.ModelChoiceField(
        queryset=Perumahan.objects.all(),
        label="Proyek Perumahan",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_perumahan'})
    )
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.filter(status='Tersedia'),
        label="Daftar ke Blok / Unit",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_unit'})
    )
    metode_pembelian = forms.ChoiceField(
        choices=Customer.METODE_CHOICES,
        label="Metode Pembelian",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_metode_pembelian'})
    )
    utj = forms.DecimalField(
        max_digits=12, decimal_places=2, initial=0,
        label="UTJ - Uang Tanda Jadi (Rp)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 5000000', 'id': 'id_utj', 'min': '0'})
    )
    dp = forms.DecimalField(
        max_digits=12, decimal_places=2, initial=0,
        label="DP - Down Payment (Rp)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 20000000', 'id': 'id_dp', 'min': '0'})
    )
    bunga_per_tahun = forms.DecimalField(
        max_digits=5, decimal_places=2, initial=0, required=False,
        label="Bunga Per Tahun (%) — Khusus KPR",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 7.5', 'id': 'id_bunga', 'step': '0.1', 'min': '0'})
    )
    lama_cicilan = forms.IntegerField(
        label="Lama Cicilan (Bulan)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 120', 'id': 'id_lama_cicilan', 'min': '1'})
    )
    tanggal_jatuh_tempo = forms.DateField(
        label="Tgl Jatuh Tempo Cicilan Perdana",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    tanggal_batas_bayar_offset = forms.IntegerField(
        label="Toleransi Bayar (Hari setelah jatuh tempo)",
        initial=7,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 7', 'min': '0'})
    )
    denda_persen = forms.DecimalField(
        max_digits=5, decimal_places=2, initial=0, required=False,
        label="Denda Keterlambatan (% dari cicilan/bulan)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 2', 'step': '0.1', 'min': '0'})
    )

    class Meta:
        model = Customer
        fields = ['nama_lengkap', 'nik', 'no_telepon', 'alamat_ktp', 'alamat_sekarang',
                  'nama_kontak_darurat', 'no_kontak_darurat', 'hubungan_kontak_darurat', 'alamat_kontak_darurat']
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Lengkap'}),
            'nik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 3201234567890001 (16 digit)'}),
            'no_telepon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 08123456789 (Opsional)'}),
            'alamat_ktp': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat sesuai KTP'}),
            'alamat_sekarang': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat tempat tinggal saat ini'}),
            'nama_kontak_darurat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Kontak Darurat (Opsional)'}),
            'no_kontak_darurat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'No. HP Kontak Darurat (Opsional)'}),
            'hubungan_kontak_darurat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Adik Kandung, Kakak'}),
            'alamat_kontak_darurat': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat Kontak Darurat'}),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['perumahan', 'blok', 'nomor_rumah', 'tipe_rumah', 'luas_tanah', 'luas_bangunan', 'harga_total', 'status']
        widgets = {
            'perumahan': forms.Select(attrs={'class': 'form-select'}),
            'blok': forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': 'Contoh: A, B, C'}),
            'nomor_rumah': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 1, 2, 3'}),
            'tipe_rumah': forms.Select(attrs={'class': 'form-select'}),
            'luas_tanah': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 72 (m²)', 'step': '0.01'}),
            'luas_bangunan': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 36 (m²)', 'step': '0.01'}),
            'harga_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 250000000'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class ConfirmasiBayarForm(forms.ModelForm):
    jumlah_dibayar = forms.DecimalField(
        max_digits=12, decimal_places=2,
        label="Jumlah Dibayar (Rp)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nominal yang benar-benar dibayar', 'min': '0', 'step': '1000'})
    )
    metode_bayar = forms.ChoiceField(
        choices=[('Cash', 'Cash'), ('Transfer', 'Transfer')],
        label="Metode Pembayaran",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_metode_bayar_confirm'})
    )
    rekening = forms.ChoiceField(
        choices=Cicilan.REKENING_CHOICES,
        label="Transfer ke Bank",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_rekening_confirm'})
    )

    class Meta:
        model = Cicilan
        fields = ['jumlah_dibayar', 'metode_bayar', 'rekening']

class CompanyInfoForm(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = '__all__'
        widgets = {
            'nama_perusahaan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: PT. Anugerah Jaya Prakarsa'}),
            'alamat_perusahaan': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat lengkap perusahaan'}),
            'rekening_1_bank': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: BCA'}),
            'rekening_1_nomor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 3401522678'}),
            'rekening_1_cabang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Cabang Nagoya, Batam'}),
            'rekening_2_bank': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: BRI'}),
            'rekening_2_nomor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 065915000498315'}),
            'rekening_2_cabang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Cabang Aviari, Batam'}),
            'catatan_surat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Contoh: Free Smartlock, TV 43", Sertifikat, AJB, BPHTB'}),
        }
