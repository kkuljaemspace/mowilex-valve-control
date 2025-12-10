# Build Django Mowilex sebagai Android APK

## 📱 Tools yang Digunakan

### **Opsi 1: Menggunakan Buildozer (Recommended)**
Buildozer adalah tool untuk compile Python app menjadi APK Android menggunakan Python-for-Android (p4a).

### **Opsi 2: Menggunakan Chaquopy**
Plugin Gradle untuk run Python di Android app (lebih complex, perlu Java/Kotlin).

## 🚀 Tutorial Build dengan Buildozer

### Prerequisites
```bash
# Install di Linux/Mac (tidak bisa di Windows native, pakai WSL)
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    libffi-dev \
    libssl-dev \
    python3-dev \
    python3-venv \
    zip \
    unzip \
    openjdk-11-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev

# Install Android SDK & NDK (akan otomatis oleh buildozer)
```

### Install Buildozer
```bash
pip install buildozer
pip install cython
```

### Persiapan Project

#### 1. Buat buildozer.spec
```bash
cd /Users/chikal/Code/mowilex999
buildozer init
```

#### 2. Edit `buildozer.spec`
```ini
[app]
# Nama aplikasi
title = Mowilex PLC Monitor

# Package name (harus huruf kecil, tidak ada spasi)
package.name = mowilexplc

# Domain (reverse DNS)
package.domain = com.lerix

# Source code directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas,html,css,js,json,txt,sql,db

# Source files to exclude
source.exclude_exts = spec
source.exclude_dirs = tests, bin, .venv, __pycache__, .git, _archived_files, staticfiles

# Application version
version = 1.0.0

# Application requirements
requirements = python3==3.12,kivy==2.3.0,django==6.0,pyModbusTCP,python-dateutil,requests,pillow,sqlalchemy

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API level
android.api = 33
android.minapi = 21

# Architecture
android.archs = arm64-v8a,armeabi-v7a

# Orientation
orientation = portrait

# Icon & Presplash
#icon.filename = %(source.dir)s/media/logo/icon.png
#presplash.filename = %(source.dir)s/media/logo/splash.png

# Wakelock (agar app tetap jalan di background)
android.wakelock = True

# Services (untuk run background task)
services = modbus:./service/modbus_service.py

[buildozer]
# Log level
log_level = 2

# Build directory
build_dir = ./.buildozer

# Bin directory  
bin_dir = ./bin

# Android SDK/NDK paths (otomatis di-download)
# android.sdk_path = 
# android.ndk_path =
```

### Struktur Project untuk Android

Perlu refactor sedikit agar Django bisa jalan di Android:

#### 1. Buat `main.py` sebagai entry point
```python
# main.py
import os
import sys
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcore.settings')

import django
django.setup()

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.webview import WebView
from kivy.clock import Clock
from android.runnable import run_on_ui_thread
from jnius import autoclass

# Import Django server
from django.core.management import execute_from_command_line
import threading

# Import Modbus service
from project.modbus_service import modbus_service
from project.models import ModbusConfig


class MowilexApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.django_thread = None
        self.django_port = 8000
        
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        # Label status
        self.status_label = Label(
            text='Starting Mowilex App...', 
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.status_label)
        
        # Start Django server
        self.start_django_server()
        
        # WebView untuk tampilkan Django
        Clock.schedule_once(self.load_webview, 2)
        
        return layout
    
    def start_django_server(self):
        """Start Django development server"""
        def run_server():
            try:
                execute_from_command_line([
                    'manage.py', 
                    'runserver', 
                    f'0.0.0.0:{self.django_port}',
                    '--noreload'
                ])
            except Exception as e:
                print(f"Django server error: {e}")
        
        self.django_thread = threading.Thread(target=run_server, daemon=True)
        self.django_thread.start()
        
        # Auto-start Modbus if enabled
        self.start_modbus_if_enabled()
    
    def start_modbus_if_enabled(self):
        """Start Modbus server jika auto_start=True"""
        def check_and_start():
            import time
            time.sleep(3)  # Wait for Django to be ready
            
            try:
                config = ModbusConfig.get_config()
                if config.auto_start:
                    result = modbus_service.start(
                        config.android_ip, 
                        config.android_port
                    )
                    if result['success']:
                        self.status_label.text = f"Modbus: {result['message']}"
            except Exception as e:
                print(f"Modbus auto-start error: {e}")
        
        threading.Thread(target=check_and_start, daemon=True).start()
    
    def load_webview(self, dt):
        """Load Django web interface in WebView"""
        try:
            from android.webview import WebView
            webview = WebView()
            webview.load_url(f'http://localhost:{self.django_port}')
            self.root.add_widget(webview)
            self.status_label.text = 'Mowilex Ready!'
        except Exception as e:
            self.status_label.text = f'Error: {e}'
    
    def on_stop(self):
        """Cleanup saat app ditutup"""
        # Stop Modbus server
        modbus_service.stop()


if __name__ == '__main__':
    MowilexApp().run()
```

