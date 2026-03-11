from django import forms
from .models import Customer, Unit

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['nama_lengkap', 'no_telepon', 'alamat']
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Lengkap'}),
            'no_telepon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 08123456789 (Opsional)'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alamat Lengkap (Opsional)'}),
        }

class CustomerRegistrationForm(forms.ModelForm):
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all(), 
        label="Daftar ke Blok / Unit", 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    lama_cicilan = forms.IntegerField(
        label="Lama Cicilan (Bulan)", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 120'})
    )
    harga_rumah = forms.DecimalField(
        max_digits=12, decimal_places=2, 
        label="Harga Rumah Kesepakatan (Rp)", 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 250000000'})
    )
    tanggal_jatuh_tempo = forms.DateField(
        label="Tgl Jatuh Tempo Cicilan Perdana", 
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Customer
        fields = ['nama_lengkap', 'no_telepon', 'alamat']
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Lengkap'}),
            'no_telepon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 08123456789 (Opsional)'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alamat Lengkap (Opsional)'}),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['kode_blok', 'tipe_rumah', 'harga_total', 'status']
        widgets = {
            'kode_blok': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: D1, A5'}),
            'tipe_rumah': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Tipe 36, Kavling'}),
            'harga_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 250000000'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
