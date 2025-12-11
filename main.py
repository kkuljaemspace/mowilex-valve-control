#!/usr/bin/env python
"""
Mowilex Valve Control - Android/Termux Entry Point
Main entry point untuk aplikasi Android dan Termux
"""
import os
import sys
import django
from pathlib import Path
import signal
import atexit

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

# Global service instance for cleanup
_modbus_service = None

def cleanup_handler(signum=None, frame=None):
    """Cleanup handler for graceful shutdown"""
    print("\n🛑 Shutting down gracefully...")
    global _modbus_service
    if _modbus_service:
        try:
            _modbus_service.stop()
            print("✅ Modbus server stopped")
        except:
            pass
    sys.exit(0)

# Register cleanup handlers
signal.signal(signal.SIGTERM, cleanup_handler)
signal.signal(signal.SIGINT, cleanup_handler)
atexit.register(lambda: cleanup_handler() if _modbus_service else None)

def start_modbus_server():
    """Start Modbus server in background thread"""
    global _modbus_service
    print("🔷 Starting Modbus Server...")
    _modbus_service = ModbusService()
    
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
    except Exception as e:
        print(f"⚠️  Config load failed: {e}")
        host = '0.0.0.0'
        port = 9502
    
    result = _modbus_service.start(host, port)
    if result['success']:
        print(f"✅ Modbus server started: {result['message']}")
    else:
        print(f"❌ Modbus server failed: {result['message']}")
    
    # Keep server running
    try:
        while True:
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Stopping Modbus server...")
        _modbus_service.stop()

def main():
    """Main entry point"""
    print("="*70)
    print("🚀 MOWILEX VALVE CONTROL SYSTEM")
    print("="*70)
    print(f"📅 Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Working Dir: {os.getcwd()}")
    print("="*70)
    print()
    
    # Run migrations first
    print("📦 Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations complete")
    except Exception as e:
        print(f"⚠️  Migration warning: {e}")
    
    print()
    
    # Start Modbus server in background
    modbus_thread = threading.Thread(
        target=start_modbus_server,
        daemon=True,
        name="ModbusServerThread"
    )
    modbus_thread.start()
    
    # Wait for server to initialize
    time.sleep(3)
    
    # Start Django development server
    print("\n📡 Services Status:")
    print("   ✅ Modbus TCP Server: 0.0.0.0:9502")
    print("   ✅ Django Web Server: http://0.0.0.0:8000")
    print("\n💡 Tips:")
    print("   - Access web UI: http://localhost:8000")
    print("   - PLC connects to: <android-ip>:9502")
    print("   - Press Ctrl+C to stop")
    print("="*70)
    print()
    
    # Run Django on port 8000 (disable auto-reload for stability)
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:8000', '--noreload']
    
    try:
        execute_from_command_line(sys.argv)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
