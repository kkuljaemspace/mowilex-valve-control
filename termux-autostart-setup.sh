#!/data/data/com.termux/files/usr/bin/bash

echo "🔧 MOWILEX AUTO-START SETUP"
echo "================================"

# 1. Install Termux:Boot dari F-Droid
echo ""
echo "📱 LANGKAH 1: Install Termux:Boot"
echo "   Download dari: https://f-droid.org/en/packages/com.termux.boot/"
echo "   Atau install manual APK"
echo ""
echo "   ⚠️  HARUS dari F-Droid, bukan Play Store!"
echo ""
read -p "Sudah install Termux:Boot? (y/n): " installed

if [ "$installed" != "y" ]; then
    echo "❌ Install Termux:Boot dulu, lalu jalankan script ini lagi"
    exit 1
fi

# 2. Setup Termux permissions
echo ""
echo "📱 LANGKAH 2: Setup Permissions"
termux-wake-lock
echo "✅ Wake lock enabled"

# 3. Buat directory boot
mkdir -p ~/.termux/boot
chmod +x ~/.termux/boot

# 4. Buat script auto-start
cat > ~/.termux/boot/start-mowilex.sh << 'BOOTSCRIPT'
#!/data/data/com.termux/files/usr/bin/bash

# Wait untuk sistem siap
sleep 15

# Acquire wake lock agar tidak sleep
termux-wake-lock

# Log file
LOG_FILE="$HOME/mowilex-boot.log"
echo "🚀 Starting Mowilex at $(date)" > "$LOG_FILE"

# Masuk ke directory project
cd ~/mowilex-valve-control || exit 1

# Activate virtual environment jika ada
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Django dengan Modbus
echo "Starting Django + Modbus..." >> "$LOG_FILE"
python main.py >> "$LOG_FILE" 2>&1 &

# Simpan PID
echo $! > ~/mowilex.pid

echo "✅ Mowilex started with PID: $(cat ~/mowilex.pid)" >> "$LOG_FILE"
BOOTSCRIPT

chmod +x ~/.termux/boot/start-mowilex.sh

# 5. Buat shortcut untuk manual start/stop
cat > ~/start-mowilex.sh << 'STARTSCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/mowilex-valve-control
source venv/bin/activate 2>/dev/null
python main.py
STARTSCRIPT

cat > ~/stop-mowilex.sh << 'STOPSCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
if [ -f ~/mowilex.pid ]; then
    PID=$(cat ~/mowilex.pid)
    kill $PID 2>/dev/null
    rm ~/mowilex.pid
    echo "✅ Mowilex stopped"
else
    echo "❌ Mowilex tidak berjalan"
fi
STOPSCRIPT

chmod +x ~/start-mowilex.sh
chmod +x ~/stop-mowilex.sh

echo ""
echo "✅ SETUP SELESAI!"
echo ""
echo "📋 LANGKAH SELANJUTNYA:"
echo ""
echo "1. Buka aplikasi Termux:Boot"
echo "2. Grant permission yang diminta"
echo "3. Restart device untuk test auto-start"
echo "4. Buka browser ke: http://localhost:8000"
echo ""
echo "📝 COMMAND TERSEDIA:"
echo "   ~/start-mowilex.sh  - Manual start"
echo "   ~/stop-mowilex.sh   - Stop service"
echo "   cat ~/mowilex-boot.log - Lihat log"
echo ""
echo "🔍 TROUBLESHOOTING:"
echo "   - Log boot: cat ~/mowilex-boot.log"
echo "   - Check process: ps aux | grep python"
echo "   - Check port: netstat -tuln | grep 8000"
echo ""
