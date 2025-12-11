#!/data/data/com.termux/files/usr/bin/bash
# Termux Boot Script - Auto-starts Mowilex on device boot
# This file should be in: ~/.termux/boot/start-mowilex.sh

# Wait for Termux to fully initialize
sleep 10

# Set project directory
PROJECT_DIR=~/mowilex-valve-control
LOG_FILE=~/mowilex.log
PID_FILE=~/mowilex.pid

# Check if project exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project not found at $PROJECT_DIR" >> "$LOG_FILE"
    exit 1
fi

# Navigate to project
cd "$PROJECT_DIR" || exit 1

# Start the service
echo "🚀 Starting Mowilex Valve Control at $(date)" >> "$LOG_FILE"
python main.py >> "$LOG_FILE" 2>&1 &

# Save PID
echo $! > "$PID_FILE"

echo "✅ Started with PID: $(cat $PID_FILE)" >> "$LOG_FILE"
echo "🌐 Web UI: http://localhost:8000" >> "$LOG_FILE"
echo "📡 Modbus: localhost:9502" >> "$LOG_FILE"
