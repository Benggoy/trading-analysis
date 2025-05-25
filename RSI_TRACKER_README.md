# 📈 RSI Stock Tracker - Desktop Application

A real-time desktop application for tracking RSI (Relative Strength Index) of your favorite stocks. Built with Python and tkinter for a native desktop experience.

![RSI Tracker](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎯 Real-Time Stock Tracking
- **Live RSI calculations** for any stock symbol
- **Automatic updates** every 30 seconds
- **Real-time price data** from Yahoo Finance
- **Persistent watchlist** that saves between sessions

### 📊 RSI Analysis
- **Professional RSI calculation** using 14-period standard
- **Color-coded status indicators**:
  - 🔴 **Overbought** (RSI > 70)
  - 🟡 **Neutral** (RSI 30-70)
  - 🟢 **Oversold** (RSI < 30)
- **Price change tracking** with dollar and percentage changes

### 🖥️ Desktop-Ready Interface
- **Native desktop application** using tkinter
- **Dark theme** for comfortable extended use
- **Resizable interface** that adapts to your screen
- **Easy stock management** - add/remove with simple clicks

### 📱 User-Friendly Design
- **Intuitive interface** suitable for all experience levels
- **Real-time status updates** and last update timestamps
- **Error handling** for invalid symbols and network issues
- **Watchlist persistence** - your stocks are remembered

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/Benggoy/trading-analysis.git
cd trading-analysis

# Run the automated setup
chmod +x setup_tracker.sh
./setup_tracker.sh

# Launch the application
./run_rsi_tracker.sh        # On macOS/Linux
# OR double-click run_rsi_tracker.bat on Windows
```

### Option 2: Manual Setup

```bash
# Prerequisites: Python 3.8+ and pip

# 1. Clone the repository
git clone https://github.com/Benggoy/trading-analysis.git
cd trading-analysis

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python3 rsi_tracker_app.py
```

## 📋 Requirements

### System Requirements
- **Python 3.8+** (Python 3.9+ recommended)
- **Internet connection** for real-time stock data
- **1GB RAM** minimum
- **Any desktop OS**: Windows, macOS, or Linux

### Python Dependencies
- `yfinance` - Yahoo Finance data access
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `tkinter` - GUI framework (included with Python)

## 🎮 How to Use

### Adding Stocks to Your Watchlist

1. **Enter Stock Symbol**: Type any stock symbol (e.g., AAPL, GOOGL, TSLA) in the input field
2. **Click Add** or **Press Enter**: The stock will be validated and added to your tracking list
3. **Automatic Updates**: The app will start tracking RSI and price data automatically

### Understanding the Display

| Column | Description |
|--------|-------------|
| **Symbol** | Stock ticker symbol |
| **Price** | Current stock price in USD |
| **Change ($)** | Price change from previous close |
| **Change %** | Percentage price change |
| **RSI** | Current RSI value (0-100) |
| **Status** | RSI interpretation (Overbought/Neutral/Oversold) |
| **Updated** | Last data update timestamp |

### RSI Interpretation Guide

#### 🔴 Overbought (RSI > 70)
- **Meaning**: Stock may be overvalued
- **Potential Action**: Consider taking profits if holding
- **Caution**: In strong uptrends, stocks can stay overbought longer

#### 🟡 Neutral (RSI 30-70)
- **Meaning**: Normal trading range
- **Potential Action**: Monitor for trend changes
- **Note**: Most stocks spend majority of time in this range

#### 🟢 Oversold (RSI < 30)
- **Meaning**: Stock may be undervalued
- **Potential Action**: Consider buying opportunities
- **Caution**: In strong downtrends, stocks can stay oversold longer

## ⚙️ Configuration & Customization

### Watchlist Management
- **Persistent Storage**: Watchlist automatically saved to `watchlist.json`
- **Easy Removal**: Select any stock and click "Remove Selected"
- **No Limits**: Add as many stocks as you want to track

### Update Settings
- **Default Interval**: 30 seconds between updates
- **Manual Refresh**: "Refresh Now" button for immediate updates
- **Rate Limiting**: Built-in delays to respect API limits

### Data Sources
- **Primary**: Yahoo Finance (via yfinance library)
- **Coverage**: All major stock exchanges worldwide
- **Reliability**: Industrial-grade financial data provider

## 🛠️ Advanced Usage

### Creating a Desktop Executable

For easier distribution, you can create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable (one file)
pyinstaller --onefile --windowed --name "RSI Stock Tracker" rsi_tracker_app.py

# The executable will be in the 'dist' folder
```

### Running on Startup (Optional)

#### macOS:
1. Open **System Preferences** → **Users & Groups** → **Login Items**
2. Add the RSI Stock Tracker.app to startup applications

#### Windows:
1. Press **Win+R**, type `shell:startup`
2. Copy the `run_rsi_tracker.bat` file to the startup folder

#### Linux:
Add to your desktop environment's startup applications:
```bash
# Add to ~/.bashrc or create a .desktop file
/path/to/your/run_rsi_tracker.sh
```

## 🔧 Troubleshooting

### Common Issues

#### "Module not found" Error
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

#### "Invalid Symbol" Error
- **Check spelling** of stock symbol
- **Verify symbol exists** on Yahoo Finance
- **Try alternative symbols** (e.g., BRK-B for Berkshire Hathaway Class B)

#### Slow Data Loading
- **Check internet connection**
- **Yahoo Finance may be experiencing issues**
- **Try manual refresh** after a few minutes

#### Application Won't Start
```bash
# Check Python version
python3 --version

# Ensure tkinter is available
python3 -c "import tkinter; print('tkinter works!')"

# Run with verbose output
python3 -v rsi_tracker_app.py
```

### Performance Optimization

#### For Many Stocks (10+):
- **Increase update interval** to reduce API calls
- **Monitor network usage** during market hours
- **Consider using during off-market hours** for setup

#### For Lower-End Hardware:
- **Reduce window size** to improve responsiveness
- **Close other applications** to free up memory
- **Use fewer stocks** in watchlist simultaneously

## 📊 Technical Details

### RSI Calculation
The application uses the standard RSI formula:
```
RSI = 100 - (100 / (1 + RS))
Where RS = Average Gain / Average Loss over 14 periods
```

### Data Refresh Strategy
- **Background threading** prevents UI freezing
- **Staggered updates** to avoid API rate limits
- **Intelligent caching** reduces redundant API calls
- **Error recovery** handles network interruptions gracefully

### Security & Privacy
- **No data collection** - all data stays on your device
- **No account required** - works anonymously
- **Local storage only** - watchlist saved locally
- **Read-only access** - no trading capabilities

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Bug Reports
- Use the **Issues** tab to report bugs
- Include **error messages** and **steps to reproduce**
- Specify your **OS and Python version**

### Feature Requests
- Suggest new features in the **Issues** tab
- Explain the **use case** and **expected behavior**
- Consider **implementation complexity**

### Code Contributions
- **Fork** the repository
- **Create feature branch**: `git checkout -b feature-name`
- **Commit changes**: `git commit -m "Add feature"`
- **Push to branch**: `git push origin feature-name`
- **Submit pull request**

### Potential Enhancements
- **Additional indicators** (MACD, Bollinger Bands)
- **Historical charts** and trend visualization
- **Export functionality** for data analysis
- **Alert system** for RSI threshold breaches
- **Portfolio tracking** with multiple watchlists

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for **educational and informational purposes only**. It should not be considered as investment advice. Always:

- **Do your own research** before making investment decisions
- **Consult financial professionals** for investment advice
- **Understand the risks** involved in stock trading
- **Never invest more** than you can afford to lose

**Past performance does not guarantee future results.**

## 🔗 Resources

### Learn More About RSI
- **Investopedia RSI Guide**: Understanding RSI fundamentals
- **TradingView RSI**: Interactive RSI charts and analysis
- **Technical Analysis**: Books on RSI and momentum indicators

### Python Trading Resources
- **yfinance Documentation**: Yahoo Finance Python library
- **pandas**: Data manipulation for financial analysis
- **QuantLib**: Advanced quantitative finance library

---

**Happy Trading! 📈💰**

*Built with ❤️ by [Benggoy](https://github.com/Benggoy) for the trading community*
