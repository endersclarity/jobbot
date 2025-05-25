#!/bin/bash
# Fix Puppeteer Browser Dependencies for Indeed War
# Round 4: Installing missing browser libraries

echo "🔧 Installing Puppeteer browser dependencies..."
echo "Missing libraries: libnss3, libnssutil3, libsmime3, libnspr4, libasound2"

# Check if running on Debian/Ubuntu
if ! command -v apt-get &> /dev/null; then
    echo "❌ This script requires apt-get (Debian/Ubuntu)"
    exit 1
fi

# Update package list
if ! sudo apt-get update; then
    echo "❌ Failed to update package list"
    exit 1
fi

# Install missing dependencies
if ! sudo apt-get install -y \
    libnss3 \
    libnss3-dev \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libxshmfence1; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed!"
echo "Testing browser launch..."

# Find Chrome binary dynamically
CHROME_PATH=$(find ~/.cache/puppeteer -name "chrome" -type f 2>/dev/null | head -1)
if [ -n "$CHROME_PATH" ]; then
    "$CHROME_PATH" --version
else
    echo "⚠️ Chrome binary not found in Puppeteer cache"
    exit 1
fi

echo "🚀 Ready for Puppeteer Indeed attack!"