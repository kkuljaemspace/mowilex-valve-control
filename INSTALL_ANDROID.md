# 📱 Panduan Install Mowilex di Android

## 🎯 Cara Tercepat (Recommended)

### LANGKAH 1: Install Aplikasi yang Dibutuhkan

1. **Install F-Droid** (App Store untuk open source)
   - Download: https://f-droid.org/
   - Install APK yang didownload

2. **Install Termux dari F-Droid**
   - Buka F-Droid
   - Search "Termux"
   - Install (versi terbaru v0.118+)
   - ⚠️ **JANGAN install dari Play Store!**

3. **Install Termux:Boot dari F-Droid** (untuk auto-start)
   - Di F-Droid, search "Termux:Boot"
   - Install

### LANGKAH 2: Setup Termux (First Time)

1. **Buka Termux**, tunggu sampai prompt `$` muncul

2. **Update package manager:**
```bash
pkg update -y
pkg upgrade -y
```

3. **Install Python dan dependencies:**
```bash
pkg install -y python git
```

4. **Install pip packages:**
```bash
pip install --upgrade pip
pip install django pyModbusTCP django-select2 django-tables2 pillow django-import-export
```

### LANGKAH 3: Copy Project ke Android

**Pilihan A: Via GitHub (Recommended)**
```bash
cd ~
git clone https://github.com/kkuljaemspace/mowilex-valve-control.git
cd mowilex-valve-control
```

**Pilihan B: Via File Transfer (jika ada file di PC)**
```bash
# Di PC/Mac, transfer via adb atau cable
adb push /Users/chikal/Code/mowilex999 /sdcard/mowilex999

# Di Termux Android
cp -r /sdcard/mowilex999 ~/mowilex-valve-control
cd ~/mowilex-valve-control
```

**Pilihan C: Via Manual (copy paste)**
```bash
# Buat folder
mkdir -p ~/mowilex-valve-control
cd ~/mowilex-valve-control

# Download file by file dari GitHub raw
# Atau gunakan text editor di Termux untuk copy paste
```

### LANGKAH 4: Setup Database

```bash
cd ~/mowilex-valve-control
python manage.py migrate
python manage.py createsuperuser
# Isi: username, email (optional), password
```

### LANGKAH 5: Setup Auto-Start (Optional)

1. **Setup wake lock:**
```bash
termux-wake-lock
```

2. **Buat boot script:**
```bash
mkdir -p ~/.termux/boot

cat > ~/.termux/boot/start-mowilex.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 15
termux-wake-lock
cd ~/mowilex-valve-control
python main.py >> ~/mowilex-boot.log 2>&1 &
echo $! > ~/mowilex.pid
EOF

chmod +x ~/.termux/boot/start-mowilex.sh
```

3. **Setup Termux:Boot app:**
   - Buka aplikasi Termux:Boot
   - Grant semua permissions yang diminta
   - Settings Android → Apps → Termux → Battery → Unrestricted
   - Settings Android → Apps → Termux:Boot → Battery → Unrestricted

### LANGKAH 6: Start Mowilex

**Start Manual:**
```bash
cd ~/mowilex-valve-control
python main.py
```

Tunggu sampai muncul:
```
🚀 MOWILEX VALVE CONTROL SYSTEM
✅ Modbus TCP Server: 0.0.0.0:9502
✅ Django Web Server: http://0.0.0.0:8000
```

### LANGKAH 7: Akses Web Interface

1. **Buka browser di Android** (Chrome/Firefox)

2. **Akses:** `http://localhost:8000`

3. **Login** dengan username/password yang dibuat di LANGKAH 4

4. **Add to Home Screen** (optional):
   - Chrome menu → Add to Home Screen
   - Beri nama "Mowilex"
   - Icon akan muncul di home screen

---

## 🔧 Troubleshooting

### Problem: "pkg: command not found"
```bash
# Update Termux
apt update
apt upgrade
```

### Problem: "Permission denied"
```bash
# Allow storage access
termux-setup-storage
# Grant permission di popup
```

### Problem: Port 8000 sudah dipakai
```bash
# Kill process lama
pkill -f python
# Start lagi
python main.py
```

### Problem: "Module not found"
```bash
# Install ulang dependencies
pip install django pyModbusTCP django-select2 django-tables2 pillow django-import-export
```

### Problem: Auto-start tidak jalan
```bash
# Cek log
cat ~/mowilex-boot.log

# Test manual
~/.termux/boot/start-mowilex.sh

# Pastikan battery optimization disabled
```

---

## 📋 Quick Reference Commands

```bash
# Start Mowilex
cd ~/mowilex-valve-control && python main.py

# Stop Mowilex
pkill -f "python main.py"

# Check if running
ps aux | grep python
netstat -tuln | grep 8000

# View logs
cat ~/mowilex-boot.log

# Update code from GitHub
cd ~/mowilex-valve-control
git pull

# Backup database
cp db.sqlite3 /sdcard/backup-$(date +%Y%m%d).db

# Reset database (HATI-HATI!)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 🌐 Akses dari Device Lain

1. **Cek IP Android:**
```bash
ifconfig wlan0 | grep "inet "
# Contoh output: inet 192.168.1.100
```

2. **Dari PC/Laptop di jaringan yang sama:**
   - Buka browser
   - Akses: `http://192.168.1.100:8000`

3. **Dari PLC:**
   - Set PLC sebagai Modbus TCP Client
   - Target: `192.168.1.100:9502`

---

## 🎨 Tips & Tricks

### 1. Akses mudah tanpa ketik URL
```bash
# Install shortcut creator
pkg install termux-api

# Buat shortcut
termux-notification --title "Mowilex" --content "Tap to open" --action "am start -a android.intent.action.VIEW -d http://localhost:8000"
```

### 2. Keep screen on saat development
- Settings → Developer Options → Stay awake (saat charging)

### 3. Background mode
```bash
# Install termux-services
pkg install termux-services

# Enable service
sv-enable mowilex

# Start/stop
sv up mowilex
sv down mowilex
```

### 4. SSH dari PC ke Android
```bash
# Di Termux
pkg install openssh
sshd

# Di PC
ssh -p 8022 192.168.1.100
```

---

## 📱 Screenshot Hasil

Setelah sukses, Anda akan lihat:

1. **Terminal Termux:**
```
🚀 MOWILEX VALVE CONTROL SYSTEM
📅 Started: 2025-12-11 12:00:00
✅ Modbus TCP Server: 0.0.0.0:9502
✅ Django Web Server: http://0.0.0.0:8000
```

2. **Browser:**
   - Login page Mowilex
   - Dashboard dengan status valve
   - Modbus settings page
   - Floating widget (hijau = running)

---

## 🆘 Butuh Bantuan?

### Log Files
- `~/mowilex-boot.log` - Auto-start log
- `~/mowilex-valve-control/` - Main project
- Termux log: `logcat | grep Termux`

### Common Issues
1. ❌ "Can't assign requested address" → Gunakan 0.0.0.0, bukan IP spesifik
2. ❌ "Port already in use" → Kill process lama: `pkill -f python`
3. ❌ "Module not found" → Install ulang: `pip install -r requirements.txt`
4. ❌ "Database locked" → Stop semua instance Python yang running

---

**✅ Selesai!** Mowilex siap digunakan di Android.
