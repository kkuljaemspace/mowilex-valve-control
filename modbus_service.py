#!/usr/bin/env python
"""
Modbus Service untuk Android Background Service
Service ini akan jalan terus di background bahkan ketika app minimize
"""
import os
import sys
import django
from pathlib import Path

# Setup path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcore.settings')
django.setup()

# Import after Django setup
from project.modbus_service import ModbusService
from project.models import ModbusConfig
import time
from android import AndroidService
from jnius import autoclass

# Android services
PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)

def start_service():
    """Start Modbus service"""
    print("📱 Android Background Service - Modbus Server")
    
    service = ModbusService()
    
    # Load config dari database
    try:
        config = ModbusConfig.objects.first()
        if config:
            host = config.android_ip or '0.0.0.0'
            port = config.android_port or 9502
            print(f"Config loaded: {host}:{port}")
        else:
            host = '0.0.0.0'
            port = 9502
            print("Using default config: 0.0.0.0:9502")
    except Exception as e:
        print(f"Config load error: {e}")
        host = '0.0.0.0'
        port = 9502
    
    # Start server
    result = service.start(host, port)
    print(f"Server start result: {result}")
    
    # Keep service alive
    while True:
        time.sleep(10)
        # Health check
        if service.server is None:
            print("⚠️ Server stopped, restarting...")
            service.start(host, port)

if __name__ == '__main__':
    start_service()
