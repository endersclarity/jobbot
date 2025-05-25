#!/bin/bash
# Fix Puppeteer Browser Dependencies for Indeed War
# Round 4: Installing missing browser libraries

echo "🔧 Installing Puppeteer browser dependencies..."
echo "Missing libraries: libnss3, libnssutil3, libsmime3, libnspr4, libasound2"

# Update package list
sudo apt-get update

# Install missing dependencies
sudo apt-get install -y \
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
    libxshmfence1

echo "✅ Dependencies installed!"
echo "Testing browser launch..."

# Test if Chrome can now launch
/home/ender/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome --version

echo "🚀 Ready for Puppeteer Indeed attack!"