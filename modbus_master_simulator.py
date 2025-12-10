#!/usr/bin/env python3
"""
Modbus Master Simulator untuk Testing
Simulasi PLC yang connect ke Android Modbus Server
"""

import time
import random
from pyModbusTCP.client import ModbusClient

# Konfigurasi koneksi ke Android/Server
ANDROID_IP = '127.0.0.1'  # Ganti dengan IP Android jika beda device
ANDROID_PORT = 9502        # Port yang Android listen

# Inisialisasi Modbus Client (PLC simulator)
client = ModbusClient(
    host=ANDROID_IP,
    port=ANDROID_PORT,
    auto_open=True,
    auto_close=False,
    timeout=5.0
)

def test_connection():
    """Test koneksi ke Modbus server"""
    print(f"🔌 Testing connection to {ANDROID_IP}:{ANDROID_PORT}...")
    
    if client.open():
        print("✅ Connected to Modbus Server!")
        return True
    else:
        print("❌ Failed to connect to Modbus Server!")
        print("   Make sure:")
        print("   1. Modbus server is running")
        print("   2. IP and Port are correct")
        print("   3. Firewall is not blocking the port")
        return False

def read_registers(start_addr, count):
    """Baca holding registers"""
    print(f"\n📖 Reading registers {start_addr} to {start_addr + count - 1}...")
    
    regs = client.read_holding_registers(start_addr, count)
    
    if regs:
        for i, value in enumerate(regs):
            addr = start_addr + i
            print(f"   Register {addr}: {value}")
        return regs
    else:
        print("   ❌ Failed to read registers")
        return None

