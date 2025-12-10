# 📱 CARA MENDAPATKAN APK

Karena Mac tidak bisa build APK langsung tanpa Docker/Linux, ada 3 cara:

---

## ✅ CARA 1: INSTALL DOCKER DESKTOP (Recommended)

### 1. Install Docker
```bash
# Download & Install:
https://www.docker.com/products/docker-desktop

# Atau via Homebrew:
brew install --cask docker
```

### 2. Start Docker Desktop
- Buka Docker Desktop app
- Tunggu hingga status "Running"

### 3. Build APK
```bash
cd /Users/chikal/Code/mowilex999
./build_apk_docker.sh
```

**⏱️ Waktu:** 20-30 menit (first build)  
**📦 Hasil:** `bin/mowilexvalve-1.0.0-arm64-v8a-debug.apk`

---

## ✅ CARA 2: TANPA BUILD - LANGSUNG PAKAI TERMUX

Tidak perlu APK! Langsung jalankan di HP:

### 1. Install Termux
- Download dari: https://f-droid.org/en/packages/com.termux/
- JANGAN dari Play Store (versi lama)

### 2. Copy Project ke HP
- Via USB: Copy folder `mowilex999` ke `/storage/emulated/0/`
- Via Git: Clone repository (jika sudah di GitHub)

### 3. Setup di Termux
```bash
# Di Termux:
pkg install python git
pip install django pyModbusTCP pillow

# Ke folder project
cd /storage/emulated/0/mowilex999

# Setup
python manage.py migrate
python manage.py createsuperuser

# Jalankan
python main.py
```

### 4. Akses
- Browser HP: `http://localhost:8000`

**⏱️ Waktu:** 10-15 menit  
**💾 Size:** 0 MB (no APK needed)

---

## ✅ CARA 3: BUILD VIA GITHUB ACTIONS

### 1. Create GitHub Repository
```bash
# Di terminal Mac:
cd /Users/chikal/Code/mowilex999

git init
git add .
git commit -m "Initial commit"

# Buat repo di GitHub.com, lalu:
git remote add origin https://github.com/USERNAME/mowilex-valve.git
git push -u origin main
```

### 2. GitHub Actions Auto-Build
- GitHub akan otomatis build APK (via `.github/workflows/build-android.yml`)
- Check progress di: `https://github.com/USERNAME/REPO/actions`

### 3. Download APK
- Setelah build selesai (~20 menit)
- Klik workflow → "Artifacts"
- Download APK

**⏱️ Waktu:** 20-30 menit  
**📦 Hasil:** APK ready untuk install

---

## 🎯 REKOMENDASI SAYA

### Untuk Testing Cepat:
→ **CARA 2 (Termux)** - Paling cepat, tidak perlu build

### Untuk Distribusi:
→ **CARA 1 (Docker)** atau **CARA 3 (GitHub)** - Dapat APK installer

---

## 📞 Mau Dibantu?

Pilih salah satu dan saya guide step-by-step:

1. **Install Docker** → Saya bantu setup Docker + build
2. **Setup Termux** → Saya guide install di HP
3. **Push GitHub** → Saya bantu create repo + auto-build

Mau yang mana? 😊
