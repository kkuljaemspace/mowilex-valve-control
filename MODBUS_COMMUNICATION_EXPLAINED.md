# Cara Kerja Komunikasi Modbus - Android & PLC

## 🔍 Konsep Dasar: Client-Server

### Android = **SERVER/SLAVE** (Menunggu Koneksi)
- **Role:** Modbus TCP Server (Slave)
- **Action:** **LISTEN** di port tertentu
- **Tidak connect ke PLC**, hanya **menunggu** PLC connect ke sini

### PLC = **CLIENT/MASTER** (Menginisiasi Koneksi)
- **Role:** Modbus TCP Client (Master)
- **Action:** **CONNECT** ke Android
- **PLC yang aktif** membuat koneksi

## 📊 Diagram Komunikasi

```
STEP 1: Android Start Server
┌─────────────────────────┐
│  Android (Server)       │
│  IP: 192.168.2.100      │ ← IP Android di WiFi
│  PORT: 9502 (LISTEN)    │ ← Menunggu koneksi...
└─────────────────────────┘


STEP 2: PLC Connect ke Android
┌─────────────────────────┐
│  PLC (Client/Master)    │
│  IP: 192.168.2.99       │
│  Port Local: 54321      │ ← Port random otomatis
└───────────┬─────────────┘
            │
            │ TCP Connect TO:
            │ 192.168.2.100:9502
            │
┌───────────▼─────────────┐
│  Android (Server/Slave) │
│  IP: 192.168.2.100      │
│  PORT: 9502 (ACCEPT)    │ ← Terima koneksi
└─────────────────────────┘


STEP 3: Komunikasi Modbus
┌─────────────────────────┐
│  PLC                    │
│  Read Register 0        │ ─┐
└─────────────────────────┘  │
                             │ Request
                             │
┌─────────────────────────┐  │
│  Android                │ ◄┘
│  Response: Value = 2    │ ─┐
└─────────────────────────┘  │
                             │ Response
                             │
┌─────────────────────────┐  │
│  PLC                    │ ◄┘
│  Received: 2            │
└─────────────────────────┘
```

## ⚙️ Konfigurasi yang Benar

### Di Android (Django Settings):

| Setting | Value | Keterangan |
|---------|-------|------------|
| **Android IP** | `0.0.0.0` | Listen di semua network interface |
| **Android Port** | `9502` | Port untuk **LISTEN** (≥1024 untuk Android non-root) |
| **PLC IP** | `192.168.2.99` | Dokumentasi saja (IP PLC untuk referensi) |
| **PLC Port** | `502` | Dokumentasi saja (tidak digunakan Android) |

### Di PLC (Setting Modbus TCP Client):

```
Connection Type: Modbus TCP Client
Remote Host: 192.168.2.100    ← IP Android di network
Remote Port: 9502              ← Port yang Android listen
Connection Mode: Auto Connect
Timeout: 5000 ms
```

## ❌ Kesalahan Umum

### SALAH ❌
```
Android connect ke 192.168.2.99:502
```
**Kenapa salah:**
- Port 502 di-block di Android (privileged port)
- Android = Server, tidak perlu connect
- Arah komunikasi terbalik

### BENAR ✅
```
PLC connect ke 192.168.2.100:9502
Android hanya LISTEN di port 9502
```
**Kenapa benar:**
- Port 9502 tidak di-block (≥1024)
- PLC (client) yang connect ke Android (server)
- Arah komunikasi sesuai konsep Modbus TCP

## 🔐 Port & Security

### Port <1024 (Privileged Ports)
- **Port 502:** Standar Modbus TCP
- **Masalah:** Di Android/Linux, butuh **root access**
- **Solusi:** Gunakan port ≥1024

### Port ≥1024 (Non-Privileged)
- **Port 9502:** Recommended untuk Android
- **Tidak butuh root**
- **Aman digunakan**

### Port di PLC
- PLC **tidak butuh setting port lokal**
- OS PLC otomatis assign port random (ephemeral port) saat connect
- Biasanya range 49152-65535

## 🌐 Network Topology

```
┌──────────────────────────────────────┐
│  Local Network 192.168.2.0/24        │
│                                      │
│  ┌─────────────┐    ┌─────────────┐ │
│  │ Router/AP   │◄──►│   PLC       │ │
│  │ Gateway     │    │ .2.99       │ │
│  └──────┬──────┘    └─────────────┘ │
│         │                            │
│         │                            │
│  ┌──────▼──────┐                     │
│  │  Android    │                     │
│  │  .2.100     │                     │
│  │  Port: 9502 │                     │
│  └─────────────┘                     │
│                                      │
└──────────────────────────────────────┘
```

## 📝 Checklist Deployment

### 1. Setup Android
- [ ] Install aplikasi Mowilex
- [ ] Connect ke WiFi yang sama dengan PLC
- [ ] Cek IP Android (Settings → WiFi → IP Address)
- [ ] Buka Modbus Settings di app
- [ ] Set Android IP: `0.0.0.0`
- [ ] Set Android Port: `9502`
- [ ] Klik **Start Modbus Server**
- [ ] Pastikan status: **Running**

### 2. Setup PLC
- [ ] Setting Modbus TCP Client
- [ ] Remote IP: `<IP-Android>` (misal: `192.168.2.100`)
- [ ] Remote Port: `9502`
- [ ] Connection Type: Auto Connect
- [ ] Enable Modbus TCP Client

### 3. Testing
- [ ] PLC connect berhasil ke Android
- [ ] Test Read Register 0-10
- [ ] Test Write Register 0-10
- [ ] Test Read Register 11-20
- [ ] Cek database Django terisi data

## 🔧 Troubleshooting

### Problem: PLC tidak bisa connect
**Check:**
1. Ping Android dari PLC (atau sebaliknya)
2. Pastikan Android & PLC di network yang sama
3. Firewall Android tidak block port 9502
4. Modbus server di Android status **Running**

### Problem: Port 9502 already in use
**Solusi:**
1. Stop aplikasi lain yang pakai port 9502
2. Atau ganti port Android ke 9503, 9504, dst
3. Restart Modbus server

### Problem: Connection timeout
**Check:**
1. IP Android benar
2. Port Android benar
3. Network WiFi stabil
4. PLC setting timeout cukup besar (5-10 detik)

## 📚 Referensi Register Mapping

| Address | Direction | Description |
|---------|-----------|-------------|
| 0-10 | Django → Modbus | Command dari web ke PLC |
| 11-20 | Modbus → Django | Status dari PLC ke web |

### Contoh Penggunaan:
```python
# Via Django web:
# User set valve 3 = OPEN (value 1)
ValveSet.objects.filter(valve_number=3).update(status=1)

# Modbus server sync ke register 3
# PLC read register 3, dapat value = 1

# PLC write register 13 = 1 (valve 3 terbuka)
# Modbus server sync ke database
# Django web tampilkan status valve 3 = OPEN
```

## 🎯 Summary

**Yang Perlu Diingat:**
1. ✅ **Android = Server** (listen port 9502)
2. ✅ **PLC = Client** (connect ke Android:9502)
3. ✅ **Port 502 tidak dipakai** di Android
4. ✅ **PLC yang connect**, bukan Android
5. ✅ **Gunakan port ≥1024** di Android

**Jangan Bingung:**
- "Port PLC 502" di settings = hanya dokumentasi
- Yang penting: **PLC connect ke Android:9502**
- Android **TIDAK** connect ke PLC:502
