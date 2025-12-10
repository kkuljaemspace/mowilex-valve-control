#!/bin/bash
# Script untuk build APK menggunakan Docker
# Otomatis install Docker jika belum ada (manual), lalu build APK

echo "========================================="
echo "🏗️  BUILD ANDROID APK - DOCKER METHOD"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed!"
    echo ""
    echo "📥 Please install Docker Desktop for Mac:"
    echo "   1. Download: https://www.docker.com/products/docker-desktop"
    echo "   2. Install Docker Desktop"
    echo "   3. Start Docker Desktop"
    echo "   4. Run this script again"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is ready!"
echo ""

# Pull buildozer image
echo "📦 Pulling buildozer image (first time may take ~5-10 min)..."
docker pull kivy/buildozer

echo ""
echo "🔨 Building APK..."
echo "   This will take 15-30 minutes on first build"
echo "   Subsequent builds will be much faster (5-10 min)"
echo ""

# Create bin directory if not exists
mkdir -p bin

# Build APK with Docker
docker run --rm \
    -v "$(pwd)":/home/user/app \
    -v "$HOME/.buildozer":/home/user/.buildozer \
    kivy/buildozer \
    android debug

# Check if APK was created
if ls bin/*.apk 1> /dev/null 2>&1; then
    echo ""
    echo "========================================="
    echo "✅ APK BUILD SUCCESSFUL!"
    echo "========================================="
    echo ""
    echo "📱 APK Location:"
    ls -lh bin/*.apk
    echo ""
    echo "📦 APK Size:"
    du -h bin/*.apk | awk '{print $1}'
    echo ""
    echo "📤 Transfer to Android:"
    echo "   1. Connect Android via USB"
    echo "   2. Copy APK to phone:"
    echo "      adb install -r bin/*.apk"
    echo "   OR"
    echo "   3. Email/Upload APK and download on phone"
    echo ""
else
    echo ""
    echo "❌ Build failed! Check logs above."
    echo ""
fi
