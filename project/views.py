import logging
import threading
import time
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from requests.auth import HTTPBasicAuth
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.dateparse import parse_date

# Import model yang diperlukan
from .models import EpicorPO, ValveOperation, MappingValve, ValveSet, ModbusConfig

# ===============================
# Konfigurasi API Live
# ===============================
LIVE_USERNAME = "dkp.rfid"
LIVE_PASSWORD = "KPX_Y0A@mwl25"
LIVE_API_KEY = "zeOCUvyYrMSn2WrRFhnoFPbCTDldqej3AullXpQdfwQju"
LIVE_BASE_URL = "https://mowilex-live.epicorsaas.com/server/api/v2/odata/mwl/BaqSvc"


def get_po_check_live(ponum: int):
    """
    Mengambil detail PO Check dari live API.
    """
    url = f"{LIVE_BASE_URL}/MWL_POCheck/Data?PONum={ponum}"
    headers = {
        "X-Api-Key": LIVE_API_KEY
    }
    response = requests.get(url, auth=HTTPBasicAuth(LIVE_USERNAME, LIVE_PASSWORD), headers=headers)
    response.raise_for_status()
    return response.json()


def get_po_check_summary_live(ponum: int):
    """
    Mengambil summary PO Check dari live API.
    """
    url = f"{LIVE_BASE_URL}/MWL_POCheckSummary/Data?PONum={ponum}"
    headers = {
        "X-Api-Key": LIVE_API_KEY
    }
    response = requests.get(url, auth=HTTPBasicAuth(LIVE_USERNAME, LIVE_PASSWORD), headers=headers)
    response.raise_for_status()
    return response.json()


# ===============================
# View Aplikasi
# ===============================
@login_required
def menu(request):
    return render(request, "project/menu.html")


@login_required
def scan(request):
    if request.method == 'POST':
        scan_value = request.POST.get('scan_value')
        if not scan_value:
            return render(request, 'project/scan.html', {
                'error': 'Scan Value tidak boleh kosong.'
            })
        try:
            # Pastikan nilai PO berbentuk integer
            po_number = int(scan_value)
            # Panggil API untuk validasi PO
            data = get_po_check_live(po_number)
            if not data.get("value"):
                return render(request, 'project/scan.html', {
                    'error': 'PO tidak ditemukan.'
                })
            # Jika valid, redirect ke halaman detail PO
            return redirect('po_detail', ponum=po_number)
        except ValueError:
            return render(request, 'project/scan.html', {
                'error': 'Scan Value harus berupa angka.'
            })
        except requests.exceptions.RequestException as e:
            return render(request, 'project/scan.html', {
                'error': f"Terjadi kesalahan koneksi: {e}"
            })
    return render(request, "project/scan.html")


@login_required
def po_detail(request, ponum):
    try:
        # Pastikan ponum merupakan integer
        po_number = int(ponum)
        # Ambil data detail dan summary dari API
        detail_data = get_po_check_live(po_number)
        summary_data = get_po_check_summary_live(po_number)
        # Balik urutan data supaya data terbaru tampil di awal
        detail_data["value"] = detail_data["value"][::-1]
        summary_data["value"] = summary_data["value"][::-1]

        # Simpan atau update data ke model EpicorPO beserta user yang melakukan transaksi
        epicor = EpicorPO.objects.update_or_create(
            ponum=po_number,
            defaults={
                'detail_data': detail_data,
                'summary_data': summary_data,
                'user': request.user,  # Pastikan field user sudah ada pada model EpicorPO
            }
        )
        epicorstatus = epicor[0].status
        if request.POST.get('epicor_id'):
            epicor_delete = EpicorPO.objects.filter(ponum=request.POST.get('epicor_id'))
            epicor_delete.delete()
            try:
                valve_instance = MappingValve.objects.filter(part_number=request.POST.get('valve_instance')).last()
                valve_set = ValveSet.objects.filter(valve_number=valve_instance.valve_number).last()
                valve_set.status = 0
                valve_set.save()
            except:
                pass
            messages.info(request, f"PO number: {ponum} sudah dihapus dari proses")
            return redirect('/po-list/')
        return render(request, 'project/po_detail.html', {
            'ponum': po_number,
            'detail_data': detail_data,
            'summary_data': summary_data,
            'epicorstatus': epicorstatus,
        })
    except ValueError:
        return render(request, 'project/po_detail.html', {
            'ponum': ponum,
            'error': 'Nomor PO tidak valid.'
        })
    except requests.exceptions.RequestException as e:
        return render(request, 'project/po_detail.html', {
            'ponum': ponum,
            'error': f"Gagal memanggil API, kesalahan koneksi: {e}"
        })


