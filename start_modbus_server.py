#!/usr/bin/env python
"""
Script untuk menjalankan Modbus Server standalone
Untuk testing dengan simulator
"""
import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcore.settings')
django.setup()

from project.modbus_service import ModbusService
import time

def main():
    print("=" * 60)
    print("🚀 MODBUS SERVER STARTER")
    print("=" * 60)
    
    service = ModbusService()
    result = service.start('127.0.0.1', 9502)
    
    if result['success']:
        print(f"✅ {result['message']}")
        print("\n⏳ Server running... Press Ctrl+C to stop\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping server...")
            service.stop()
            print("✅ Server stopped")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)

if __name__ == '__main__':
    main()
