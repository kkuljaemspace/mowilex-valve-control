# 🚀 Mowilex Auto-Start di Android (Termux)

## 📋 Requirements

### 1. Install Aplikasi
- **Termux** - Terminal emulator (v0.118+)
  - Download: [F-Droid](https://f-droid.org/en/packages/com.termux/)
  - ⚠️ **WAJIB dari F-Droid**, bukan Play Store!
  
- **Termux:Boot** - Auto-start service
  - Download: [F-Droid](https://f-droid.org/en/packages/com.termux.boot/)
  - Diperlukan untuk auto-start saat device nyala

### 2. Versi yang Direkomendasikan
```
Termux: v0.118 atau lebih baru
Termux:Boot: v0.7 atau lebih baru
Android: 7.0 (Nougat) atau lebih tinggi
```

## 🔧 Setup Auto-Start

### Metode 1: Automatic Setup (Recommended)

1. **Copy file ke Android:**
```bash
# Di Mac/PC, push ke Android via adb
adb push termux-autostart-setup.sh /sdcard/
```

2. **Di Termux Android, jalankan:**
```bash
# Copy dari storage
cp /sdcard/termux-autostart-setup.sh ~/
chmod +x ~/termux-autostart-setup.sh

# Run setup
./termux-autostart-setup.sh
```

### Metode 2: Manual Setup

1. **Install Termux:Boot** dari F-Droid

2. **Setup permissions di Termux:**
```bash
termux-wake-lock
```

3. **Buat boot script:**
```bash
mkdir -p ~/.termux/boot
nano ~/.termux/boot/start-mowilex.sh
```

Isi dengan:
```bash
#!/data/data/com.termux/files/usr/bin/bash

# Wait untuk sistem siap
sleep 15

# Acquire wake lock
termux-wake-lock

# Log
LOG_FILE="$HOME/mowilex-boot.log"
echo "🚀 Starting Mowilex at $(date)" > "$LOG_FILE"

# Start Django
cd ~/mowilex-valve-control
source venv/bin/activate 2>/dev/null
python main.py >> "$LOG_FILE" 2>&1 &

# Save PID
echo $! > ~/mowilex.pid
```

4. **Buat executable:**
```bash
chmod +x ~/.termux/boot/start-mowilex.sh
```

## 🎯 Konfigurasi Termux:Boot

1. **Buka aplikasi Termux:Boot**
2. **Grant semua permissions:**
   - Boot permission
   - Battery optimization - disable untuk Termux & Termux:Boot
   - Background execution

3. **Settings Android:**
   - Settings → Apps → Termux
   - Battery → Unrestricted
   - Settings → Apps → Termux:Boot
   - Battery → Unrestricted

## 🧪 Testing

### Test Auto-Start:
```bash
# Restart device
adb reboot

# Setelah boot, cek log
cat ~/mowilex-boot.log

# Cek process
ps aux | grep python

# Test akses
curl http://localhost:8000
```

### Manual Start/Stop:
```bash
# Start manual
~/start-mowilex.sh

# Stop
~/stop-mowilex.sh

# Check status
cat ~/mowilex.pid
```

## 🔍 Troubleshooting

### Auto-start tidak jalan?

1. **Cek Termux:Boot permissions:**
```bash
# Di Termux
ls -la ~/.termux/boot/
# Harus ada start-mowilex.sh dengan execute permission
```

2. **Cek log boot:**
```bash
cat ~/mowilex-boot.log
```

3. **Cek battery optimization:**
```
Settings → Apps → Termux → Battery → Unrestricted
Settings → Apps → Termux:Boot → Battery → Unrestricted
```

4. **Cek wake lock:**
```bash
termux-wake-lock
```

5. **Test manual start:**
```bash
~/.termux/boot/start-mowilex.sh
```

### Port 8000 sudah dipakai?

```bash
# Cek port
netstat -tuln | grep 8000

# Kill process lama
pkill -f "python main.py"
```

### Django tidak start?

```bash
# Cek manual
cd ~/mowilex-valve-control
source venv/bin/activate
python main.py
```

## 📱 Akses dari Browser

Setelah auto-start berhasil:

1. **Di Android (localhost):**
   ```
   http://localhost:8000
   ```

2. **Dari device lain (same network):**
   ```
   http://<android-ip>:8000
   ```
   
   Cek Android IP: `ifconfig wlan0` di Termux

## 🎨 Progressive Web App (PWA)

Untuk akses lebih mudah tanpa buka browser:

1. Buka `http://localhost:8000` di Chrome
2. Menu → "Add to Home Screen"
3. Icon Mowilex akan muncul di home screen
4. Buka seperti native app!

## 🔋 Battery Optimization

Untuk prevent Android kill Termux:

```bash
# Request battery optimization whitelist
termux-battery-status

# Di Settings Android:
Settings → Battery → Battery Optimization
→ All apps → Termux → Don't optimize
→ All apps → Termux:Boot → Don't optimize
```

## 🔐 Security Tips

1. **Batasi akses jaringan:**
   Edit `xcore/settings.py`:
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.x.x']
   ```

2. **Enable authentication:**
   Login wajib untuk akses Modbus settings

3. **Firewall (optional):**
   Block port 8000 dari internet, allow hanya local network

## 📝 Maintenance Commands

```bash
# Lihat log
cat ~/mowilex-boot.log

# Restart service
~/stop-mowilex.sh && ~/start-mowilex.sh

# Update code dari GitHub
cd ~/mowilex-valve-control
git pull
~/stop-mowilex.sh
~/start-mowilex.sh

# Backup database
cp ~/mowilex-valve-control/db.sqlite3 /sdcard/mowilex-backup-$(date +%Y%m%d).db
```

## 🆘 Support

Jika masalah:
1. Cek `~/mowilex-boot.log`
2. Test manual start: `python ~/mowilex-valve-control/main.py`
3. Cek permissions Termux:Boot
4. Disable battery optimization
5. Pastikan waktu sleep cukup (15 detik default)
