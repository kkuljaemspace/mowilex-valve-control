# 📱 Build Mowilex Valve Control untuk Android

## Persiapan

### 1. Install Buildozer di Linux/Mac

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    libffi-dev \
    libssl-dev \
    python3-dev \
    openjdk-11-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    cmake

# Install Buildozer
pip3 install --user buildozer cython
```

### 2. Persiapan Project

File-file penting sudah disiapkan:
- ✅ `buildozer.spec` - Konfigurasi build
- ✅ `main.py` - Entry point aplikasi
- ✅ `modbus_service.py` - Background service untuk Modbus
- ✅ `requirements.txt` - Dependencies Python

## Build APK

### Debug Build (untuk testing)

```bash
# Build APK debug
buildozer android debug

# APK akan ada di: bin/mowilexvalve-1.0.0-arm64-v8a-debug.apk
```

### Release Build (untuk production)

```bash
# Build APK release
buildozer android release

# Sign APK (perlu keystore)
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
    -keystore my-release-key.keystore \
    bin/mowilexvalve-1.0.0-arm64-v8a-release-unsigned.apk \
    alias_name

# Optimize APK
zipalign -v 4 \
    bin/mowilexvalve-1.0.0-arm64-v8a-release-unsigned.apk \
    bin/mowilexvalve-1.0.0-release.apk
```

## Install ke Android

### Via USB Debugging

```bash
# Enable USB debugging di Android Settings > Developer Options

# Install APK
buildozer android deploy run

# Atau manual dengan adb
adb install -r bin/mowilexvalve-1.0.0-arm64-v8a-debug.apk
```

### Via File Transfer

1. Copy APK ke HP Android
2. Buka file dengan File Manager
3. Install (mungkin perlu enable "Install from Unknown Sources")

## Konfigurasi di Android

### 1. Port Configuration

**PENTING:** Android memblokir port < 1024 untuk non-root apps!

Saat pertama kali jalan:
1. Buka browser di HP: `http://localhost:8000`
2. Login dengan user Django
3. Buka menu "Modbus Settings"
4. Set:
   - **Android IP:** `0.0.0.0` (listen semua interface)
   - **Android Port:** `9502` (atau port > 1024)
   - **PLC IP:** IP address PLC di network
   - **PLC Port:** Port Modbus di PLC

### 2. Network Configuration

#### Koneksi WiFi (Recommended)
- HP dan PLC harus di network WiFi yang sama
- Cek IP HP di Settings > WiFi > [Network Name] > Advanced
- PLC connect ke IP HP tersebut dengan port 9502

#### Hotspot HP
- Enable Hotspot di HP
- Connect PLC ke Hotspot HP
- IP HP biasanya: `192.168.43.1`
- PLC connect ke `192.168.43.1:9502`

## Troubleshooting

### Build Errors

```bash
# Clean build
buildozer android clean

# Rebuild
buildozer android debug

# Jika error di p4a, force update
buildozer android debug -v  # verbose mode
```

### Permission Errors

Edit `buildozer.spec` bagian permissions:
```ini
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,WAKE_LOCK
```

### Port Already in Use

```bash
# Check port usage
adb shell netstat -tulpn | grep :9502

# Kill process
adb shell su -c "kill <PID>"
```

### Database Errors

```bash
# Connect via adb
adb shell

# Navigate to app data
cd /data/data/com.mowilex.mowilexvalve/files/app

# Run Django commands
python manage.py migrate
python manage.py createsuperuser
```

## Testing di Android

### 1. Start Aplikasi

```bash
# Via adb
adb shell am start -n com.mowilex.mowilexvalve/org.kivy.android.PythonActivity

# Atau buka dari launcher
```

### 2. Check Logs

```bash
# Real-time logs
adb logcat | grep python

# Modbus specific
adb logcat | grep -i modbus

# Django logs
adb logcat | grep -i django
```

### 3. Test Modbus Connection

Dari PC di network yang sama:

```python
from pyModbusTCP.client import ModbusClient

# Ganti dengan IP HP Android
client = ModbusClient(host='192.168.1.XXX', port=9502, auto_open=True)

if client.is_open:
    print("✅ Connected!")
    
    # Test write
    client.write_single_register(3, 1)
    
    # Test read
    status = client.read_holding_registers(14, 1)
    print(f"Valve 3 status: {status}")
else:
    print("❌ Connection failed")
```

## Optimasi

### Reduce APK Size

Edit `buildozer.spec`:
```ini
# Exclude unused files
source.exclude_dirs = tests,bin,venv,.venv,__pycache__,build,dist,_archived_files,exSiemensProfinet

# Exclude heavy libraries jika tidak dipakai
# Misalnya hapus cx-Oracle jika tidak konek ke Epicor
```

### Performance

1. **Database:** Gunakan WAL mode untuk SQLite
2. **Static Files:** Collect static files sebelum build
3. **Logging:** Reduce log level di production

## Next Steps

Setelah APK berhasil:

1. **Setup Auto-start:** Service Modbus jalan otomatis saat HP boot
2. **Battery Optimization:** Whitelist app agar tidak di-kill
3. **Monitoring:** Setup notification untuk error/disconnect
4. **Security:** Enable HTTPS untuk web interface
5. **Backup:** Auto backup database ke cloud

## Alternatif: Termux (Quick Test)

Untuk testing cepat tanpa build APK:

```bash
# Install Termux dari F-Droid atau Play Store
# Di Termux:
pkg install python git
pip install django pyModbusTCP

# Clone project
git clone <repo-url>
cd mowilex999

# Install requirements
pip install -r requirements.txt

# Run server
python main.py
```

Akses dari browser HP: `http://localhost:8000`

---

**Status Build:** Ready ✅  
**Platform:** Android 5.0+ (API 21+)  
**Size:** ~50-80 MB (depends on architecture)  
**Tested On:** Android 11, 12, 13
