# Mowilex Project - Struktur & Dokumentasi

## 📁 Struktur Project

```
mowilex999/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── db.sqlite3                  # Database SQLite
├── docker-compose.yml          # Docker configuration (belum digunakan)
│
├── xcore/                      # Django project core
│   ├── settings.py             # Konfigurasi utama Django
│   ├── urls.py                 # URL routing utama
│   ├── wsgi.py                 # WSGI application
│   └── asgi.py                 # ASGI application
│
├── otentifikasi/               # App untuk autentikasi & user management
│   ├── models.py               # Profile, AppIdentity, Menu, Submenu
│   ├── views.py                # Login, logout, profile, user management
│   ├── forms.py                # Form untuk user & app identity
│   ├── decorators.py           # Custom decorators untuk akses control
│   ├── context_processors.py  # Context processor untuk menu & identity
│   └── templatetags/           # Custom template filters
│
├── project/                    # App utama untuk business logic
│   ├── models.py               # VendorURL, ItemMap, ScanTable, EpicorPO, 
│   │                           # ValveOperation, MappingValve, ValveSet
│   ├── views.py                # Menu, scan, inquiry, valve operations, PO
│   ├── urls.py                 # URL routing untuk project
│   └── admin.py                # Django admin configuration
│
├── templates/                  # Template HTML
│   ├── base.html               # Base template dengan navbar & menu
│   ├── base-dashboard.html     # Alternative base template
│   ├── otentifikasi/           # Templates untuk login, profile, user mgmt
│   └── project/                # Templates untuk menu, scan, inquiry, dll
│
├── static/                     # Static files (CSS, JS, images)
│   └── assets/                 # Template assets
│
├── staticfiles/                # Collected static files (production)
│
├── media/                      # Upload files
│   ├── logo/                   # App logos
│   └── profile_photos/         # User profile photos
│
├── communications.py           # Modbus/TCP server dengan integrasi Django
│                               # (sync data antara Modbus & database)
│
├── integrasi_oracle.py         # Script untuk integrasi dengan Epicor API
│                               # (get PO data dari live system)
│
└── _archived_files/            # File-file lama yang sudah tidak digunakan
    ├── old_scripts/            # Script Modbus/PLC lama
    ├── exSiemensProfinet/      # Kode lama Siemens PLC
    └── README.md               # Dokumentasi file arsip
```

## 🔧 Komponen Utama

### 1. Django Apps

#### **otentifikasi**
- Autentikasi user (login/logout)
- User management (CRUD users)
- Group & permission management
- Menu & submenu management dengan access control
- App identity & branding

#### **project**
- Menu utama aplikasi
- Scan RFID tag
- Inquiry & PO management
- Valve operations (buka/tutup valve)
- Integrasi dengan Epicor API

### 2. Integration Scripts

#### **communications.py**
- Modbus/TCP server
- Sinkronisasi data antara Modbus registers dan Django database
- Support untuk valve control system
- Logging & monitoring

#### **integrasi_oracle.py**
- API client untuk Epicor system
- Get PO Check detail & summary
- Basic authentication dengan API key

### 3. Database Models

**otentifikasi app:**
- Profile (extends Django User)
- AppIdentity (branding)
- Menu & Submenu (dynamic menu system)

**project app:**
- VendorURL (vendor configuration)
- ItemMap (item mapping)
- ScanTable (RFID scan records)
- EpicorPO (PO data from Epicor)
- MappingValve (valve mapping)
- ValveOperation (valve operation logs)
- ValveSet (valve settings)

## 🚀 Setup & Running

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Django Server
```bash
python manage.py runserver
```

### Run Modbus Server (optional)
```bash
python communications.py -H 192.168.2.99 -p 1502
```

### Database Migration
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

## 📦 Dependencies

- Django 6.0
- django-import-export
- django-crispy-forms & crispy-bootstrap5
- django-select2
- django-pwa
- pyModbusTCP (untuk Modbus communication)
- cx-Oracle (untuk Oracle database - optional)
- python-dateutil

## 🔐 Security Notes

- Secret key disimpan di settings.py (production harus menggunakan environment variable)
- DEBUG mode aktif (production harus False)
- ALLOWED_HOSTS = ['*'] (production harus specific)
- API credentials di integrasi_oracle.py (sebaiknya gunakan environment variable)

## 📝 TODO / Future Improvements

1. Pindahkan sensitive data ke environment variables
2. Setup proper logging system
3. Implementasi Docker deployment
4. Add automated tests
5. Setup CI/CD pipeline
6. Improve error handling & validation
7. Add API documentation
8. Implement real-time updates menggunakan WebSocket/SSE

## 🗑️ Cleanup

File-file yang sudah tidak digunakan telah dipindahkan ke folder `_archived_files/`
Lihat `_archived_files/README.md` untuk detail.
