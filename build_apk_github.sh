#!/bin/bash
# Script untuk build APK via GitHub Actions dan download ke folder lokal

echo "========================================="
echo "🏗️  BUILD APK VIA GITHUB ACTIONS"
echo "========================================="
echo ""

# Check if git repo exists
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - Mowilex Valve Control"
    echo "✅ Git repo initialized"
    echo ""
fi

# Check if remote exists
if ! git remote | grep -q "origin"; then
    echo "⚠️  No remote repository configured!"
    echo ""
    echo "Please create a GitHub repository and add it:"
    echo "  1. Go to https://github.com/new"
    echo "  2. Create new repository (e.g., mowilex-valve-control)"
    echo "  3. Run:"
    echo "     git remote add origin https://github.com/USERNAME/REPO.git"
    echo "     git push -u origin main"
    echo ""
    echo "GitHub Actions will automatically build APK on push."
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Build APK - $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
git push

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "========================================="
echo "📱 APK AKAN TERSEDIA DI:"
echo "========================================="
echo ""
echo "1. Buka: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\).git/\1/')/actions"
echo "2. Klik workflow yang sedang running"
echo "3. Tunggu build selesai (~15-20 menit)"
echo "4. Download APK dari 'Artifacts'"
echo ""
echo "Atau gunakan script ini untuk auto-download:"
echo "  ./download_apk_from_github.sh"
echo ""
