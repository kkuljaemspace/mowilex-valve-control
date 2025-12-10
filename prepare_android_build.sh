#!/bin/bash
# Prepare project untuk Android build

echo "========================================="
echo "🔧 PREPARING PROJECT FOR ANDROID BUILD"
echo "========================================="
echo ""

# 1. Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✅ Static files collected"
echo ""

# 2. Make migrations
echo "🗄️  Checking migrations..."
python manage.py makemigrations
python manage.py migrate
echo "✅ Database ready"
echo ""

# 3. Create default ModbusConfig if not exists
echo "⚙️  Setting up Modbus config..."
python manage.py shell << EOF
from project.models import ModbusConfig
if not ModbusConfig.objects.exists():
    ModbusConfig.objects.create(
        android_ip='0.0.0.0',
        android_port=9502,
        plc_ip='192.168.1.100',
        plc_port=502,
        auto_start=True
    )
    print('✅ Default Modbus config created')
else:
    print('✅ Modbus config already exists')
EOF
echo ""

# 4. Clean up unnecessary files
echo "🧹 Cleaning up..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name ".DS_Store" -delete
echo "✅ Cleanup done"
echo ""

# 5. Check file permissions
echo "🔐 Setting permissions..."
chmod +x main.py
chmod +x modbus_service.py
chmod +x start_modbus_server.py
echo "✅ Permissions set"
echo ""

# 6. Verify requirements
echo "📋 Verifying requirements..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
else
    echo "⚠️  requirements.txt not found - generating..."
    pip freeze > requirements.txt
fi
echo ""

# 7. Test imports
echo "🧪 Testing critical imports..."
python -c "
import django
import pyModbusTCP
print('✅ Django:', django.__version__)
print('✅ pyModbusTCP: OK')
" || echo "❌ Import test failed"
echo ""

echo "========================================="
echo "✅ PROJECT READY FOR BUILD"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. buildozer android debug     # Build debug APK"
echo "2. buildozer android deploy    # Deploy to device"
echo "3. buildozer android logcat    # View logs"
echo ""
echo "APK will be in: bin/"
echo ""
