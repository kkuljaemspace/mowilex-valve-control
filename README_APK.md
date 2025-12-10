# 📱 BUILD APK - SIMPLE GUIDE

## 🚀 CARA TERCEPAT - 1 COMMAND

```bash
./install_docker_and_build.sh
```

Script ini akan:
1. ✅ Install Docker Desktop (jika belum ada)
2. ✅ Pull buildozer image
3. ✅ Build APK
4. ✅ APK siap di folder `bin/`

**⏱️ Total waktu:** ~30-40 menit (first time)

---

## 📦 HASIL

Setelah selesai, Anda akan punya:

```
bin/mowilexvalve-1.0.0-arm64-v8a-debug.apk  (~50-80 MB)
```

---

## 📲 INSTALL KE ANDROID

### Via USB:
```bash
adb install -r bin/*.apk
```

### Via Transfer Manual:
1. Copy APK ke HP (USB/Email/Cloud)
2. Buka file APK di HP
3. Install (enable "Unknown Sources" jika diminta)

---

## ⚙️ KONFIGURASI SETELAH INSTALL

1. Buka app "Mowilex Valve Control"
2. Browser otomatis buka `http://localhost:8000`
3. Login dengan user yang dibuat
4. Klik "Modbus Settings"
5. Set:
   - Android Port: `9502`
   - PLC IP: sesuai network Anda

---

## ❓ JIKA ADA MASALAH

### Docker tidak jalan:
```bash
open -a Docker  # Start Docker Desktop
```

### Build error:
```bash
# Clean dan rebuild
rm -rf .buildozer bin
./install_docker_and_build.sh
```

### Perlu bantuan:
Baca: `CARA_DAPAT_APK.md`

---

## ✅ READY!

Setelah APK terinstall:
- ✅ Modbus Server auto-start
- ✅ Web UI di localhost:8000
- ✅ Database sudah ter-setup
- ✅ Siap connect ke PLC

**Enjoy! 🎉**