def write_register(addr, value):
    """Tulis single holding register"""
    print(f"\n✍️  Writing register {addr} = {value}...")
    
    try:
        result = client.write_single_register(addr, value)
        if result:
            print(f"   ✅ Successfully wrote {value} to register {addr}")
            return True
        else:
            print(f"   ❌ Failed to write to register {addr}")
            print(f"   Debug: write_single_register returned {result}")
            print(f"   Last error: {client.last_error}")
            return False
    except Exception as e:
        print(f"   ❌ Exception during write: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_valve_control():
    """
    Simulasi PLC mengontrol valve
    - Register 0-10: PLC kirim command ke Android
    - Register 11-20: PLC baca status dari Android
    """
    print("\n" + "="*60)
    print("🏭 SIMULASI PLC - VALVE CONTROL")
    print("="*60)
    
    # Simulasi: PLC minta buka valve 3
    print("\n[SCENARIO 1] PLC minta buka Valve 3")
    print("-" * 40)
    
    # Write command ke register 3 (value 1 = OPEN)
    if write_register(3, 1):
        print("   ⏳ Tunggu Android proses command...")
        time.sleep(3)  # Tunggu sync database dan update register 14
        
        # Baca status dari register 14 (valve 3 status = 3+11)
        print("\n📖 PLC cek status Valve 3 dari register 14...")
        regs = read_registers(14, 1)
        
        if regs:
            status = "OPEN" if regs[0] == 1 else "CLOSED"
            print(f"   Status Valve 3: {status} (value={regs[0]})")
    
    time.sleep(2)
    
    # Simulasi: PLC minta tutup valve 3
    print("\n[SCENARIO 2] PLC minta tutup Valve 3")
    print("-" * 40)
    
    if write_register(3, 0):
        print("   ⏳ Tunggu Android proses command...")
        time.sleep(3)  # Tunggu sync
        
        regs = read_registers(14, 1)
        if regs:
            status = "OPEN" if regs[0] == 1 else "CLOSED"
            print(f"   Status Valve 3: {status} (value={regs[0]})")

def simulate_continuous_monitoring():
    """
    Simulasi PLC monitoring valve secara kontinyu
    PLC polling register setiap 2 detik
    """
    print("\n" + "="*60)
    print("📊 SIMULASI PLC - CONTINUOUS MONITORING")
    print("="*60)
    print("Press Ctrl+C to stop...\n")
    
    try:
        cycle = 1
        while True:
            print(f"\n[Cycle {cycle}] Polling registers...")
            
            # Baca register 11-15 (status valve dari Android)
            regs = read_registers(11, 5)
            
            if regs:
                print("\n   Valve Status:")
                for i, value in enumerate(regs):
                    valve_num = 11 + i
                    status = "🟢 OPEN" if value == 1 else "🔴 CLOSED"
                    print(f"   - Valve {valve_num}: {status} (value={value})")
            
            # Random command: kadang PLC kirim command
            if random.random() > 0.7:
                rand_valve = random.randint(0, 5)
                rand_value = random.randint(0, 1)
                print(f"\n   🎲 Random command: Set Valve {rand_valve} = {rand_value}")
                write_register(rand_valve, rand_value)
            
            cycle += 1
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")

def interactive_mode():
    """Mode interaktif untuk testing manual"""
    print("\n" + "="*60)
    print("🖥️  INTERACTIVE MODE - Modbus Master Simulator")
    print("="*60)
    print("\nCommands:")
    print("  read <addr> [count]  - Read registers")
    print("  write <addr> <value> - Write single register")
    print("  valve                - Simulate valve control")
    print("  monitor              - Continuous monitoring")
    print("  exit                 - Exit program")
    print()
    
    while True:
        try:
            cmd = input("PLC> ").strip().lower()
            
            if cmd == "exit":
                break
                
            elif cmd.startswith("read"):
                parts = cmd.split()
                if len(parts) >= 2:
                    addr = int(parts[1])
                    count = int(parts[2]) if len(parts) > 2 else 1
                    read_registers(addr, count)
                else:
                    print("Usage: read <addr> [count]")
                    
            elif cmd.startswith("write"):
                parts = cmd.split()
                if len(parts) == 3:
                    addr = int(parts[1])
                    value = int(parts[2])
                    write_register(addr, value)
                else:
                    print("Usage: write <addr> <value>")
                    
            elif cmd == "valve":
                simulate_valve_control()
                
            elif cmd == "monitor":
                simulate_continuous_monitoring()
                
            elif cmd == "help":
                print("\nCommands:")
                print("  read <addr> [count]  - Read registers")
                print("  write <addr> <value> - Write single register")
                print("  valve                - Simulate valve control")
                print("  monitor              - Continuous monitoring")
                print("  exit                 - Exit program")
                
            else:
                print("Unknown command. Type 'help' for commands.")
                
        except ValueError as e:
            print(f"Error: Invalid input - {e}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function"""
    print("="*60)
    print("🤖 MODBUS MASTER SIMULATOR (PLC)")
    print("="*60)
    print(f"Target Server: {ANDROID_IP}:{ANDROID_PORT}")
    print()
    
    # Test connection
    if not test_connection():
        print("\n⚠️  Cannot connect to Modbus server. Exiting...")
        return
    
    # Menu
    print("\n" + "="*60)
    print("SELECT MODE:")
    print("="*60)
    print("1. Valve Control Simulation")
    print("2. Continuous Monitoring")
    print("3. Interactive Mode")
    print("4. Exit")
    print()
    
    try:
        choice = input("Select mode (1-4): ").strip()
        
        if choice == "1":
            simulate_valve_control()
        elif choice == "2":
            simulate_continuous_monitoring()
        elif choice == "3":
            interactive_mode()
        elif choice == "4":
            print("👋 Goodbye!")
            return
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    finally:
        client.close()
        print("\n🔌 Disconnected from Modbus server")

if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        # Test connection
        print("="*60)
        print("🤖 MODBUS MASTER SIMULATOR (PLC)")
        print("="*60)
        print(f"Target Server: {ANDROID_IP}:{ANDROID_PORT}")
        print()
        
        if not test_connection():
            print("\n⚠️  Cannot connect to Modbus server. Exiting...")
            sys.exit(1)
        
        try:
            if mode == '--valve-control':
                simulate_valve_control()
            elif mode == '--monitor':
                simulate_continuous_monitoring()
            elif mode == '--interactive':
                interactive_mode()
            else:
                print(f"Unknown mode: {mode}")
                print("Usage: python modbus_master_simulator.py [--valve-control|--monitor|--interactive]")
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
        finally:
            client.close()
            print("\n🔌 Disconnected from Modbus server")
    else:
        main()
