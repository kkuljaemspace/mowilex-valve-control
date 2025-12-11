#!/data/data/com.termux/files/usr/bin/bash
# Termux Setup Script for Mowilex Valve Control
# Run this script once after installing Termux

echo "🔧 Setting up Mowilex Valve Control in Termux..."

# Update packages
echo "📦 Updating packages..."
pkg update -y && pkg upgrade -y

# Install required packages
echo "📦 Installing Python and dependencies..."
pkg install -y python git clang openssl libffi

# Upgrade pip
pip install --upgrade pip

# Install Python packages
echo "🐍 Installing Python packages..."
pip install django==5.1.1 pyModbusTCP pillow requests python-dateutil

# Create project directory
echo "📁 Setting up project directory..."
cd ~ || exit
PROJECT_DIR=~/mowilex-valve-control

# Check if already cloned
if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  Project directory already exists. Pulling latest changes..."
    cd "$PROJECT_DIR" || exit
    git pull
else
    echo "📥 Cloning project from GitHub..."
    git clone https://github.com/kkuljaemspace/mowilex-valve-control.git
    cd "$PROJECT_DIR" || exit
fi

# Setup database
echo "🗄️  Setting up database..."
python manage.py migrate

# Create superuser (interactive)
echo "👤 Create admin user (you'll be prompted for username/password):"
python manage.py createsuperuser

# Setup autostart
echo "🚀 Setting up autostart..."
mkdir -p ~/.termux/boot
cp termux-boot.sh ~/.termux/boot/start-mowilex.sh
chmod +x ~/.termux/boot/start-mowilex.sh

# Create start script
cat > ~/start-mowilex.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/mowilex-valve-control
python main.py > ~/mowilex.log 2>&1 &
echo $! > ~/mowilex.pid
echo "✅ Mowilex Valve Control started! PID: $(cat ~/mowilex.pid)"
echo "📝 Log: ~/mowilex.log"
echo "🌐 Web: http://localhost:8000"
EOF

chmod +x ~/start-mowilex.sh

# Create stop script
cat > ~/stop-mowilex.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
if [ -f ~/mowilex.pid ]; then
    PID=$(cat ~/mowilex.pid)
    kill $PID 2>/dev/null
    rm ~/mowilex.pid
    echo "✅ Mowilex stopped (PID: $PID)"
else
    echo "⚠️  No PID file found. Searching for process..."
    pkill -f "python main.py"
    echo "✅ All Python processes killed"
fi
EOF

chmod +x ~/stop-mowilex.sh

# Create status script
cat > ~/status-mowilex.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
if [ -f ~/mowilex.pid ]; then
    PID=$(cat ~/mowilex.pid)
    if ps -p $PID > /dev/null; then
        echo "✅ Mowilex is RUNNING (PID: $PID)"
        echo "🌐 Web UI: http://localhost:8000"
        echo "📡 Modbus: localhost:9502"
        tail -20 ~/mowilex.log
    else
        echo "❌ Mowilex is NOT running (stale PID file)"
        rm ~/mowilex.pid
    fi
else
    echo "❌ Mowilex is NOT running"
fi
EOF

chmod +x ~/status-mowilex.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📱 Commands:"
echo "  Start:  ~/start-mowilex.sh"
echo "  Stop:   ~/stop-mowilex.sh"
echo "  Status: ~/status-mowilex.sh"
echo ""
echo "🚀 To start now, run:"
echo "  ~/start-mowilex.sh"
echo ""
echo "🔄 For autostart on Termux boot:"
echo "  1. Install Termux:Boot from F-Droid"
echo "  2. Open Termux:Boot once"
echo "  3. Script will auto-run on device boot"
echo ""
