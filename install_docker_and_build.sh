#!/bin/bash
# Auto-install Docker Desktop dan build APK

echo "========================================="
echo "🐳 DOCKER AUTO-INSTALLER + APK BUILDER"
echo "========================================="
echo ""

# Check if Homebrew installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found!"
    echo "Install Homebrew first: https://brew.sh"
    exit 1
fi

echo "✅ Homebrew found: $(brew --version | head -1)"
echo ""

# Check if Docker already installed
if command -v docker &> /dev/null; then
    echo "✅ Docker already installed: $(docker --version)"
    
    # Check if Docker is running
    if docker info &> /dev/null 2>&1; then
        echo "✅ Docker is running!"
    else
        echo "⚠️  Docker installed but not running"
        echo "Starting Docker Desktop..."
        open -a Docker
        echo "⏳ Waiting for Docker to start (30 seconds)..."
        sleep 30
    fi
else
    echo "📥 Installing Docker Desktop via Homebrew..."
    echo "   This may take 5-10 minutes..."
    echo ""
    
    brew install --cask docker
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker Desktop installed!"
        echo ""
        echo "🚀 Starting Docker Desktop..."
        open -a Docker
        
        echo "⏳ Waiting for Docker to initialize (60 seconds)..."
        echo "   You may see Docker whale icon in menu bar when ready"
        sleep 60
    else
        echo "❌ Docker installation failed!"
        echo "Please install manually: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
fi

# Verify Docker is ready
echo ""
echo "🔍 Verifying Docker..."
if docker info &> /dev/null 2>&1; then
    echo "✅ Docker is ready!"
else
    echo "⚠️  Docker not ready yet. Please:"
    echo "   1. Make sure Docker Desktop is running (check menu bar)"
    echo "   2. Wait until status shows 'Running'"
    echo "   3. Run this script again"
    exit 1
fi

echo ""
echo "========================================="
echo "🏗️  BUILDING APK"
echo "========================================="
echo ""

# Pull buildozer image
echo "📦 Pulling buildozer Docker image..."
echo "   First time: ~5-10 minutes"
docker pull kivy/buildozer

# Create bin directory
mkdir -p bin

echo ""
echo "🔨 Building Android APK..."
echo "   ⏱️  First build: 20-30 minutes"
echo "   ⏱️  Subsequent: 5-10 minutes"
echo ""
echo "☕ Go grab a coffee... This will take a while!"
echo ""

# Build APK
docker run --rm \
    -v "$(pwd)":/home/user/app \
    -v "$HOME/.buildozer":/home/user/.buildozer \
    kivy/buildozer \
    android debug

# Check result
echo ""
echo "========================================="
if ls bin/*.apk 1> /dev/null 2>&1; then
    echo "✅ APK BUILD SUCCESSFUL!"
    echo "========================================="
    echo ""
    echo "📱 APK Details:"
    ls -lh bin/*.apk
    echo ""
    echo "📊 File Size:"
    du -h bin/*.apk | awk '{print "   " $1}'
    echo ""
    echo "📤 Install to Android:"
    echo "   1. Connect Android via USB"
    echo "   2. Enable USB Debugging"
    echo "   3. Run: adb install -r bin/*.apk"
    echo ""
    echo "   OR transfer file manually:"
    echo "   - Email APK to yourself"
    echo "   - Download on Android"
    echo "   - Install (enable 'Unknown Sources')"
    echo ""
    echo "✅ APK Location: $(pwd)/bin/"
    echo ""
else
    echo "❌ BUILD FAILED!"
    echo "========================================="
    echo ""
    echo "Check error messages above."
    echo "Common issues:"
    echo "   - Not enough disk space (need ~5GB)"
    echo "   - Network issues downloading dependencies"
    echo "   - Docker not enough memory (increase in Docker settings)"
    echo ""
fi
