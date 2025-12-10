#!/data/data/com.termux/files/usr/bin/bash
# Script untuk setup dan run Mowilex di Termux Android
# Copy script ini ke HP dan jalankan di Termux

echo "========================================="
echo "📱 MOWILEX VALVE CONTROL - TERMUX SETUP"
echo "========================================="
echo ""

# Update packages
echo "📦 Updating packages..."
pkg update -y
pkg upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
pkg install -y python git

# Install Python packages
echo "🐍 Installing Python packages..."
pip install django pyModbusTCP pillow requests python-dateutil cryptography

# Setup storage access (optional)
echo "📂 Setting up storage access..."
termux-setup-storage

# Create app directory
APP_DIR="$HOME/mowilex-valve-control"
if [ -d "$APP_DIR" ]; then
    echo "⚠️  App directory exists. Backing up..."
    mv "$APP_DIR" "$APP_DIR.backup.$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$APP_DIR"
cd "$APP_DIR"

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "========================================="
echo "📥 NEXT STEPS:"
echo "========================================="
echo ""
echo "1. Copy all project files to: $APP_DIR"
echo "   Via:"
echo "   - USB transfer to /storage/emulated/0/"
echo "   - Git clone (if you have repo)"
echo "   - Termux file sharing"
echo ""
echo "2. After files are copied, run:"
echo "   cd $APP_DIR"
echo "   python manage.py migrate"
echo "   python manage.py createsuperuser"
echo "   python main.py"
echo ""
echo "3. Access web UI:"
echo "   http://localhost:8000"
echo ""
echo "4. For auto-start on boot:"
echo "   pkg install termux-services"
echo "   sv-enable mowilex"
echo ""
echo "========================================="
echo "📝 SAVE THIS LOCATION:"
echo "   $APP_DIR"
echo "========================================="
echo ""
