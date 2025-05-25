#!/bin/bash

# RSI Stock Tracker Setup Script
# This script sets up the RSI Stock Tracker application for desktop use

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE} RSI Stock Tracker Setup${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Main setup function
main() {
    print_header
    
    # Check if Python is installed
    print_status "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python $python_version found"
    
    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip first."
        exit 1
    fi
    
    # Create virtual environment (optional but recommended)
    print_status "Setting up virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Install requirements
    print_status "Installing required packages..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
    
    # Create desktop launcher script
    print_status "Creating desktop launcher..."
    
    # Get current directory
    current_dir=$(pwd)
    
    # Create launcher script
    cat > run_rsi_tracker.sh << EOF
#!/bin/bash
# RSI Stock Tracker Launcher
cd "$current_dir"
source venv/bin/activate
python3 rsi_tracker_app.py
EOF
    
    # Make launcher executable
    chmod +x run_rsi_tracker.sh
    print_success "Desktop launcher created: run_rsi_tracker.sh"
    
    # Create application wrapper for macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "Creating macOS application wrapper..."
        
        # Create .app directory structure
        app_name="RSI Stock Tracker.app"
        mkdir -p "$app_name/Contents/MacOS"
        mkdir -p "$app_name/Contents/Resources"
        
        # Create Info.plist
        cat > "$app_name/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>RSI Stock Tracker</string>
    <key>CFBundleIdentifier</key>
    <string>com.benggoy.rsi-tracker</string>
    <key>CFBundleName</key>
    <string>RSI Stock Tracker</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>
EOF
        
        # Create main executable
        cat > "$app_name/Contents/MacOS/RSI Stock Tracker" << EOF
#!/bin/bash
cd "$current_dir"
source venv/bin/activate
python3 rsi_tracker_app.py
EOF
        
        chmod +x "$app_name/Contents/MacOS/RSI Stock Tracker"
        print_success "macOS app created: $app_name"
    fi
    
    # Create Windows batch file
    print_status "Creating Windows launcher..."
    cat > run_rsi_tracker.bat << 'EOF'
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python rsi_tracker_app.py
pause
EOF
    print_success "Windows launcher created: run_rsi_tracker.bat"
    
    # Final instructions
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN} Setup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    
    echo "Your RSI Stock Tracker is now ready to use!"
    echo ""
    echo "To run the application:"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  • Double-click: RSI Stock Tracker.app"
        echo "  • Terminal: ./run_rsi_tracker.sh"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "  • Double-click: run_rsi_tracker.bat"
        echo "  • Command prompt: run_rsi_tracker.bat"
    else
        echo "  • Terminal: ./run_rsi_tracker.sh"
    fi
    
    echo ""
    echo "Features:"
    echo "  ✅ Real-time RSI tracking"
    echo "  ✅ Add/remove stocks from watchlist"
    echo "  ✅ Automatic updates every 30 seconds"
    echo "  ✅ Color-coded RSI status indicators"
    echo "  ✅ Persistent watchlist storage"
    
    echo ""
    echo "Usage Tips:"
    echo "  • Add stocks using symbols like AAPL, GOOGL, TSLA"
    echo "  • RSI > 70 = Overbought (Red)"
    echo "  • RSI < 30 = Oversold (Green)"
    echo "  • RSI 30-70 = Neutral (Yellow)"
    
    echo ""
    print_warning "Note: First run may take a moment to download stock data"
}

# Run main function
main "$@"
