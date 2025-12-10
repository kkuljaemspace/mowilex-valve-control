# Solusi Deploy Django + Modbus Server di Android

## 🎯 Arsitektur Saat Ini
```
┌─────────────────┐
│  Django Web     │ ← User Interface (Web)
│  (Port 8000)    │
└────────┬────────┘
         │ (Database: SQLite)
         │
┌────────┴────────┐
│ communications  │ ← Modbus Server
│ (Port 502/1502) │ ← Sync DB ↔ Modbus
└─────────────────┘
```

## ❌ Masalah di Android

### 1. **Port Privileged** 
- Android tidak izinkan port <1024 tanpa root
- Port 502 (Modbus standard) → **TIDAK BISA**
- Port 9000+ → **BISA**

### 2. **Background Service**
- `communications.py` harus jalan terus di background
- Android membatasi background process

## ✅ Solusi yang Direkomendasikan

### **OPSI 1: Pakai Port Non-Privileged (Paling Mudah)**

#### Ubah Default Port
```python
# communications.py - line 177
parser.add_argument('-p', '--port', type=int, default=9502)  # Ubah dari 1502 ke 9502
```

#### Ubah Modbus Client untuk Connect ke Port Custom
```python
# Di sisi client (PLC/device yang connect)
# Ganti port dari 502 → 9502
client.connect('192.168.x.x', 9502)
```

**Kelebihan:**
- Langsung jalan di Android tanpa root
- Mudah diimplementasi

**Kekurangan:**  
- Device Modbus client harus support custom port
- Beberapa device Modbus strict hanya port 502

---

### **OPSI 2: Gabung Django + Modbus dalam 1 App (Recommended for Android)**

Buat service management dalam Django untuk run communications.py

#### File: `project/modbus_service.py`
```python
import threading
import logging
from pyModbusTCP.server import DataBank, ModbusServer
from .models import ValveSet
from django.utils import timezone

class ModbusService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.server = None
            self.data_bank = None
            self.initialized = True
    
    def start(self, host='0.0.0.0', port=9502):
        """Start Modbus server"""
        if self.server is not None:
            logging.warning("Modbus server already running")
            return
        
        from communications import SendReceiveDataBank
        
        self.data_bank = SendReceiveDataBank()
        self.server = ModbusServer(
            host=host,
            port=port,
            data_bank=self.data_bank,
            no_block=True
        )
        
        self.server.start()
        
        # Start sync thread
        sync_thread = threading.Thread(
            target=self.data_bank.sync_valves, 
            daemon=True
        )
        sync_thread.start()
        
        logging.info(f"Modbus server started on {host}:{port}")
    
    def stop(self):
        """Stop Modbus server"""
        if self.server:
            self.server.stop()
            self.server = None
            logging.info("Modbus server stopped")
    
    def is_running(self):
        """Check if server is running"""
        return self.server is not None

# Global instance
modbus_service = ModbusService()
```

#### Tambah URL endpoint untuk control service
`project/urls.py`:
```python
urlpatterns = [
    # ... existing urls
    path('modbus/start/', views.start_modbus_service, name='start_modbus'),
    path('modbus/stop/', views.stop_modbus_service, name='stop_modbus'),
    path('modbus/status/', views.modbus_status, name='modbus_status'),
]
```

#### Tambah views untuk control
`project/views.py`:
```python
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .modbus_service import modbus_service

@staff_member_required
def start_modbus_service(request):
    try:
        host = request.GET.get('host', '0.0.0.0')
        port = int(request.GET.get('port', 9502))
        modbus_service.start(host, port)
        return JsonResponse({'status': 'success', 'message': f'Modbus started on {host}:{port}'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@staff_member_required
def stop_modbus_service(request):
    try:
        modbus_service.stop()
        return JsonResponse({'status': 'success', 'message': 'Modbus stopped'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def modbus_status(request):
    return JsonResponse({
        'running': modbus_service.is_running(),
        'timestamp': timezone.now().isoformat()
    })
```

**Kelebihan:**
- Semua dalam 1 aplikasi Django
- Bisa control start/stop dari web interface
- Lebih mudah deploy

**Kekurangan:**
- Masih tetap butuh port 9000+

---

### **OPSI 3: Port Forwarding dengan Root (Advanced)**

Jika HP Android di-root, bisa forward port 502 → 9502:

```bash
# Di Android (Termux dengan root)
su
iptables -t nat -A PREROUTING -p tcp --dport 502 -j REDIRECT --to-port 9502
```

**Kelebihan:**
- Device Modbus tetap connect ke port 502
- Transparent forwarding

**Kekurangan:**
- Butuh root access
- Risky untuk production

---

### **OPSI 4: Deploy di Server/PC, Android hanya Web Interface**

Pisahkan deployment:
- **Server/PC**: Jalankan Django + communications.py
- **Android**: Akses web interface Django saja

```
Internet/LAN
    │
    ├─► Server/PC (Django + Modbus) ← Modbus Devices
    │   - Port 8000: Django Web
    │   - Port 502: Modbus Server
    │
    └─► Android (Browser)
        - Akses http://server-ip:8000
```

**Kelebihan:**
- Tidak ada masalah port
- Reliable & production-ready
- Android cuma butuh browser

**Kekurangan:**
- Butuh server terpisah

---

## 📱 Deployment di Android (Termux)

### Install Requirements
```bash
# Install Termux dari F-Droid atau Play Store
pkg update && pkg upgrade
pkg install python git
pip install django pyModbusTCP cx-Oracle python-dateutil
```

### Clone & Setup Project
```bash
cd ~
git clone <repo-url> mowilex999
cd mowilex999
pip install -r requirements.txt
python manage.py migrate
```

### Run Django (Port 8000)
```bash
python manage.py runserver 0.0.0.0:8000
```

### Run Modbus Server (Port 9502) - Terminal Terpisah
```bash
# Buka session baru dengan tmux
pkg install tmux
tmux new -s modbus

# Jalankan modbus server
python communications.py -H 0.0.0.0 -p 9502

# Detach: Ctrl+B, lalu tekan D
```

### Auto-start on Boot (Optional)
Buat script `start_services.sh`:
```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/mowilex999

# Start Django
python manage.py runserver 0.0.0.0:8000 &

# Start Modbus
python communications.py -H 0.0.0.0 -p 9502 &

echo "Services started"
```

---

## 🎯 Rekomendasi Saya

**Untuk Android:**
1. **Gunakan OPSI 2** (Gabung dalam Django) + Port 9502
2. Akses via web browser di `http://localhost:8000`
3. Control Modbus server dari web interface

**Untuk Production:**
- **Gunakan OPSI 4** (Server terpisah)
- Android hanya sebagai client/monitoring

---

## ⚙️ Implementasi yang Harus Dilakukan

Mau saya buatkan kode untuk **OPSI 2** (Gabung Django + Modbus)?
Atau mau solusi lain?
