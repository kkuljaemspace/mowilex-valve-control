#!/usr/bin/env python
"""
Mowilex Valve Control - Android Entry Point
Main entry point untuk aplikasi Android
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcore.settings')

# Add project to path
sys.path.insert(0, str(BASE_DIR))

# Setup Django
django.setup()

# Import after Django setup
from django.core.management import execute_from_command_line
from project.modbus_service import ModbusService
import threading
import time

def start_modbus_server():
    """Start Modbus server in background thread"""
    print("🔷 Starting Modbus Server...")
    service = ModbusService()
    
    # Get config from database or use defaults
    try:
        from project.models import ModbusConfig
        config = ModbusConfig.objects.first()
        if config and config.auto_start:
            host = config.android_ip or '0.0.0.0'
            port = config.android_port or 9502
        else:
            host = '0.0.0.0'  # Listen on all interfaces
            port = 9502
    except:
        host = '0.0.0.0'
        port = 9502
    
    result = service.start(host, port)
    if result['success']:
        print(f"✅ Modbus server started: {result['message']}")
    else:
        print(f"❌ Modbus server failed: {result['message']}")
    
    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Modbus server...")
        service.stop()

def main():
    """Main entry point"""
    print("="*60)
    print("🚀 MOWILEX VALVE CONTROL SYSTEM")
    print("="*60)
    print()
    
    # Start Modbus server in background
    modbus_thread = threading.Thread(
        target=start_modbus_server,
        daemon=True,
        name="ModbusServerThread"
    )
    modbus_thread.start()
    
    # Wait for server to initialize
    time.sleep(2)
    
    # Start Django development server
    print("\n🌐 Starting Django web server...")
    print("="*60)
    
    # Run Django on port 8000
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:8000']
    
    try:
        execute_from_command_line(sys.argv)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)

if __name__ == '__main__':
    main()
