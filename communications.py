#!/usr/bin/env python3

"""
Modbus/TCP server dengan integrasi Django
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Sinkronisasi data antara Modbus registers dan database Django.
- Alamat 0-10: Database → Modbus (update register dari database)
- Alamat 11-20: Modbus → Database (update database dari register)
- Dilengkapi antarmuka perintah interaktif.
"""

import argparse
import logging
import threading
import time
import os
import sys

# Setup Django
import django
from django.utils import timezone

# Konfigurasi environment Django
top_dir = os.path.expanduser('~/mowilex')  # Sesuaikan path
sys.path.append(top_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcore.settings')
django.setup()

from pyModbusTCP.server import DataBank, ModbusServer
from project.models import ValveSet  # Sesuaikan dengan model Anda

# Daftar IP yang diizinkan (opsional)
ALLOW_R_L = ['127.0.0.1', '172.17.164.24', '172.17.164.39']
ALLOW_W_L = ['127.0.0.1', '172.17.164.24', '172.17.164.39']


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
                                logging.info(f"Sync on read: Valve {addr} diupdate ke {value}")
                        except Exception as e:
                            logging.error(f"Gagal sync read Valve {addr}: {e}", exc_info=True)

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
                        logging.info(f"Register {addr} diubah {old_value}→{value} oleh {srv_info.client.address}")

                        # Sinkronisasi 0-10: Database → Modbus
                        if 0 <= addr <= 10:
                            try:
                                ValveSet.objects.filter(valve_number=addr).update(
                                    status=value,
                                    updated_at=timezone.now()
                                )
                                logging.info(f"Database updated: Valve {addr} = {value}")
                            except Exception as e:
                                logging.error(f"Gagal update database Valve {addr}: {e}", exc_info=True)
                else:
                    super().set_holding_registers(addr, [value], srv_info)

    def sync_valves(self):
        """Thread untuk sinkronisasi periodik"""
        while True:
            try:
                time.sleep(1)
                with self._lock:
                    # Sinkronisasi 0-10: Database → Modbus
                    for addr in range(0, 11):
                        try:
                            valve = ValveSet.objects.filter(valve_number=addr).first()
                            if valve and self._virtual_holding_registers[addr] != valve.status:
                                self._virtual_holding_registers[addr] = valve.status
                                logging.info(f"Sync DB→Modbus: Valve {addr} = {valve.status}")
                        except Exception as e:
                            logging.error(f"Gagal sync DB→Modbus {addr}: {e}", exc_info=True)

                    # Sinkronisasi 11-20: Modbus → Database
                    for addr in range(11, 21):
                        try:
                            current_value = self._virtual_holding_registers[addr]
                            valve, _ = ValveSet.objects.get_or_create(valve_number=addr)
                            if valve.status != current_value:
                                valve.status = current_value
                                valve.updated_at = timezone.now()
                                valve.save(update_fields=["status", "updated_at"])
                                logging.info(f"Sync Modbus→DB: Valve {addr} = {current_value}")
                        except Exception as e:
                            logging.error(f"Gagal sync Modbus→DB {addr}: {e}", exc_info=True)
            except Exception as e:
                logging.error(f"Error sinkronisasi: {e}", exc_info=True)
                time.sleep(5)


def command_interface(data_bank):
    """Antarmuka perintah interaktif"""
    print("Modbus Server Command Interface")
    print("Perintah: help, set <addr> <val>, get <addr>, exit")
    while True:
        try:
            cmd = input(">> ").strip().lower()
            if cmd == "help":
                print("set <addr> <val> - Ubah nilai register")
                print("get <addr>       - Baca nilai register")
                print("exit             - Keluar")
            elif cmd.startswith("set "):
                _, addr, val = cmd.split()
                addr = int(addr)
                val = int(val)
                data_bank.set_holding_registers(addr, [val])
                print(f"Register {addr} diatur ke {val}")
            elif cmd.startswith("get "):
                _, addr = cmd.split()
                addr = int(addr)
                val = data_bank.get_holding_registers(addr)[0]
                print(f"Register {addr} = {val}")
            elif cmd == "exit":
                break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int, default=1502)
    args = parser.parse_args()

    data_bank = SendReceiveDataBank()
    server = ModbusServer(
        host=args.host,
        port=args.port,
        data_bank=data_bank,
        no_block=True
    )

    logging.info("Starting Modbus server...")
    server.start()

    sync_thread = threading.Thread(target=data_bank.sync_valves, daemon=True)
    sync_thread.start()

    cmd_thread = threading.Thread(target=command_interface, args=(data_bank,), daemon=True)
    cmd_thread.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
    finally:
        server.stop()