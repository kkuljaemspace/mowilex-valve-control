# 📱 Mowilex Valve Control - Android Deployment Summary

## ✅ Files Yang Sudah Disiapkan

### 1. Build Configuration
- **`buildozer.spec`** - Konfigurasi lengkap untuk build Android APK
  - Package: `com.mowilex.mowilexvalve`
  - Version: 1.0.0
  - Target: Android 5.0+ (API 21-33)
  - Architectures: arm64-v8a, armeabi-v7a
  - Permissions: Internet, Network, Storage

### 2. Application Entry Points
- **`main.py`** - Main entry point untuk Android app
  - Auto-start Modbus server di background thread
  - Django web server di port 8000
  - Graceful shutdown handling

- **`modbus_service.py`** - Background service
  - Android Service untuk Modbus server
  - Auto-restart on failure
  - Persistent bahkan saat app minimize

### 3. Build Scripts
- **`prepare_android_build.sh`** - Preparation script
  - Collect static files
  - Run migrations
  - Create default config
  - Cleanup files
  - Verify requirements

### 4. Documentation
- **`ANDROID_BUILD_GUIDE.md`** - Comprehensive guide
  - Build instructions
  - Configuration steps
  - Troubleshooting
  - Testing procedures

- **`QUICK_START.md`** - Quick reference
  - 4 deployment options
  - Step-by-step guides
  - Recommendations

### 5. CI/CD
- **`.github/workflows/build-android.yml`** - GitHub Actions
  - Auto-build APK on push/PR
  - Caching untuk faster builds
  - Upload artifacts
  - Auto-release on tags

---

## 🚀 Cara Build APK

### Opsi 1: GitHub Actions (Paling Mudah untuk Mac User)

1. **Push ke GitHub:**
```bash
git init
git add .
git commit -m "Initial commit - Mowilex Valve Control"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

2. **GitHub Actions akan auto-build APK**
   - Check tab "Actions" di GitHub repo
   - Download APK dari "Artifacts"
   - Build time: ~15-20 menit

3. **Install APK ke HP Android**

### Opsi 2: Docker (Build di Mac)

```bash
# Pull buildozer image
docker pull kivy/buildozer

# Build APK
docker run --rm -v "$(pwd)":/home/user/app \
    kivy/buildozer android debug

# APK ada di: bin/
```

### Opsi 3: Linux VM

```bash
# Di Ubuntu/Debian VM
./prepare_android_build.sh
buildozer android debug
```

### Opsi 4: Termux (Testing Tanpa Build)

```bash
# Di Termux Android
pkg install python git
git clone <repo> atau copy files manual
pip install django pyModbusTCP pillow
python main.py
```

---

## ⚙️ Konfigurasi Setelah Install

### 1. First Run

```bash
# Buka browser di HP
http://localhost:8000

# Login dengan superuser
# (dibuat via manage.py createsuperuser)
```

### 2. Modbus Settings

```
Menu: Modbus Settings

Android IP: 0.0.0.0 (listen all interfaces)
Android Port: 9502 (WAJIB > 1024!)
PLC IP: 192.168.1.100 (IP PLC di network)
PLC Port: 502

Auto Start: ✓ (checked)
```

### 3. Network Setup

**WiFi Connection:**
- HP dan PLC di WiFi yang sama
- Cek IP HP: Settings > WiFi > Advanced
- PLC connect ke IP tersebut port 9502

**HP Hotspot:**
- Enable Hotspot
- PLC connect ke hotspot
- IP HP biasanya: 192.168.43.1
- PLC target: 192.168.43.1:9502

---

## 🧪 Testing

### Test Modbus dari PC

```python
from pyModbusTCP.client import ModbusClient

# Ganti dengan IP HP Android
client = ModbusClient(host='192.168.1.XXX', port=9502, auto_open=True)

# Write command
client.write_single_register(3, 1)  # Open valve 3

# Read status
status = client.read_holding_registers(14, 1)  # Status valve 3
print(f"Valve 3: {'OPEN' if status[0] == 1 else 'CLOSED'}")
```

### Check Logs (via adb)

```bash
# Real-time logs
adb logcat | grep python

# Django logs
adb logcat | grep django

# Modbus logs  
adb logcat | grep -i modbus
```

---

## 📊 APK Details

**Expected APK Size:** 50-80 MB  
**Supported Android:** 5.0 - 14+ (API 21-33+)  
**Architectures:** arm64-v8a, armeabi-v7a  
**Permissions:**
- INTERNET - untuk web server & Modbus
- ACCESS_NETWORK_STATE - detect network  
- ACCESS_WIFI_STATE - WiFi info
- WRITE_EXTERNAL_STORAGE - database backup

**Services:**
- ModbusService - background Modbus server
- Django runserver - web interface

---

## 🔧 Troubleshooting

### Build Fails
```bash
buildozer android clean
rm -rf .buildozer
buildozer -v android debug  # verbose mode
```

### Port Already in Use
```bash
# Di Android via adb
adb shell netstat -tulpn | grep :9502
adb shell su -c "kill <PID>"
```

### App Crashes
```bash
# Check logs
adb logcat | grep -E "(python|django|modbus)"

# Re-install
adb uninstall com.mowilex.mowilexvalve
buildozer android deploy run
```

### Database Errors
```bash
# Connect to app
adb shell
cd /data/data/com.mowilex.mowilexvalve/files/app

# Run migrations
python manage.py migrate
python manage.py createsuperuser
```

---

## 📈 Production Checklist

- [ ] Change DEBUG = False in settings.py
- [ ] Set ALLOWED_HOSTS properly
- [ ] Generate SECRET_KEY yang secure
- [ ] Setup HTTPS untuk web interface
- [ ] Enable battery optimization whitelist
- [ ] Setup auto-start on boot
- [ ] Configure backup strategy
- [ ] Test pada multiple Android versions
- [ ] Prepare user documentation
- [ ] Setup monitoring & alerts

---

## 🎯 Next Steps

1. **Build APK:**
   - Push to GitHub → auto-build via Actions, ATAU
   - Use Docker on Mac, ATAU
   - Use Linux VM/Cloud

2. **Test di HP:**
   - Install APK
   - Configure Modbus settings
   - Test dengan simulator atau PLC asli

3. **Deploy Production:**
   - Build release APK (signed)
   - Distribute ke users
   - Monitor & support

---

## 📞 Support

Jika ada pertanyaan atau issue:
1. Check documentation files
2. Review troubleshooting section  
3. Check GitHub Actions logs (jika pakai GitHub)
4. Test dengan Termux dulu untuk isolate masalah

**Status:** Ready for build! ✅
