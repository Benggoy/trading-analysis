#!/bin/bash
# Enhanced RSI Tracker - Mac App Builder
# This script will create a standalone Mac application

set -e  # Exit on any error

echo "🚀 Enhanced RSI Stock Tracker - Mac App Builder"
echo "==============================================\n"
echo "📈 Features: Real-time RSI + Interactive Charts + Portfolio Import"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "ultimate_rsi_tracker.py" ]; then
    print_error "ultimate_rsi_tracker.py not found in current directory"
    print_status "Please run this script from the directory containing your RSI tracker app"
    exit 1
fi

# Create virtual environment
print_status "Creating virtual environment for app building..."
if [ -d "venv_build" ]; then
    rm -rf venv_build
fi

python3 -m venv venv_build
source venv_build/bin/activate

print_success "Virtual environment created and activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing application requirements..."
if [ -f "requirements-ultimate.txt" ]; then
    pip install -r requirements-ultimate.txt
else
    print_warning "requirements-ultimate.txt not found, installing basic requirements..."
    pip install yfinance pandas numpy matplotlib seaborn plotly scipy requests beautifulsoup4
fi

# Install PyInstaller
print_status "Installing PyInstaller..."
pip install pyinstaller

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build dist *.spec __pycache__

# Build with PyInstaller
pyinstaller \
    --name "Enhanced RSI Tracker" \
    --onedir \
    --windowed \
    --clean \
    --noconfirm \
    --osx-bundle-identifier "com.benggoy.enhanced-rsi-tracker" \
    --hidden-import yfinance \
    --hidden-import pandas \
    --hidden-import numpy \
    --hidden-import matplotlib \
    --hidden-import tkinter \
    ultimate_rsi_tracker.py

# Check if build was successful
if [ -d "dist/Enhanced RSI Tracker.app" ]; then
    print_success "App bundle created successfully!"
    
    # Make the app executable
    chmod +x "dist/Enhanced RSI Tracker.app/Contents/MacOS/Enhanced RSI Tracker"
    
    # Copy watchlist if it exists
    if [ -f "watchlist.json" ]; then
        cp watchlist.json "dist/Enhanced RSI Tracker.app/Contents/MacOS/"
        print_status "Copied existing watchlist to app bundle"
    fi
    
    APP_PATH="$(pwd)/dist/Enhanced RSI Tracker.app"
    
    echo ""
    print_success "🎉 Enhanced RSI Tracker.app has been created!"
    echo ""
    echo "📍 Location: $APP_PATH"
    echo ""
    echo "🔧 Installation Options:"
    echo "   1. Double-click the app to run it directly"
    echo "   2. Drag it to Applications folder for permanent installation"
    echo "   3. Create an alias on your desktop"
    echo ""
    echo "🚀 Quick Commands:"
    echo "   • Open app: open '$APP_PATH'"
    echo "   • Install to Applications: cp -r '$APP_PATH' /Applications/"
    echo "   • Create desktop alias: ln -s '$APP_PATH' ~/Desktop/"
    echo ""
    
    # Offer to open the app
    read -p "Would you like to open the app now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Opening Enhanced RSI Tracker..."
        open "$APP_PATH"
    fi
    
    # Offer to install to Applications
    read -p "Would you like to install it to Applications folder? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing to Applications..."
        cp -r "$APP_PATH" /Applications/
        print_success "Installed to Applications folder!"
    fi
    
else
    print_error "Build failed - app bundle not created"
    echo "Check the output above for error details"
    exit 1
fi

# Deactivate virtual environment
deactivate

print_success "Build process completed!"
print_status "You can now delete the 'venv_build' directory if desired"
