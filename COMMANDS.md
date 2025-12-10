# ⚡ Quick Command Reference

## 🏗️ Build Commands

```bash
# === PREPARATION ===
./prepare_android_build.sh              # Prepare project for build
python manage.py collectstatic          # Collect static files
python manage.py migrate                # Run migrations

# === BUILD APK ===
buildozer android debug                 # Build debug APK
buildozer android release               # Build release APK
buildozer android clean                 # Clean build cache

# === DEPLOY ===
buildozer android deploy                # Deploy to connected device
buildozer android deploy run            # Deploy and run
buildozer android logcat                # View logs from device

# === DOCKER BUILD ===
docker pull kivy/buildozer              # Pull buildozer image
docker run --rm -v "$(pwd)":/home/user/app kivy/buildozer android debug
```

## 📱 Android Commands (adb)

```bash
# === INSTALL ===
adb install -r bin/*.apk                # Install APK
adb uninstall com.mowilex.mowilexvalve  # Uninstall app

# === LOGS ===
adb logcat | grep python                # Python logs
adb logcat | grep django                # Django logs
adb logcat | grep -i modbus             # Modbus logs
adb logcat -c                           # Clear logs

# === DEBUG ===
adb shell                               # Shell into device
adb shell pm list packages | grep mowilex  # Check if installed
adb shell am start -n com.mowilex.mowilexvalve/org.kivy.android.PythonActivity

# === NETWORK ===
adb shell netstat -tulpn | grep :9502   # Check port 9502
adb shell ifconfig                      # Check IP address
```

## 🚀 Development Commands

```bash
# === LOCAL TESTING ===
python manage.py runserver 0.0.0.0:8000     # Start Django
python start_modbus_server.py               # Start Modbus server
python modbus_master_simulator.py --valve-control  # Test simulator

# === DATABASE ===
python manage.py makemigrations         # Create migrations
python manage.py migrate                # Apply migrations
python manage.py createsuperuser        # Create admin user
python manage.py shell                  # Django shell

# === TESTING ===
python modbus_master_simulator.py --valve-control    # Valve control test
python modbus_master_simulator.py --monitor          # Monitoring mode
python modbus_master_simulator.py --interactive      # Interactive mode
```

## 🔧 Termux Commands (Android)

```bash
# === SETUP ===
pkg update && pkg upgrade               # Update packages
pkg install python git                  # Install Python
pip install django pyModbusTCP pillow   # Install dependencies
termux-setup-storage                    # Access to storage

# === RUN ===
python main.py                          # Start app
python manage.py runserver 0.0.0.0:8000 # Django only
python start_modbus_server.py           # Modbus only

# === BACKGROUND ===
nohup python main.py > app.log 2>&1 &   # Run in background
pkill -f main.py                        # Stop app
```

## 🐳 Docker Commands

```bash
# === BUILD ===
docker pull kivy/buildozer
docker run --rm -v "$(pwd)":/home/user/app kivy/buildozer android debug

# === WITH CACHE ===
docker run --rm \
    -v "$(pwd)":/home/user/app \
    -v "$HOME/.buildozer":/home/user/.buildozer \
    kivy/buildozer android debug
```

## 🌐 Network Testing

```bash
# === CHECK CONNECTIVITY ===
ping <android-ip>                       # Test connection
nc -zv <android-ip> 9502                # Test port 9502
nmap <android-ip>                       # Scan all ports

# === MODBUS TEST (Python) ===
python -c "
from pyModbusTCP.client import ModbusClient
c = ModbusClient(host='<android-ip>', port=9502, auto_open=True)
print('Connected!' if c.is_open else 'Failed')
"
```

## 📊 Monitoring Commands

```bash
# === SYSTEM ===
adb shell top | grep mowilex            # CPU usage
adb shell dumpsys battery               # Battery status
adb shell dumpsys meminfo com.mowilex.mowilexvalve  # Memory

# === LOGS ===
adb logcat -s python:D *:S              # Python logs only
adb logcat -v time | grep ERROR         # Errors only
adb logcat -d > app_log.txt             # Save logs to file
```

## 🔐 Production Commands

```bash
# === COLLECT STATIC ===
python manage.py collectstatic --noinput --clear

# === BUILD RELEASE ===
buildozer android release

# === SIGN APK ===
keytool -genkey -v -keystore mowilex.keystore -alias mowilex \
    -keyalg RSA -keysize 2048 -validity 10000

jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
    -keystore mowilex.keystore \
    bin/*.apk mowilex

zipalign -v 4 bin/*-unsigned.apk bin/mowilex-release.apk
```

## 🛠️ Troubleshooting

```bash
# === CLEAN BUILD ===
buildozer android clean
rm -rf .buildozer
rm -rf bin

# === RESET DATABASE ===
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser

# === FIX PERMISSIONS ===
chmod +x *.sh *.py
find . -type d -exec chmod 755 {} \;
find . -type f -name "*.py" -exec chmod 644 {} \;

# === CLEAR CACHE ===
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

## 📦 APK Locations

```bash
# Debug APK
bin/mowilexvalve-1.0.0-arm64-v8a-debug.apk
bin/mowilexvalve-1.0.0-armeabi-v7a-debug.apk

# Release APK  
bin/mowilexvalve-1.0.0-arm64-v8a-release.apk

# GitHub Actions Artifacts
https://github.com/<user>/<repo>/actions
```

## 🔗 Quick URLs

```
Web Interface:  http://localhost:8000
Admin Panel:    http://localhost:8000/admin
Modbus Config:  http://localhost:8000/modbus/settings/
API Status:     http://localhost:8000/api/modbus/status/

From Network:   http://<android-ip>:8000
Modbus Server:  <android-ip>:9502
```

## 📝 Configuration Files

```
buildozer.spec                  # Build configuration
xcore/settings.py              # Django settings
project/modbus_service.py      # Modbus service
main.py                        # Entry point
prepare_android_build.sh       # Build preparation
```

---

**Tip:** Bookmark this file untuk quick reference! 🔖
