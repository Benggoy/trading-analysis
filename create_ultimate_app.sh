#!/bin/bash
# Ultimate Enhanced RSI Tracker - Mac App Builder with Charts & Import
# Creates a comprehensive Mac app with all features

set -e  # Exit on any error

echo "🚀 Ultimate Enhanced RSI Stock Tracker - Mac App Builder"
echo "======================================================"
echo "📈 Features: Real-time RSI + Interactive Charts + Portfolio Import"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

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

print_feature() {
    echo -e "${PURPLE}[FEATURE]${NC} $1"
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
    print_status "Please run this script from the directory containing your Ultimate RSI tracker app"
    exit 1
fi

print_feature "Ultimate RSI Tracker Features:"
print_feature "✅ Real-time RSI monitoring with color-coded alerts"
print_feature "✅ Interactive matplotlib charts (Price + RSI analysis)"
print_feature "✅ Optional Plotly interactive charts (opens in browser)"
print_feature "✅ Portfolio import from CSV/TXT files"
print_feature "✅ Bulk stock addition"
print_feature "✅ Comprehensive market data display"
print_feature "✅ Professional dark theme interface"
print_feature "✅ Seeking Alpha integration"
print_feature "✅ Tabbed interface (Tracker + Charts)"

# Create virtual environment
print_status "Creating virtual environment for Ultimate app building..."
if [ -d "venv_ultimate" ]; then
    rm -rf venv_ultimate
fi

python3 -m venv venv_ultimate
source venv_ultimate/bin/activate

print_success "Virtual environment created and activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install ultimate requirements
print_status "Installing Ultimate RSI Tracker requirements..."
if [ -f "requirements-ultimate.txt" ]; then
    pip install -r requirements-ultimate.txt
else
    print_warning "requirements-ultimate.txt not found, installing essential requirements..."
    pip install yfinance pandas numpy matplotlib seaborn plotly scipy requests beautifulsoup4 pyinstaller
fi

print_success "All dependencies installed successfully!"

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build dist *.spec __pycache__

# Create directories for charts if they don't exist
mkdir -p charts

# Build the Ultimate Mac app bundle
print_status "Building Ultimate Enhanced RSI Tracker Mac app..."

pyinstaller \
    --name "Ultimate Enhanced RSI Tracker" \
    --onedir \
    --windowed \
    --clean \
    --noconfirm \
    --osx-bundle-identifier "com.benggoy.ultimate-enhanced-rsi-tracker" \
    --hidden-import yfinance \
    --hidden-import pandas \
    --hidden-import numpy \
    --hidden-import matplotlib \
    --hidden-import matplotlib.pyplot \
    --hidden-import matplotlib.backends.backend_tkagg \
    --hidden-import seaborn \
    --hidden-import plotly \
    --hidden-import plotly.graph_objects \
    --hidden-import plotly.offline \
    --hidden-import scipy \
    --hidden-import tkinter \
    --hidden-import tkinter.ttk \
    --hidden-import tkinter.filedialog \
    --add-data "sample_portfolio.csv:." \
    ultimate_rsi_tracker.py

# Check if build was successful
if [ -d "dist/Ultimate Enhanced RSI Tracker.app" ]; then
    print_success "Ultimate Enhanced RSI Tracker.app created successfully!"
    
    # Make the app executable
    chmod +x "dist/Ultimate Enhanced RSI Tracker.app/Contents/MacOS/Ultimate Enhanced RSI Tracker"
    
    # Copy sample files if they exist
    if [ -f "watchlist.json" ]; then
        cp watchlist.json "dist/Ultimate Enhanced RSI Tracker.app/Contents/MacOS/"
        print_status "Copied existing watchlist to app bundle"
    fi
    
    if [ -f "sample_portfolio.csv" ]; then
        cp sample_portfolio.csv "dist/Ultimate Enhanced RSI Tracker.app/Contents/MacOS/"
        print_status "Copied sample portfolio for testing imports"
    fi
    
    APP_PATH="$(pwd)/dist/Ultimate Enhanced RSI Tracker.app"
    
    echo ""
    print_success "🎉 Ultimate Enhanced RSI Tracker.app has been created!"
    echo ""
    echo "📍 Location: $APP_PATH"
    echo ""
    echo "🎯 Ultimate Features Available:"
    echo "   📊 Real-time RSI tracking with professional interface"
    echo "   📈 Interactive matplotlib charts (Price + RSI analysis)"
    echo "   🚀 Optional Plotly charts (interactive browser-based)"
    echo "   📁 Portfolio import from CSV/TXT files"
    echo "   📋 Bulk stock addition via text input"
    echo "   🔗 Seeking Alpha integration (double-click stocks)"
    echo "   💾 Persistent watchlist storage"
    echo "   🎨 Professional dark theme optimized for trading"
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
    read -p "Would you like to test the Ultimate RSI Tracker now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Opening Ultimate Enhanced RSI Tracker..."
        open "$APP_PATH"
        print_status "The app should now be running!"
        echo ""
        echo "🎮 How to use your Ultimate RSI Tracker:"
        echo "   1. Add stocks manually or import your portfolio"
        echo "   2. View real-time RSI data in the main tracker tab"
        echo "   3. Select any stock and click 'View Chart' for technical analysis"
        echo "   4. Use the Charts tab for detailed price and RSI analysis"
        echo "   5. Double-click stocks to view on Seeking Alpha"
        echo ""
    fi
    
    # Offer to install to Applications
    read -p "Would you like to install it to Applications folder? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing Ultimate Enhanced RSI Tracker to Applications..."
        cp -r "$APP_PATH" /Applications/
        print_success "Installed to Applications folder!"
        print_status "You can now launch it from Launchpad or Spotlight search"
    fi
    
else
    print_error "Build failed - app bundle not created"
    echo "Check the output above for error details"
    exit 1
fi

# Deactivate virtual environment
deactivate

print_success "Ultimate Enhanced RSI Tracker build process completed!"
print_feature "Your app now includes:"
print_feature "• Real-time stock tracking with RSI analysis"
print_feature "• Interactive charts with matplotlib"
print_feature "• Portfolio import capabilities"
print_feature "• Professional trading interface"
print_feature "• All the features of a premium stock analysis tool!"

print_status "You can now delete the 'venv_ultimate' directory if desired"
echo ""
print_success "🎊 Enjoy your Ultimate Enhanced RSI Stock Tracker Mac App! 📈🚀"