@login_required
def inquiry(request):
    """
    Halaman inquiry dengan filter berdasarkan tanggal.
    Jika tidak ada parameter tanggal, tampilkan data hari ini saja.
    Menampilkan daftar Epicor PO dan Valve Operation beserta user yang melakukan transaksi.
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Jika tidak ada request tanggal, default ke tanggal hari ini
    if not (start_date and end_date):
        today = timezone.now().date()
        start_date = today
        end_date = today

    epicor_qs = EpicorPO.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    valve_qs = ValveOperation.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

    context = {
        'epicor_list': epicor_qs,
        'valve_list': valve_qs,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, "project/inquiry.html", context)

# ============================================
# View untuk mengirim pembukaan Valve
# ============================================
@login_required
def open_valve(request):
    """
    View Django untuk membuka valve.
    Diterima parameter GET:
      - valve: nilai input dari user (dari field valve_number)
      - valve_partnum: part number yang ditetapkan di halaman po-detail
    Hanya jika kedua parameter tersebut sama, perintah open valve akan dijalankan.
    """
    valve_str = request.GET.get("valve", "")
    valve_partnum = request.GET.get("valve_partnum", "")

    # Validasi: open valve hanya dijalankan jika valve_str sama dengan valve_partnum
    if valve_str != valve_partnum:
        return JsonResponse({
            "error": "Valve yang dimasukkan tidak sesuai dengan part number yang ditetapkan.",
            "valve": valve_str or "unknown",
            "response": 1
        })

    # Cari instance MappingValve berdasarkan valve_str (yang juga merupakan valve_partnum)
    valve_instance = MappingValve.objects.filter(part_number=valve_str).last()
    if not valve_instance:
        return JsonResponse({
            "error": "Valve PartNumber tidak valid.",
            "valve": valve_str or "unknown",
            "response": 1
        })

    # Mapping perintah: misal register yang digunakan sesuai dengan nomor valve
    command_register = valve_instance.valve_number
    nilai_perintah = 1  # 1 artinya perintah untuk membuka valve

    valve_set = ValveSet.objects.filter(valve_number=command_register).last()
    if not valve_set:
        return JsonResponse({
            "error": "Valve tidak valid.",
            "valve": valve_instance.valve_number,
            "response": 1
        })
    valve_set.status = nilai_perintah
    valve_set.save()

    # Tunggu beberapa detik agar PLC mengupdate status valve
    time.sleep(5)
    status_register = valve_set.valve_number + 10
    valve_set_status = ValveSet.objects.filter(valve_number=status_register).last()
    if not valve_set_status:
        return JsonResponse({
            "error": "Status Valve tidak ditemukan.",
            "valve": valve_instance.valve_number,
            "response": 1
        })
    nilai_status = valve_set_status.status

    # Interpretasi status
    if nilai_status == 0:
        status_text = "Open Valve"
        response_data = {
            "valve": valve_instance.valve_number,
            "response": 0,
            "status": status_text
        }
    elif nilai_status == 1:
        status_text = "Valve Penuh"
        response_data = {
            "valve": valve_instance.valve_number,
            "response": 1,
            "error": f"Valve penuh (nilai: {nilai_status}). Silahkan tunggu dan scan kembali.",
            "status": status_text
        }
    else:
        status_text = f"Tidak diketahui ({nilai_status})"
        response_data = {
            "valve": valve_instance.valve_number,
            "response": 1,
            "error": f"Status tidak diketahui, nilai: {nilai_status}",
            "status": status_text
        }

    # Simpan transaksi pembukaan valve ke model ValveOperation
    ValveOperation.objects.create(
        valve_number=valve_instance,
        command_value=nilai_perintah,
        status_value=nilai_status,
        status=status_text,
        user=request.user,
    )

    return JsonResponse(response_data)


def list_po(request):
    """
    Menampilkan daftar PO dengan status.
    Urutan: PO yang belum selesai (status selain 'Selesai') muncul terlebih dahulu.
    """
    epicor_pos = EpicorPO.objects.all()
    po_list = []
    for po in epicor_pos:
        po_list.append({
            "ponum": po.ponum,
            "created_at": po.created_at,
            "status": po.status,
        })
    # Urutkan: PO dengan status "Selesai" diurutkan paling bawah
    po_list = sorted(po_list, key=lambda x: 1 if x['status'] == "Selesai" else 0, reverse=False)
    context = {"po_list": po_list}
    return render(request, "project/list_po.html", context)


def mark_po_done(request, ponum, valve):
    """
    Menandai bahwa PO telah selesai (DONE).
    Mengirim nilai 0 ke register command untuk menutup valve.
    """
    try:
        po = EpicorPO.objects.get(ponum=ponum)
        po.status = "Selesai"
        po.save()
        
        # Kirim nilai 0 ke register command untuk menutup valve
        valve_set = ValveSet.objects.filter(valve_number=valve).first()
        if valve_set:
            valve_set.status = 0  # 0 = tutup valve
            valve_set.save()
            return JsonResponse({"status": "success", "message": "PO telah ditandai selesai dan valve ditutup."})
        else:
            return JsonResponse({"status": "success", "message": "PO telah ditandai selesai (valve tidak ditemukan)."})
    except EpicorPO.DoesNotExist:
        return JsonResponse({"status": "error", "message": "PO tidak ditemukan."})

def mark_po_pause(request, ponum, valve):
    """
    Menandai bahwa PO sedang dijeda (PAUSE).
    """
    try:
        po = EpicorPO.objects.get(ponum=ponum)
        po.status = "Pause"
        po.save()
        return JsonResponse({"status": "success", "message": "PO telah dijeda."})
    except EpicorPO.DoesNotExist:
        return JsonResponse({"status": "error", "message": "PO tidak ditemukan."})


def alarm(request):
    try:
        nilai_perintah = request.POST.get('value')
        valve_set = ValveSet.objects.filter(valve_number=0).last()
        valve_set.status = nilai_perintah
        valve_set.save()

        return JsonResponse({"status": "success", "message": "Alarm Sukses Dikirim."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": e})


# ===============================
# Modbus Service Management
# ===============================
from .modbus_service import modbus_service

@login_required
def modbus_settings(request):
    """Halaman settings Modbus"""
    config = ModbusConfig.get_config()
    status = modbus_service.get_status()
    
    if request.method == 'POST':
        # Update konfigurasi
        config.android_ip = request.POST.get('android_ip', '0.0.0.0')
        config.android_port = int(request.POST.get('android_port', 9502))
        config.plc_ip = request.POST.get('plc_ip', '192.168.2.99')
        config.plc_port = int(request.POST.get('plc_port', 502))
        config.auto_start = request.POST.get('auto_start') == 'on'
        config.updated_by = request.user
        
        # Validasi port Android
        if config.android_port < 1024:
            messages.warning(
                request, 
                f'⚠️ Port {config.android_port} adalah privileged port. '
                f'Di Android, port <1024 memerlukan root access. '
                f'Gunakan port ≥1024 (recommended: 9502)'
            )
        
        config.save()
        messages.success(request, '✅ Konfigurasi berhasil disimpan')
        
        # Restart server jika sedang berjalan
        if status['running']:
            result = modbus_service.restart(config.android_ip, config.android_port)
            if result['success']:
                messages.success(request, '✅ Modbus server direstart dengan konfigurasi baru')
            else:
                messages.error(request, f'❌ {result["message"]}')
        
        return redirect('modbus_settings')
    
    context = {
        'config': config,
        'status': status,
    }
    return render(request, 'project/modbus_settings.html', context)


@login_required
def modbus_start(request):
    """Start Modbus server"""
    config = ModbusConfig.get_config()
    result = modbus_service.start(config.android_ip, config.android_port)
    
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])
    
    return redirect('modbus_settings')


@login_required
def modbus_stop(request):
    """Stop Modbus server"""
    result = modbus_service.stop()
    
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])
    
    return redirect('modbus_settings')


@login_required
def modbus_restart(request):
    """Restart Modbus server"""
    config = ModbusConfig.get_config()
    result = modbus_service.restart(config.android_ip, config.android_port)
    
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])
    
    return redirect('modbus_settings')


def modbus_status_api(request):
    """API untuk cek status Modbus server"""
    status = modbus_service.get_status()
    return JsonResponse(status)
