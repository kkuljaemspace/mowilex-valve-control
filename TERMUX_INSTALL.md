# Panduan Instalasi Termux - Mowilex Valve Control

## 📱 Instalasi di Android dengan Termux

### Langkah 1: Install Termux
1. Download Termux dari [F-Droid](https://f-droid.org/packages/com.termux/) (JANGAN dari Play Store, versi lama)
2. Install Termux:Boot dari F-Droid (untuk autostart)

### Langkah 2: Setup Otomatis
Jalankan di Termux:

```bash
# Download setup script
pkg install wget -y
wget https://raw.githubusercontent.com/kkuljaemspace/mowilex-valve-control/main/termux-setup.sh

# Jalankan setup
chmod +x termux-setup.sh
./termux-setup.sh
```

Setup akan otomatis:
- ✅ Install Python dan dependencies
- ✅ Clone project dari GitHub
- ✅ Setup database
- ✅ Buat admin user
- ✅ Setup autostart scripts

### Langkah 3: Jalankan Server

**Manual start:**
```bash
~/start-mowilex.sh
```

**Stop server:**
```bash
~/stop-mowilex.sh
```

**Cek status:**
```bash
~/status-mowilex.sh
```

### Langkah 4: Setup Autostart (Opsional)

1. Buka app **Termux:Boot** sekali (untuk activate)
2. Restart HP
3. Server akan otomatis jalan saat HP boot

### Langkah 5: Akses Web UI

**Di HP yang sama:**
- Browser: `http://localhost:8000`
- Atau tambahkan ke Home Screen (PWA)

**Dari HP/PC lain di jaringan yang sama:**
- `http://<IP-Android>:8000`
- Contoh: `http://192.168.1.100:8000`

**Cari IP Android:**
```bash
ifconfig wlan0 | grep inet
```

## 🔧 Troubleshooting

### Server tidak bisa diakses dari luar
```bash
# Cek IP Android
ifconfig

# Pastikan Django listen di 0.0.0.0, bukan 127.0.0.1
# Sudah diatur otomatis di main.py
```

### Port conflict (port 8000 atau 9502 sudah dipakai)
Edit `~/mowilex-valve-control/main.py` dan ganti port

### Lupa password admin
```bash
cd ~/mowilex-valve-control
python manage.py changepassword <username>
```

### Update ke versi terbaru
```bash
cd ~/mowilex-valve-control
git pull
python manage.py migrate
~/stop-mowilex.sh
~/start-mowilex.sh
```

## 📱 Membuat WebView App dengan MIT App Inventor

### Settingan yang Benar:
1. **Component**: WebViewer1
2. **Home URL**: `http://localhost:8000`
3. **Initialize**: Set WebViewer1.HomeUrl to global home
4. **PageLoaded**: Set WebViewer1.Visible to true

### Tips WebView:
- ✅ Pastikan Termux running di background
- ✅ WebView harus allow JavaScript
- ✅ Disable zoom control untuk UI lebih native
- ✅ Handle back button untuk navigasi

## 🔐 Keamanan

**WARNING**: Server berjalan tanpa authentication di network!

Untuk production:
1. Set `ALLOWED_HOSTS` di `xcore/settings.py`
2. Enable HTTPS dengan self-signed certificate
3. Tambahkan authentication di Modbus

## 📊 Monitoring

**Lihat log real-time:**
```bash
tail -f ~/mowilex.log
```

**Lihat log Modbus:**
```bash
cd ~/mowilex-valve-control
tail -f modbus.log
```

## 🎯 Testing Modbus

**Dari terminal lain:**
```bash
cd ~/mowilex-valve-control
python modbus_master_simulator.py --valve-control
```

**Dari PLC:**
- Host: `<IP-Android>`
- Port: `9502`
- Registers: 0-10 (command), 11-20 (status)

## 💡 Tips Performance

1. **Disable auto-reload** (sudah diatur di main.py)
2. **Gunakan SQLite** (sudah default)
3. **Jangan collectstatic** di Android (tidak perlu)
4. **Keep screen on** saat testing (Settings → Developer Options)

## 🔄 Uninstall

```bash
~/stop-mowilex.sh
rm -rf ~/mowilex-valve-control
rm ~/start-mowilex.sh ~/stop-mowilex.sh ~/status-mowilex.sh
rm ~/.termux/boot/start-mowilex.sh
```
