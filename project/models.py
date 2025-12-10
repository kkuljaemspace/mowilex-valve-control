from django.db import models

# Create your models here.
from django.db import models

from otentifikasi.models import Profile


class VendorURL(models.Model):
    # Primary key
    vendor_id = models.AutoField(primary_key=True)

    # Sesuaikan max_length sesuai kebutuhan
    uri = models.CharField(max_length=50)

    # Karena nvarchar(MAX), kita gunakan TextField
    security_token = models.TextField()

    # Tipe data bit -> BooleanField di Django
    ssl = models.BooleanField(default=False)

    # Sesuaikan max_length sesuai kebutuhan
    format_output = models.CharField(max_length=50)

    # Tipe data datetime -> DateTimeField di Django
    created_date = models.DateTimeField()

    def __str__(self):
        return f"VendorURL {self.vendor_id} - {self.uri}"


class ItemMap(models.Model):
    # Primary key
    item_map_id = models.AutoField(primary_key=True)

    # Foreign key ke VendorURL
    vendor = models.ForeignKey(VendorURL, on_delete=models.CASCADE)

    # Sesuaikan max_length sesuai kebutuhan
    internal_item_id = models.CharField(max_length=50)
    external_item_id = models.CharField(max_length=50)
    created_by = models.CharField(max_length=50)

    # Tipe data datetime -> DateTimeField di Django
    created_date = models.DateTimeField()

    def __str__(self):
        return f"ItemMap {self.item_map_id} (Vendor: {self.vendor_id})"


class ScanTable(models.Model):
    # Primary key
    tag_id = models.AutoField(primary_key=True)

    # Tipe data datetime -> DateTimeField di Django
    trans_date = models.DateTimeField()

    # Foreign key ke VendorURL
    vendor = models.ForeignKey(VendorURL, on_delete=models.CASCADE)

    # Sesuaikan max_length sesuai kebutuhan
    vehicle_no = models.CharField(max_length=50, null=True, blank=True)
    item = models.CharField(max_length=50, null=True, blank=True)
    po = models.CharField(max_length=50, null=True, blank=True)
    um = models.CharField(max_length=50, null=True, blank=True)

    # numeric(28, 2) -> DecimalField dengan max_digits=28, decimal_places=2
    weighbridge = models.DecimalField(max_digits=28, decimal_places=2, null=True, blank=True)
    silo_qty = models.DecimalField(max_digits=28, decimal_places=2, null=True, blank=True)

    error_by = models.CharField(max_length=50, null=True, blank=True)
    plc_command = models.CharField(max_length=50, null=True, blank=True)

    # Tipe data datetime -> DateTimeField di Django
    created_date = models.DateTimeField()

    def __str__(self):
        return f"ScanTable {self.tag_id} (Vendor: {self.vendor})"

from django.db import models

class EpicorPO(models.Model):
    """
    Model untuk menyimpan data PO Check dari API Epicor.
    Jika data dengan ponum yang sama sudah ada, maka bisa dilakukan update.
    """
    ponum = models.PositiveIntegerField(primary_key=True)
    detail_data = models.JSONField(help_text="Data detail dari PO Check (JSON)")
    summary_data = models.JSONField(help_text="Data summary dari PO Check (JSON)")
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    # Tambahkan field status untuk memantau status PO:
    status = models.CharField(
        max_length=50,
        default="IDEM",
        help_text="Status PO: Open Valve, Selesai, Pause"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO STATUS {self.status}"



class MappingValve(models.Model):
    """
    Model untuk melakukan mapping Pipa per 7 digit pertama
    """
    valve_number = models.PositiveSmallIntegerField(help_text="Nomor valve (1 s/d ???)")
    part_number = models.CharField(max_length=255, null=True, blank=True)
    status_value_number = models.IntegerField(null=True, blank=True, help_text="Nilai status valve setelah eksekusi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Map Untuk Valve: {self.valve_number} dengan Material Number"


class ValveOperation(models.Model):
    """
    Model untuk mencatat setiap permintaan open_valve ke PLC.
    Mencatat nomor valve, nilai perintah yang dikirim, nilai status yang dibaca,
    status valve (misal: 'Terbuka', 'Tertutup'), serta waktu eksekusi.
    """
    valve_number = models.ForeignKey(MappingValve, on_delete=models.SET_NULL, null=True)
    command_value = models.IntegerField(default=0, help_text="Nilai perintah (0 untuk membuka)")
    status_value = models.IntegerField(null=True, blank=True, help_text="Nilai status valve setelah eksekusi")
    status = models.CharField(max_length=50, help_text="Deskripsi status (misal: Terbuka atau Tertutup)")
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Valve {self.valve_number} - {self.status} pada {self.created_at:%Y-%m-%d %H:%M:%S}"


class ValveSet(models.Model):
    valve_number = models.PositiveSmallIntegerField(help_text="Nomor valve (1 s/d ???)")
    status = models.PositiveSmallIntegerField(help_text="Nomor 0 or 1")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ModbusConfig(models.Model):
    """
    Konfigurasi Modbus Server
    Singleton model - hanya ada 1 row
    
    PENTING: 
    - Android = MODBUS SLAVE/SERVER (Listen & tunggu koneksi dari PLC)
    - PLC = MODBUS MASTER/CLIENT (Connect ke Android)
    """
    # Network Configuration - ANDROID (Modbus Slave/Server)
    android_ip = models.GenericIPAddressField(
        default='0.0.0.0',
        help_text='IP Address Android untuk LISTEN koneksi (0.0.0.0 = semua interface)'
    )
    android_port = models.PositiveIntegerField(
        default=9502,
        help_text='Port yang Android LISTEN untuk menerima koneksi dari PLC (≥1024 untuk Android)'
    )
    
    # PLC Configuration - Hanya untuk dokumentasi/referensi
    # PLC harus di-configure untuk CONNECT ke android_ip:android_port
    plc_ip = models.GenericIPAddressField(
        default='192.168.2.99',
        help_text='IP Address PLC (Modbus Master) - untuk referensi saja'
    )
    plc_port = models.PositiveIntegerField(
        default=502,
        help_text='Port standar Modbus PLC - untuk referensi saja, tidak digunakan oleh Android'
    )
    
    # Server Status
    auto_start = models.BooleanField(
        default=False,
        help_text='Auto-start Modbus server saat aplikasi dijalankan'
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        Profile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        verbose_name = 'Modbus Configuration'
        verbose_name_plural = 'Modbus Configuration'
    
    def __str__(self):
        return f'Modbus Config: Android {self.android_ip}:{self.android_port} ← PLC {self.plc_ip}:{self.plc_port}'
    
    def save(self, *args, **kwargs):
        # Pastikan hanya ada 1 konfigurasi
        if not self.pk and ModbusConfig.objects.exists():
            raise ValueError('Hanya boleh ada 1 konfigurasi Modbus')
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Get atau create konfigurasi default"""
        config, created = cls.objects.get_or_create(pk=1)
        return config