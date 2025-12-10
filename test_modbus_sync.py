#!/usr/bin/env python
"""
Test Modbus Communication
Jalankan server dan client sekaligus untuk test
"""
import time
import threading
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcore.settings')
django.setup()

from project.modbus_service import ModbusService
from pyModbusTCP.client import ModbusClient

def run_server():
    """Thread untuk server"""
    print("\n" + "="*60)
    print("🔷 STARTING MODBUS SERVER")
    print("="*60)
    
    try:
        service = ModbusService()
        result = service.start('127.0.0.1', 9502)
        
        print(f"\n[DEBUG] Start result: {result}")
        
        if result['success']:
            print(f"✅ {result['message']}\n")
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except:
                pass
        else:
            print(f"❌ {result['message']}")
    except Exception as e:
        print(f"❌ Server exception: {e}")
        import traceback
        traceback.print_exc()

def run_client():
    """Thread untuk client (PLC simulator)"""
    # Tunggu server ready
    print("\n⏳ Waiting for server to start...")
    time.sleep(5)
    
    print("\n" + "="*60)
    print("🔶 STARTING PLC CLIENT")
    print("="*60)
    
    client = ModbusClient(host='127.0.0.1', port=9502, auto_open=True)
    
    if not client.is_open:
        print("❌ Cannot connect to server")
        return
    
    print("✅ Connected to Modbus server\n")
    
    # Test 1: Write register 3 = 1
    print("[TEST 1] Write register 3 = 1 (OPEN)")
    print("-" * 40)
    result = client.write_single_register(3, 1)
    print(f"Write result: {result}")
    
    time.sleep(2)
    
    # Read register 13 (status)
    print("\nRead register 13 (status)...")
    value = client.read_holding_registers(13, 1)
    if value:
        status = "OPEN" if value[0] == 1 else "CLOSED"
        print(f"Register 13 = {value[0]} ({status})")
    
    time.sleep(2)
    
    # Test 2: Write register 3 = 0
    print("\n[TEST 2] Write register 3 = 0 (CLOSE)")
    print("-" * 40)
    result = client.write_single_register(3, 0)
    print(f"Write result: {result}")
    
    time.sleep(2)
    
    # Read register 13 again
    print("\nRead register 13 (status)...")
    value = client.read_holding_registers(13, 1)
    if value:
        status = "OPEN" if value[0] == 1 else "CLOSED"
        print(f"Register 13 = {value[0]} ({status})")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED")
    print("="*60)
    
    client.close()

if __name__ == '__main__':
    # Start server di thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Run client di main thread
    try:
        run_client()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    finally:
        # Give time for cleanup
        time.sleep(1)
        print("\n👋 Exiting...")
