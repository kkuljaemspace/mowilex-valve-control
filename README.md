# Mowilex Valve Control System

Django-based web application untuk kontrol valve industri via Modbus TCP/IP. Aplikasi ini dapat berjalan di Android sebagai Modbus Server (Slave) yang dikontrol oleh PLC (Master).

## 🚀 Features

- ✅ **Web Interface** - Django admin untuk management valve
- ✅ **Modbus TCP/IP Server** - Port 9502+ untuk Android compatibility
- ✅ **Real-time Sync** - Database ↔️ Modbus registers
- ✅ **Multi-Valve Control** - Support 11 valves (register 0-10)
- ✅ **Status Monitoring** - Real-time valve status (register 11-20)
- ✅ **Android Ready** - APK build via GitHub Actions

## 📱 Architecture

```
PLC (Master/Client)  ←→  Android (Slave/Server)
                          ↓
                    Modbus Server (Port 9502)
                          ↓
                    Django Web App (Port 8000)
                          ↓
                    SQLite Database
```

## 🔧 Register Mapping

| Register | Function | R/W | Description |
|----------|----------|-----|-------------|
| 0-10 | Command | Write | PLC writes valve commands |
| 11-20 | Status | Read | PLC reads valve status |

**Example:**
- Write register 3 = 1 → Open valve 3
- Read register 14 → Get valve 3 status (3+11=14)

## 🛠️ Installation

### Local Development (Mac/Linux)

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/mowilex-valve.git
cd mowilex-valve

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Run server
python main.py
```

Access:
- Web UI: `http://localhost:8000`
- Modbus: `localhost:9502`

### Android via Termux

```bash
# Install Termux from F-Droid
pkg install python git
pip install django pyModbusTCP pillow

# Clone and setup
git clone https://github.com/YOUR_USERNAME/mowilex-valve.git
cd mowilex-valve
python manage.py migrate
python main.py
```

### Android APK

Download latest APK from [Releases](https://github.com/YOUR_USERNAME/mowilex-valve/releases) or build automatically via GitHub Actions on every push to `main` branch.

## 📦 Build APK

APK builds automatically via GitHub Actions when you push to `main`:

```bash
git add .
git commit -m "Update"
git push origin main
```

Check build status: Actions tab → Download from Artifacts

Manual build with Docker:
```bash
docker pull kivy/buildozer
docker run --rm -v "$(pwd)":/home/user/app kivy/buildozer android debug
```

## ⚙️ Configuration

After first run, configure Modbus settings:

1. Open `http://localhost:8000/modbus/settings/`
2. Set:
   - **Android IP:** `0.0.0.0` (listen all interfaces)
   - **Android Port:** `9502` (must be > 1024 for Android)
   - **PLC IP:** Your PLC IP address
   - **PLC Port:** `502` (standard Modbus)
3. Enable **Auto Start**
4. Click **Start Server**

## 🧪 Testing

### Start Modbus Server
```bash
python start_modbus_server.py
```

### Test with Simulator
```bash
# Valve control test
python modbus_master_simulator.py --valve-control

# Continuous monitoring
python modbus_master_simulator.py --monitor

# Interactive mode
python modbus_master_simulator.py --interactive
```

### Test from Python
```python
from pyModbusTCP.client import ModbusClient

client = ModbusClient(host='localhost', port=9502, auto_open=True)

# Write command: Open valve 3
client.write_single_register(3, 1)

# Read status: Check valve 3
status = client.read_holding_registers(14, 1)
print(f"Valve 3: {'OPEN' if status[0] == 1 else 'CLOSED'}")
```

## 📱 Android Deployment

### Network Setup

**WiFi Connection:**
- Connect Android and PLC to same WiFi
- Note Android IP: Settings → WiFi → Advanced
- PLC connects to `<android-ip>:9502`

**Mobile Hotspot:**
- Enable Hotspot on Android
- Connect PLC to hotspot
- Android IP usually: `192.168.43.1`
- PLC connects to `192.168.43.1:9502`

### Port Configuration

⚠️ **IMPORTANT:** Android blocks ports < 1024 for non-root apps!

Always use port ≥ 1024 (recommended: 9502)

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md)
- [Android Build Guide](ANDROID_BUILD_GUIDE.md)
- [Modbus Communication](MODBUS_COMMUNICATION_EXPLAINED.md)
- [Command Reference](COMMANDS.md)
- [Deployment Summary](DEPLOYMENT_SUMMARY.md)

## 🛠️ Tech Stack

- **Backend:** Django 5.1.1
- **Modbus:** pyModbusTCP
- **Database:** SQLite3
- **Frontend:** Bootstrap 5
- **Android Build:** Buildozer + python-for-android

## 📋 Requirements

```
Django==5.1.1
pyModbusTCP
pillow
requests
python-dateutil
```

See [requirements.txt](requirements.txt) for full list.

## 🔒 Security Notes

- Change `SECRET_KEY` in production
- Set `DEBUG = False` for production
- Configure `ALLOWED_HOSTS` properly
- Use HTTPS for web interface in production
- Implement firewall rules for Modbus port

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Mowilex Team**

## 🙏 Acknowledgments

- Django Framework
- pyModbusTCP library
- Buildozer & python-for-android projects

## 📞 Support

- Create an issue for bug reports
- Check [documentation](QUICK_START.md) for common questions
- Review [troubleshooting guide](ANDROID_BUILD_GUIDE.md#troubleshooting)

---

**Status:** Production Ready ✅  
**Version:** 1.0.0  
**Last Updated:** December 2025