#### 2. Buat Service untuk Modbus Background
```python
# service/modbus_service.py
import os
import sys
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcore.settings')

import django
django.setup()

from project.modbus_service import modbus_service
from project.models import ModbusConfig
import time

if __name__ == '__main__':
    # Start Modbus service
    config = ModbusConfig.get_config()
    
    result = modbus_service.start(config.android_ip, config.android_port)
    print(f"Modbus Service: {result['message']}")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        modbus_service.stop()
```

#### 3. Update Django Settings untuk Android
```python
# xcore/settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Detect if running on Android
IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_ROOT' in os.environ

# Debug mode
DEBUG = True  # Set False untuk production

# Allowed hosts
ALLOWED_HOSTS = ['*']  # Untuk development, production harus spesifik

# Database - SQLite (Android safe)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
if IS_ANDROID:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Logging untuk Android
if IS_ANDROID:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'mowilex.log'),
            },
        },
        'root': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    }
```

### Build APK

```bash
# Debug build (untuk testing)
buildozer android debug

# Release build (untuk production)
buildozer android release

# APK akan ada di: bin/mowilexplc-1.0.0-debug.apk
```

### Install di Android
```bash
# Via USB debugging
adb install -r bin/mowilexplc-1.0.0-debug.apk

# Atau copy file APK ke HP dan install manual
```

## 🎯 Alternatif: Pakai Termux (Lebih Mudah untuk Testing)

Jika build APK terlalu ribet, bisa pakai Termux dulu:

### 1. Install Termux
Download dari F-Droid: https://f-droid.org/en/packages/com.termux/

### 2. Setup di Termux
```bash
# Update packages
pkg update && pkg upgrade

# Install Python & dependencies
pkg install python git

# Clone project
cd ~
git clone <your-repo-url> mowilex999
cd mowilex999

# Install requirements
pip install -r requirements.txt

# Migrate database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 3. Run App
```bash
# Terminal 1: Django
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Modbus (pakai tmux)
tmux new -s modbus
python -c "from project.modbus_service import modbus_service; from project.models import ModbusConfig; config = ModbusConfig.get_config(); modbus_service.start(config.android_ip, config.android_port); import time; time.sleep(999999)"

# Detach dari tmux: Ctrl+B, lalu D
```

### 4. Akses via Browser
Buka browser di Android, akses: `http://localhost:8000`

### 5. Auto-start on Boot
```bash
# Buat script
nano ~/start_mowilex.sh
```

```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/mowilex999

# Start Django
python manage.py runserver 0.0.0.0:8000 &

# Start Modbus
python -c "from project.modbus_service import modbus_service; from project.models import ModbusConfig; config = ModbusConfig.get_config(); modbus_service.start(config.android_ip, config.android_port); import time; time.sleep(999999)" &

echo "Mowilex started!"
```

```bash
chmod +x ~/start_mowilex.sh

# Setup Termux boot
pkg install termux-services
mkdir -p ~/.termux/boot
nano ~/.termux/boot/start-mowilex
```

```bash
#!/data/data/com.termux/files/usr/bin/bash
~/start_mowilex.sh
```

```bash
chmod +x ~/.termux/boot/start-mowilex
```

## 📊 Kesimpulan

**Untuk Development/Testing:**
- ✅ Pakai **Termux** (paling mudah)
- Port Modbus: **9502** (atau ≥1024)

**Untuk Production/Distribusi:**
- ✅ Build **APK dengan Buildozer**
- Atau deploy ke **server** dan Android cuma akses web

**Network Configuration:**
- Android IP: `0.0.0.0` (listen all interfaces)
- Android Port: `9502` (Modbus server)
- PLC IP: Sesuai IP PLC Anda
- PLC Port: `502` (standar Modbus)

## 🔧 Akses Settings

Setelah install & running, akses:
- Web UI: `http://localhost:8000`
- Modbus Settings: `http://localhost:8000/modbus/settings/`
- Atur IP & Port sesuai kebutuhan
