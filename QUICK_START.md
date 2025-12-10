# 🚀 Quick Start - Build Android APK

## Opsi 1: Build di Linux/Ubuntu (Recommended)

### Setup Environment
```bash
# 1. Install buildozer
pip3 install buildozer cython

# 2. Prepare project
./prepare_android_build.sh

# 3. Build APK (first build ~20-30 minutes)
buildozer android debug

# 4. Install ke HP
buildozer android deploy run
```

**Output:** `bin/mowilexvalve-1.0.0-arm64-v8a-debug.apk`

---

## Opsi 2: Build di macOS (Current System)

### ⚠️ CATATAN: Buildozer tidak support macOS untuk Android build

**Solusi:**

### A. Menggunakan Docker
```bash
# 1. Install Docker Desktop for Mac

# 2. Pull buildozer image
docker pull kivy/buildozer

# 3. Build APK
docker run --rm -v "$(pwd)":/home/user/app kivy/buildozer \
    android debug

# APK akan ada di: bin/
```

### B. Menggunakan GitHub Actions (Recommended untuk Mac)
Saya bisa buatkan GitHub Actions workflow yang auto-build APK di cloud!

### C. Menggunakan VM/WSL
- Install VirtualBox + Ubuntu
- Atau gunakan AWS/Google Cloud VM
- Build di VM Linux tersebut

---

## Opsi 3: Testing Tanpa Build APK (TERMUX)

**Paling mudah untuk testing cepat!**

### Di Android:
1. Install **Termux** dari F-Droid (bukan Play Store!)
   - Download: https://f-droid.org/en/packages/com.termux/

2. Di Termux:
```bash
# Update packages
pkg update && pkg upgrade

# Install Python dan dependencies
pkg install python git

# Clone project (atau copy manual)
# Jika ada git repo:
git clone <your-repo-url>
cd mowilex999

# Atau copy files via:
# - USB transfer
# - termux-setup-storage (akses ke /sdcard)

# Install Python packages
pip install django pyModbusTCP pillow

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Run server
python main.py
```

3. Akses di browser HP: `http://localhost:8000`

### Keuntungan Termux:
- ✅ Tidak perlu build APK
- ✅ Testing langsung di HP
- ✅ Mudah debug
- ✅ Update code langsung

### Kekurangan:
- ❌ User harus install Termux
- ❌ Tidak ada icon/launcher
- ❌ Perlu manual start setiap reboot

---

## Opsi 4: Deploy ke Server Cloud

Alternatif: Jalankan Django di cloud, HP Android hanya akses via browser

### Setup:
1. Deploy Django ke:
   - Heroku (free tier)
   - DigitalOcean ($5/month)
   - AWS EC2 (free tier 1 tahun)
   - Google Cloud Run

2. **CATATAN PENTING:** 
   - Modbus server tetap harus di Android (sebagai SLAVE)
   - Web interface bisa di cloud
   - PLC connect ke IP Android

### Hybrid Solution:
- **Web UI:** Di cloud server
- **Modbus Server:** Di Android (Termux)
- **Database:** Shared via API

---

## Rekomendasi Saya

Untuk project ini, urutan terbaik:

### 1️⃣ **Testing:** Gunakan **Termux** (paling cepat)
```bash
# Di Termux Android
pkg install python
pip install django pyModbusTCP
python main.py
```

### 2️⃣ **Production:** Ada 2 pilihan:

#### A. Full Android App (via Docker/GitHub Actions)
- Butuh laptop Linux atau gunakan GitHub Actions
- APK size ~50-80MB
- User tinggal install APK

#### B. Termux + AutoStart Script
- Lebih ringan
- Mudah update
- Buat script autostart di Termux

---

## Mau Saya Buatkan?

Pilih salah satu dan saya bantu setup:

1. **GitHub Actions workflow** untuk auto-build APK
2. **Docker setup** untuk build di Mac
3. **Termux optimized version** dengan autostart script
4. **Cloud deployment** guide (Django di cloud + Modbus di Android)

Mana yang mau dicoba?
