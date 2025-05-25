#!/bin/bash
# 🚀 Quick Setup Script for Trading Analysis
# Resolves common installation issues

set -e

echo "🚀 Trading Analysis - Quick Setup"
echo "================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_status "Python $PYTHON_VERSION detected"

if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    print_error "Python 3.8+ required. Current: $PYTHON_VERSION"
    exit 1
fi

# Create and activate virtual environment
print_status "Creating virtual environment..."
python3 -m venv trading_env
source trading_env/bin/activate 2>/dev/null || source trading_env/Scripts/activate

# Upgrade pip first
print_status "Upgrading pip..."
python -m pip install --upgrade pip

# Install core dependencies first (most compatible)
print_status "Installing core dependencies..."
pip install numpy pandas matplotlib seaborn yfinance

# Install visualization
print_status "Installing visualization tools..."
pip install plotly

# Install technical analysis (pandas_ta is more reliable than TA-Lib)
print_status "Installing technical analysis tools..."
pip install pandas-ta

# Install development tools (optional)
print_warning "Installing development tools (optional)..."
pip install pytest black flake8 || echo "Development tools installation failed (non-critical)"

# Test core functionality
print_status "Testing core functionality..."
python -c "
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
print('✅ Core packages working')

# Test market data
try:
    ticker = yf.Ticker('AAPL')
    data = ticker.history(period='5d')
    if not data.empty:
        print('✅ Market data connection working')
    else:
        print('⚠️ Market data connection issues (may be network/API related)')
except Exception as e:
    print(f'⚠️ Market data test: {e}')

print('✅ Setup completed successfully!')
"

echo ""
print_status "Setup completed! To activate environment:"
echo "source trading_env/bin/activate  # Linux/Mac"
echo "trading_env\\Scripts\\activate     # Windows"
echo ""
print_status "Test the RSI calculator:"
echo "cd indicators && python rsi_calculator.py"
