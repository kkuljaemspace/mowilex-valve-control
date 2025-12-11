"""
Modbus Service Manager untuk Django
Mengelola Modbus TCP Server yang terintegrasi dengan database
"""

import threading
import logging
import os
import sys
from pathlib import Path

# Setup Django path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcore.settings')

import django
django.setup()

from django.utils import timezone
from pyModbusTCP.server import DataBank, ModbusServer
from project.models import ValveSet

logger = logging.getLogger(__name__)


class SendReceiveDataBank(DataBank):
    """Kelas DataBank dengan integrasi Django"""

    def __init__(self):
        super().__init__()
        # Inisialisasi register virtual dengan nilai default
        self._virtual_holding_registers = {i: 2 for i in range(21)}
        self._lock = threading.Lock()

    def get_holding_registers(self, address, number=1, srv_info=None):
        """Handle read registers dengan sinkronisasi database"""
        with self._lock:
            regs = []
            for addr in range(address, address + number):
                if addr in self._virtual_holding_registers:
                    value = self._virtual_holding_registers[addr]

                    # Sinkronisasi 11-20: Modbus → Database saat read
                    if 11 <= addr <= 20:
                        try:
                            valve, _ = ValveSet.objects.get_or_create(valve_number=addr)
                            if valve.status != value:
                                valve.status = value
                                valve.updated_at = timezone.now()
                                valve.save(update_fields=["status", "updated_at"])
                                logger.info(f"Sync on read: Valve {addr} diupdate ke {value}")
                        except Exception as e:
                            logger.error(f"Gagal sync read Valve {addr}: {e}", exc_info=True)

                    regs.append(value)
                else:
                    regs.append(super().get_holding_registers(addr, 1, srv_info)[0])
            return regs

    def set_holding_registers(self, address, values, srv_info=None):
        """Handle write registers dengan update database"""
        with self._lock:
            for i, value in enumerate(values):
                addr = address + i
                if addr in self._virtual_holding_registers:
                    old_value = self._virtual_holding_registers[addr]

                    # Update register hanya jika nilai berubah
                    if old_value != value:
                        self._virtual_holding_registers[addr] = value
                        
                        # Log dengan info client jika ada
                        client_info = srv_info.client.address if srv_info and hasattr(srv_info, 'client') else "internal"
                        logger.info(f"Register {addr} diubah {old_value}→{value} oleh {client_info}")

                        # Sinkronisasi 0-10: Command register → Database → Status register
                        if 0 <= addr <= 10:
                            try:
                                # Update database
                                ValveSet.objects.filter(valve_number=addr).update(
                                    status=value,
                                    updated_at=timezone.now()
                                )
                                logger.info(f"Database updated: Valve {addr} = {value}")
                                
                                # Mirror ke status register (addr+11)
                                status_addr = addr + 11
                                if status_addr in self._virtual_holding_registers:
                                    self._virtual_holding_registers[status_addr] = value
                                    logger.info(f"Status register {status_addr} updated = {value}")
                                    
                            except Exception as e:
                                logger.error(f"Gagal update database Valve {addr}: {e}", exc_info=True)
                else:
                    super().set_holding_registers(addr, [value], srv_info)
            
            # Return True untuk konfirmasi sukses
            return True

    def sync_valves(self):
        """Thread untuk sinkronisasi periodik"""
        while True:
            try:
                import time
                time.sleep(1)
                with self._lock:
                    # Sinkronisasi 0-10: Database → Modbus
                    for addr in range(0, 11):
                        try:
                            valve = ValveSet.objects.filter(valve_number=addr).first()
                            if valve and self._virtual_holding_registers[addr] != valve.status:
                                self._virtual_holding_registers[addr] = valve.status
                                logger.info(f"Sync DB→Modbus: Valve {addr} = {valve.status}")
                        except Exception as e:
                            logger.error(f"Gagal sync DB→Modbus {addr}: {e}", exc_info=True)

                    # Sinkronisasi 11-20: Modbus → Database
                    for addr in range(11, 21):
                        try:
                            current_value = self._virtual_holding_registers[addr]
                            valve, _ = ValveSet.objects.get_or_create(valve_number=addr)
                            if valve.status != current_value:
                                valve.status = current_value
                                valve.updated_at = timezone.now()
                                valve.save(update_fields=["status", "updated_at"])
                                logger.info(f"Sync Modbus→DB: Valve {addr} = {current_value}")
                        except Exception as e:
                            logger.error(f"Gagal sync Modbus→DB {addr}: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"Error sinkronisasi: {e}", exc_info=True)
                import time
                time.sleep(5)


class ModbusService:
    """Singleton service untuk mengelola Modbus server"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.server = None
            self.data_bank = None
            self.sync_thread = None
            self.host = None
            self.port = None
            self.initialized = True
    
    def start(self, host='0.0.0.0', port=9502):
        """
        Start Modbus server
        
        Args:
            host: IP address untuk bind server (0.0.0.0 = semua interface)
            port: Port number (recommend 9502+ untuk Android)
        """
        if self.server is not None:
            logger.warning("Modbus server already running")
            return {'success': False, 'message': 'Server sudah berjalan'}
        
        # Validasi port
        if port < 1024:
            return {
                'success': False, 
                'message': f'Port {port} adalah privileged port. Di Android gunakan port ≥1024 (recommend: 9502)'
            }
        
        try:
            self.data_bank = SendReceiveDataBank()
            self.server = ModbusServer(
                host=host,
                port=port,
                data_bank=self.data_bank,
                no_block=True  # Must be True for background operation
            )
            
            # Start Modbus server
            self.server.start()
            
            logger.info(f"✅ Modbus server started on {host}:{port}")
            
            # Start sync thread
            self.sync_thread = threading.Thread(
                target=self.data_bank.sync_valves, 
                daemon=True,
                name="ModbusSyncThread"
            )
            self.sync_thread.start()
            
            self.host = host
            self.port = port
            
            return {
                'success': True, 
                'message': f'Modbus server berhasil dijalankan di {host}:{port}'
            }
            
        except Exception as e:
            logger.error(f"Failed to start Modbus server: {e}", exc_info=True)
            return {
                'success': False, 
                'message': f'Gagal start server: {str(e)}'
            }
    
    def stop(self):
        """Stop Modbus server"""
        if self.server is None:
            return {'success': False, 'message': 'Server tidak berjalan'}
        
        try:
            self.server.stop()
            self.server = None
            self.data_bank = None
            self.sync_thread = None
            self.host = None
            self.port = None
            
            logger.info("✅ Modbus server stopped")
            return {'success': True, 'message': 'Modbus server berhasil dihentikan'}
            
        except Exception as e:
            logger.error(f"Failed to stop Modbus server: {e}", exc_info=True)
            return {'success': False, 'message': f'Gagal stop server: {str(e)}'}
    
    def restart(self, host=None, port=None):
        """Restart server dengan konfigurasi baru"""
        # Stop dulu
        self.stop()
        
        # Start dengan konfigurasi baru
        import time
        time.sleep(1)  # Delay sebentar
        
        if host is None:
            host = self.host or '0.0.0.0'
        if port is None:
            port = self.port or 9502
            
        return self.start(host, port)
    
    def get_status(self):
        """Get status server"""
        is_running = self.server is not None
        return {
            'is_running': is_running,  # Key yang dipakai widget
            'running': is_running,      # Backward compatibility
            'host': self.host or '0.0.0.0',
            'port': self.port or 9502,
            'timestamp': timezone.now().isoformat()
        }
    
    def is_running(self):
        """Check if server is running"""
        return self.server is not None


# Global singleton instance
modbus_service = ModbusService()
