#!/usr/bin/env python3
"""
Enhanced Real-Time RSI Stock Tracker
A comprehensive desktop application for tracking RSI and advanced financial metrics.

New Features:
- Market Capitalization
- Daily Volume & Average Volume
- Bid/Ask Prices
- Seeking Alpha Portfolio Integration
- Enhanced UI with more data points

Author: Benggoy
Repository: https://github.com/Benggoy/trading-analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import yfinance as yf
import pandas as pd
import numpy as np
import threading
import time
import webbrowser
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional

class RSICalculator:
    """Calculate RSI (Relative Strength Index) for stock data."""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """
        Calculate RSI for given price series.
        
        Args:
            prices: Series of closing prices
            period: RSI calculation period (default 14)
            
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # Return neutral RSI if insufficient data
        
        # Calculate price changes
        deltas = prices.diff()
        
        # Separate gains and losses
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0

class EnhancedStockData:
    """Handle comprehensive stock data fetching and processing."""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 60  # Cache data for 60 seconds
        self.info_cache = {}
        self.info_cache_timeout = 300  # Cache company info for 5 minutes
    
    def get_stock_data(self, symbol: str, period: str = "5d") -> Optional[pd.DataFrame]:
        """
        Fetch stock data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Data period ('1d', '5d', '1mo', etc.)
            
        Returns:
            DataFrame with stock data or None if error
        """
        cache_key = f"{symbol}_{period}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_timeout:
                return data
        
        try:
            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return None
            
            # Cache the data
            self.cache[cache_key] = (data, current_time)
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_comprehensive_stock_info(self, symbol: str) -> Dict:
        """
        Get comprehensive stock information including market cap, volume, bid/ask.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with comprehensive stock data
        """
        cache_key = f"info_{symbol}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.info_cache:
            info, timestamp = self.info_cache[cache_key]
            if current_time - timestamp < self.info_cache_timeout:
                return info
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get recent price data for volume calculations
            hist_data = self.get_stock_data(symbol, "3mo")
            
            # Extract key information
            stock_info = {
                # Basic price info
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice', 0),
                'previous_close': info.get('previousClose', 0),
                
                # Market data
                'market_cap': info.get('marketCap', 0),
                'daily_volume': info.get('volume') or info.get('regularMarketVolume', 0),
                'avg_volume': info.get('averageVolume') or info.get('averageVolume10days', 0),
                
                # Bid/Ask
                'bid': info.get('bid', 0),
                'ask': info.get('ask', 0),
                'bid_size': info.get('bidSize', 0),
                'ask_size': info.get('askSize', 0),
                
                # Company info
                'company_name': info.get('longName') or info.get('shortName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                
                # Additional metrics
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                
                # Calculate average volume from historical data if not available
                'calculated_avg_volume': 0
            }
            
            # Calculate average volume from historical data if needed
            if hist_data is not None and not hist_data.empty and stock_info['avg_volume'] == 0:
                stock_info['calculated_avg_volume'] = int(hist_data['Volume'].mean())
                stock_info['avg_volume'] = stock_info['calculated_avg_volume']
            
            # Cache the info
            self.info_cache[cache_key] = (stock_info, current_time)
            return stock_info
            
        except Exception as e:
            print(f"Error fetching comprehensive info for {symbol}: {e}")
            return self._get_default_stock_info(symbol)
    
    def _get_default_stock_info(self, symbol: str) -> Dict:
        """Return default stock info structure if API call fails."""
        return {
            'current_price': 0,
            'previous_close': 0,
            'market_cap': 0,
            'daily_volume': 0,
            'avg_volume': 0,
            'bid': 0,
            'ask': 0,
            'bid_size': 0,
            'ask_size': 0,
            'company_name': symbol,
            'sector': 'N/A',
            'industry': 'N/A',
            'pe_ratio': 0,
            'dividend_yield': 0,
            'fifty_two_week_high': 0,
            'fifty_two_week_low': 0,
            'calculated_avg_volume': 0
        }

class EnhancedRSIStockTracker:
    """Enhanced main application class for comprehensive RSI Stock Tracker."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced RSI Stock Tracker - Professional Market Analysis")
        self.root.geometry("1400x800")  # Larger window for more data
        self.root.configure(bg='#1e1e1e')  # Dark theme
        
        # Data handlers
        self.stock_data = EnhancedStockData()
        self.rsi_calculator = RSICalculator()
        
        # Watchlist and portfolio
        self.watchlist = []
        self.portfolio_symbols = []  # For Seeking Alpha integration
        self.watchlist_file = "enhanced_watchlist.json"
        self.portfolio_file = "seeking_alpha_portfolio.json"
        self.load_watchlist()
        self.load_portfolio()
        
        # Update control
        self.update_interval = 30  # seconds
        self.is_updating = False
        self.update_thread = None
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Start updates
        self.start_updates()
        
        # Cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Setup custom styles for the enhanced application."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('Treeview', 
                       background='#2d2d2d', 
                       foreground='white',
                       fieldbackground='#2d2d2d',
                       rowheight=25)
        style.configure('Treeview.Heading',
                       background='#404040',
                       foreground='white',
                       font=('Arial', 9, 'bold'))
        
        # Configure button styles  
        style.configure('Action.TButton',
                       background='#00ff88',
                       foreground='black',
                       font=('Arial', 9, 'bold'))
    
    def setup_ui(self):
        """Setup the enhanced user interface."""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="📈 Enhanced RSI Stock Tracker - Professional Edition", 
                              font=('Arial', 18, 'bold'),
                              bg='#1e1e1e', fg='#00ff88')
        title_label.pack(pady=(0, 10))
        
        # Control frame
        control_frame = tk.Frame(main_frame, bg='#1e1e1e')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side controls
        left_controls = tk.Frame(control_frame, bg='#1e1e1e')
        left_controls.pack(side=tk.LEFT)
        
        # Add stock section
        add_frame = tk.Frame(left_controls, bg='#1e1e1e')
        add_frame.pack(side=tk.LEFT)
        
        tk.Label(add_frame, text="Add Stock:", 
                bg='#1e1e1e', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        self.symbol_entry = tk.Entry(add_frame, width=12, font=('Arial', 10))
        self.symbol_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.symbol_entry.bind('<Return>', self.add_stock_event)
        
        tk.Button(add_frame, text="Add Stock", command=self.add_stock,
                 bg='#00ff88', fg='black', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        # Portfolio section
        portfolio_frame = tk.Frame(left_controls, bg='#1e1e1e')
        portfolio_frame.pack(side=tk.LEFT)
        
        tk.Button(portfolio_frame, text="📊 Add to SA Portfolio", command=self.add_to_portfolio,
                 bg='#4488ff', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(portfolio_frame, text="🔗 View SA Portfolio", command=self.open_seeking_alpha_portfolio,
                 bg='#ff8844', fg='white', font=('Arial', 9)).pack(side=tk.LEFT)
        
        # Right side controls
        right_controls = tk.Frame(control_frame, bg='#1e1e1e')
        right_controls.pack(side=tk.RIGHT)
        
        tk.Button(right_controls, text="Remove Selected", command=self.remove_stock,
                 bg='#ff4444', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(right_controls, text="🔄 Refresh All", command=self.manual_refresh,
                 bg='#44ff44', fg='black', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(right_controls, text="📊 Analysis View", command=self.open_analysis_view,
                 bg='#8844ff', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg='#1e1e1e')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, text="Ready - Enhanced Edition", 
                                    bg='#1e1e1e', fg='#cccccc', font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT)
        
        self.last_update_label = tk.Label(status_frame, text="", 
                                         bg='#1e1e1e', fg='#888888', font=('Arial', 9))
        self.last_update_label.pack(side=tk.RIGHT)
        
        # Enhanced stock data table
        self.setup_enhanced_table(main_frame)
        
        # Enhanced legend
        self.setup_enhanced_legend(main_frame)
    
    def setup_enhanced_table(self, parent):
        """Setup the enhanced stock data table with more columns."""
        # Table frame with horizontal scrollbar
        table_container = tk.Frame(parent, bg='#1e1e1e')
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbars for scrollable table
        canvas = tk.Canvas(table_container, bg='#1e1e1e')
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=canvas.xview)
        
        table_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        # Enhanced columns with more financial data
        columns = ('Symbol', 'Company', 'Price', 'Change', 'Change%', 'RSI', 'Status', 
                  'Market Cap', 'Volume', 'Avg Volume', 'Bid', 'Ask', 'P/E', 'Links', 'Updated')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Define enhanced headings with appropriate widths
        headings = {
            'Symbol': ('Symbol', 80),
            'Company': ('Company', 150),
            'Price': ('Price ($)', 90),
            'Change': ('Change ($)', 90), 
            'Change%': ('Change %', 90),
            'RSI': ('RSI', 60),
            'Status': ('RSI Status', 100),
            'Market Cap': ('Market Cap', 100),
            'Volume': ('Volume', 100),
            'Avg Volume': ('Avg Volume', 100),
            'Bid': ('Bid', 70),
            'Ask': ('Ask', 70),
            'P/E': ('P/E', 60),
            'Links': ('Links', 80),
            'Updated': ('Updated', 80)
        }
        
        for col, (heading, width) in headings.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        # Bind double-click to open stock analysis
        self.tree.bind('<Double-1>', self.on_stock_double_click)
        
        # Pack the treeview
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        canvas.create_window((0, 0), window=table_frame, anchor=tk.NW)
        
        # Pack scrollbars and canvas
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Update scroll region when table size changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        table_frame.bind('<Configure>', configure_scroll_region)
    
    def setup_enhanced_legend(self, parent):
        """Setup enhanced RSI interpretation legend with additional info."""
        legend_frame = tk.Frame(parent, bg='#1e1e1e')
        legend_frame.pack(pady=10)
        
        # RSI Legend
        rsi_legend_frame = tk.Frame(legend_frame, bg='#1e1e1e')
        rsi_legend_frame.pack()
        
        tk.Label(rsi_legend_frame, text="RSI Legend:", 
                bg='#1e1e1e', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        legend_text = "🔴 Overbought (>70) | 🟡 Neutral (30-70) | 🟢 Oversold (<30)"
        tk.Label(rsi_legend_frame, text=legend_text,
                bg='#1e1e1e', fg='#cccccc', font=('Arial', 9)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Additional info
        info_frame = tk.Frame(legend_frame, bg='#1e1e1e')
        info_frame.pack(pady=(5, 0))
        
        info_text = "💡 Double-click any stock for detailed analysis | Market Cap: B=Billion, M=Million | Volume: Daily vs 10-day average"
        tk.Label(info_frame, text=info_text,
                bg='#1e1e1e', fg='#888888', font=('Arial', 8)).pack()
    
    def format_market_cap(self, market_cap: float) -> str:
        """Format market cap in billions/millions."""
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.1f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.1f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.0f}M"
        elif market_cap > 0:
            return f"${market_cap:,.0f}"
        else:
            return "N/A"
    
    def format_volume(self, volume: int) -> str:
        """Format volume in K/M/B."""
        if volume >= 1e9:
            return f"{volume/1e9:.1f}B"
        elif volume >= 1e6:
            return f"{volume/1e6:.1f}M"
        elif volume >= 1e3:
            return f"{volume/1e3:.0f}K"
        elif volume > 0:
            return f"{volume:,}"
        else:
            return "N/A"
    
    def add_stock_event(self, event):
        """Handle Enter key press in symbol entry."""
        self.add_stock()
    
    def add_stock(self):
        """Add a stock to the watchlist with enhanced validation."""
        symbol = self.symbol_entry.get().strip().upper()
        if not symbol:
            return
        
        if symbol in self.watchlist:
            messagebox.showwarning("Duplicate", f"{symbol} is already in your watchlist!")
            return
        
        # Validate symbol by trying to fetch comprehensive data
        self.status_label.config(text=f"Validating {symbol} and fetching comprehensive data...")
        self.root.update()
        
        # Test both historical data and company info
        hist_data = self.stock_data.get_stock_data(symbol, "5d")
        company_info = self.stock_data.get_comprehensive_stock_info(symbol)
        
        if hist_data is None or hist_data.empty:
            messagebox.showerror("Invalid Symbol", f"Could not find historical data for {symbol}")
            self.status_label.config(text="Ready - Enhanced Edition")
            return
        
        if company_info['current_price'] == 0:
            if not messagebox.askyesno("Limited Data", 
                                     f"Limited data available for {symbol}. Add anyway?"):
                self.status_label.config(text="Ready - Enhanced Edition")
                return
        
        # Add to watchlist
        self.watchlist.append(symbol)
        self.symbol_entry.delete(0, tk.END)
        self.save_watchlist()
        
        # Add to table with loading placeholder
        company_name = company_info.get('company_name', symbol)[:20]  # Truncate long names
        self.tree.insert('', tk.END, iid=symbol, values=(
            symbol, company_name, "Loading...", "", "", "", "", "", "", "", "", "", "", "", ""
        ))
        
        # Update display with comprehensive data
        self.update_enhanced_stock_data(symbol)
        self.status_label.config(text=f"Added {symbol} to watchlist with enhanced data")
    
    def add_to_portfolio(self):
        """Add selected stock to Seeking Alpha portfolio tracking."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a stock to add to your SA portfolio")
            return
        
        symbol = selected[0]
        if symbol not in self.portfolio_symbols:
            self.portfolio_symbols.append(symbol)
            self.save_portfolio()
            messagebox.showinfo("Added to Portfolio", 
                              f"{symbol} added to your Seeking Alpha portfolio tracking")
        else:
            messagebox.showinfo("Already in Portfolio", 
                              f"{symbol} is already in your SA portfolio")
    
    def open_seeking_alpha_portfolio(self):
        """Open Seeking Alpha portfolio with tracked symbols."""
        if not self.portfolio_symbols:
            messagebox.showinfo("Empty Portfolio", 
                              "Add some stocks to your SA portfolio first!")
            return
        
        # Create Seeking Alpha portfolio URL
        symbols_string = ",".join(self.portfolio_symbols)
        sa_url = f"https://seekingalpha.com/portfolio/dashboard?symbols={symbols_string}"
        
        try:
            webbrowser.open(sa_url)
            self.status_label.config(text=f"Opened Seeking Alpha portfolio with {len(self.portfolio_symbols)} stocks")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Seeking Alpha: {e}")
    
    def on_stock_double_click(self, event):
        """Handle double-click on stock for detailed analysis."""
        item = self.tree.selection()[0]
        symbol = item
        
        # Create popup menu for analysis options
        popup = tk.Toplevel(self.root)
        popup.title(f"{symbol} - Analysis Options")
        popup.geometry("400x300")
        popup.configure(bg='#1e1e1e')
        
        tk.Label(popup, text=f"📊 {symbol} Analysis Options", 
                font=('Arial', 14, 'bold'), bg='#1e1e1e', fg='#00ff88').pack(pady=10)
        
        # Analysis buttons
        btn_frame = tk.Frame(popup, bg='#1e1e1e')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="🔗 View on Seeking Alpha", 
                 command=lambda: self.open_seeking_alpha_stock(symbol),
                 bg='#ff8844', fg='white', font=('Arial', 10), width=25).pack(pady=5)
        
        tk.Button(btn_frame, text="📈 View on Yahoo Finance", 
                 command=lambda: self.open_yahoo_finance(symbol),
                 bg='#4488ff', fg='white', font=('Arial', 10), width=25).pack(pady=5)
        
        tk.Button(btn_frame, text="📊 View on TradingView", 
                 command=lambda: self.open_tradingview(symbol),
                 bg='#44ff88', fg='black', font=('Arial', 10), width=25).pack(pady=5)
        
        tk.Button(btn_frame, text="📋 Stock Details", 
                 command=lambda: self.show_stock_details(symbol),
                 bg='#8844ff', fg='white', font=('Arial', 10), width=25).pack(pady=5)
        
        tk.Button(btn_frame, text="❌ Close", 
                 command=popup.destroy,
                 bg='#666666', fg='white', font=('Arial', 10), width=25).pack(pady=10)
    
    def open_seeking_alpha_stock(self, symbol: str):
        """Open individual stock on Seeking Alpha."""
        sa_url = f"https://seekingalpha.com/symbol/{symbol}"
        webbrowser.open(sa_url)
    
    def open_yahoo_finance(self, symbol: str):
        """Open stock on Yahoo Finance."""
        yf_url = f"https://finance.yahoo.com/quote/{symbol}"
        webbrowser.open(yf_url)
    
    def open_tradingview(self, symbol: str):
        """Open stock on TradingView."""
        tv_url = f"https://www.tradingview.com/symbols/{symbol}/"
        webbrowser.open(tv_url)
    
    def show_stock_details(self, symbol: str):
        """Show detailed stock information in a popup."""
        info = self.stock_data.get_comprehensive_stock_info(symbol)
        
        # Create details popup
        details = tk.Toplevel(self.root)
        details.title(f"{symbol} - Detailed Information")
        details.geometry("500x600")
        details.configure(bg='#1e1e1e')
        
        # Scrollable text widget
        text_frame = tk.Frame(details, bg='#1e1e1e')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, bg='#2d2d2d', fg='white', 
                             font=('Courier', 10), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Format detailed information
        details_text = f"""
📊 {symbol} - Comprehensive Stock Details
{'='*50}

🏢 Company Information:
   Name: {info.get('company_name', 'N/A')}
   Sector: {info.get('sector', 'N/A')}
   Industry: {info.get('industry', 'N/A')}

💰 Price Information:
   Current Price: ${info.get('current_price', 0):.2f}
   Previous Close: ${info.get('previous_close', 0):.2f}
   52-Week High: ${info.get('fifty_two_week_high', 0):.2f}
   52-Week Low: ${info.get('fifty_two_week_low', 0):.2f}

📈 Market Data:
   Market Cap: {self.format_market_cap(info.get('market_cap', 0))}
   P/E Ratio: {info.get('pe_ratio', 0):.2f if info.get('pe_ratio', 0) > 0 else 'N/A'}
   Dividend Yield: {info.get('dividend_yield', 0)*100:.2f}% if info.get('dividend_yield', 0) > 0 else 'N/A'

📊 Trading Information:
   Bid: ${info.get('bid', 0):.2f} (Size: {info.get('bid_size', 0):,})
   Ask: ${info.get('ask', 0):.2f} (Size: {info.get('ask_size', 0):,})
   
   Daily Volume: {self.format_volume(info.get('daily_volume', 0))}
   Average Volume: {self.format_volume(info.get('avg_volume', 0))}
   Volume Ratio: {info.get('daily_volume', 0) / max(info.get('avg_volume', 1), 1):.2f}x

🔗 Quick Links:
   • Seeking Alpha: seekingalpha.com/symbol/{symbol}
   • Yahoo Finance: finance.yahoo.com/quote/{symbol}
   • TradingView: tradingview.com/symbols/{symbol}/

⏰ Data refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        text_widget.insert(tk.END, details_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def open_analysis_view(self):
        """Open a summary analysis view of all stocks."""
        if not self.watchlist:
            messagebox.showinfo("Empty Watchlist", "Add some stocks to analyze!")
            return
        
        # Create analysis window
        analysis = tk.Toplevel(self.root)
        analysis.title("Portfolio Analysis Summary")
        analysis.geometry("800x600")
        analysis.configure(bg='#1e1e1e')
        
        tk.Label(analysis, text="📊 Portfolio Analysis Summary", 
                font=('Arial', 16, 'bold'), bg='#1e1e1e', fg='#00ff88').pack(pady=10)
        
        # Create analysis content
        analysis_frame = tk.Frame(analysis, bg='#1e1e1e')
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Summary statistics
        overbought_count = 0
        oversold_count = 0
        neutral_count = 0
        total_market_cap = 0
        
        for symbol in self.watchlist:
            try:
                # Get RSI from current display
                for item in self.tree.get_children():
                    if item == symbol:
                        values = self.tree.item(item)['values']
                        if len(values) > 5:
                            rsi_str = str(values[5])
                            if rsi_str.replace('.', '').isdigit():
                                rsi = float(rsi_str)
                                if rsi > 70:
                                    overbought_count += 1
                                elif rsi < 30:
                                    oversold_count += 1
                                else:
                                    neutral_count += 1
                        break
                
                # Add market cap
                info = self.stock_data.get_comprehensive_stock_info(symbol)
                total_market_cap += info.get('market_cap', 0)
            except:
                pass
        
        summary_text = f"""
📈 RSI Distribution:
   🔴 Overbought (>70): {overbought_count} stocks
   🟡 Neutral (30-70): {neutral_count} stocks  
   🟢 Oversold (<30): {oversold_count} stocks
   
📊 Portfolio Overview:
   Total Stocks: {len(self.watchlist)}
   Combined Market Cap: {self.format_market_cap(total_market_cap)}
   Seeking Alpha Portfolio: {len(self.portfolio_symbols)} stocks tracked
   
💡 Recommendations:
   • Review overbought stocks for profit-taking opportunities
   • Consider oversold stocks for potential buying opportunities
   • Monitor neutral stocks for trend changes
   • Diversify across different RSI categories
        """
        
        text_widget = tk.Text(analysis_frame, bg='#2d2d2d', fg='white', 
                             font=('Courier', 12), wrap=tk.WORD, height=20)
        text_widget.insert(tk.END, summary_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
    
    def remove_stock(self):
        """Remove selected stock from watchlist."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a stock to remove")
            return
        
        symbol = selected[0]
        if messagebox.askyesno("Confirm Remove", f"Remove {symbol} from watchlist?"):
            self.watchlist.remove(symbol)
            self.tree.delete(symbol)
            
            # Also remove from portfolio if present
            if symbol in self.portfolio_symbols:
                self.portfolio_symbols.remove(symbol)
                self.save_portfolio()
            
            self.save_watchlist()
            self.status_label.config(text=f"Removed {symbol} from watchlist and portfolio")
    
    def manual_refresh(self):
        """Manually refresh all stock data with enhanced information."""
        if not self.watchlist:
            messagebox.showinfo("Empty Watchlist", "Add some stocks to your watchlist first!")
            return
        
        self.status_label.config(text="Refreshing all stocks with enhanced data...")
        threading.Thread(target=self.refresh_all_enhanced_stocks, daemon=True).start()
    
    def refresh_all_enhanced_stocks(self):
        """Refresh enhanced data for all stocks in watchlist."""
        for i, symbol in enumerate(self.watchlist):
            self.root.after(0, lambda s=symbol, idx=i: self.status_label.config(
                text=f"Refreshing {s}... ({idx+1}/{len(self.watchlist)})"
            ))
            self.update_enhanced_stock_data(symbol)
            time.sleep(1)  # Avoid rate limiting
        
        self.root.after(0, lambda: self.status_label.config(text="All stocks updated with enhanced data"))
    
    def update_enhanced_stock_data(self, symbol: str):
        """Update comprehensive data for a specific stock."""
        # Get historical data for RSI calculation
        hist_data = self.stock_data.get_stock_data(symbol, "1mo")
        # Get comprehensive company information
        company_info = self.stock_data.get_comprehensive_stock_info(symbol)
        
        if hist_data is None or hist_data.empty:
            self.root.after(0, lambda: self.update_enhanced_table_row(
                symbol, "Error", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "🔗", "Error"
            ))
            return
        
        try:
            # Calculate price metrics
            current_price = company_info.get('current_price', 0)
            previous_price = company_info.get('previous_close', 0)
            
            if current_price == 0 and len(hist_data) > 0:
                current_price = float(hist_data['Close'].iloc[-1])
            if previous_price == 0 and len(hist_data) > 1:
                previous_price = float(hist_data['Close'].iloc[-2])
            
            price_change = current_price - previous_price
            percent_change = (price_change / previous_price) * 100 if previous_price != 0 else 0
            
            # Calculate RSI
            rsi = self.rsi_calculator.calculate_rsi(hist_data['Close'])
            
            # Determine RSI status
            if rsi > 70:
                rsi_status = "🔴 Overbought"
            elif rsi < 30:
                rsi_status = "🟢 Oversold"
            else:
                rsi_status = "🟡 Neutral"
            
            # Format all values
            company_name = company_info.get('company_name', symbol)[:15]  # Truncate
            price_str = f"${current_price:.2f}"
            change_str = f"${price_change:+.2f}"
            percent_str = f"{percent_change:+.2f}%"
            rsi_str = f"{rsi:.1f}"
            market_cap_str = self.format_market_cap(company_info.get('market_cap', 0))
            volume_str = self.format_volume(company_info.get('daily_volume', 0))
            avg_volume_str = self.format_volume(company_info.get('avg_volume', 0))
            bid_str = f"${company_info.get('bid', 0):.2f}"
            ask_str = f"${company_info.get('ask', 0):.2f}"
            pe_str = f"{company_info.get('pe_ratio', 0):.1f}" if company_info.get('pe_ratio', 0) > 0 else "N/A"
            updated_str = datetime.now().strftime("%H:%M")
            
            # Update table in main thread
            self.root.after(0, lambda: self.update_enhanced_table_row(
                symbol, company_name, price_str, change_str, percent_str, rsi_str, rsi_status,
                market_cap_str, volume_str, avg_volume_str, bid_str, ask_str, pe_str, "🔗", updated_str
            ))
            
        except Exception as e:
            print(f"Error updating enhanced data for {symbol}: {e}")
            self.root.after(0, lambda: self.update_enhanced_table_row(
                symbol, "Error", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "🔗", "Error"
            ))
    
    def update_enhanced_table_row(self, symbol: str, company: str, price: str, change: str, 
                                 percent: str, rsi: str, status: str, market_cap: str, 
                                 volume: str, avg_volume: str, bid: str, ask: str, 
                                 pe: str, links: str, updated: str):
        """Update a row in the enhanced stock table."""
        try:
            self.tree.item(symbol, values=(
                symbol, company, price, change, percent, rsi, status,
                market_cap, volume, avg_volume, bid, ask, pe, links, updated
            ))
        except tk.TclError:
            pass  # Item might have been deleted
    
    def start_updates(self):
        """Start automatic updates for enhanced data."""
        if not self.is_updating:
            self.is_updating = True
            self.update_thread = threading.Thread(target=self.enhanced_update_loop, daemon=True)
            self.update_thread.start()
    
    def enhanced_update_loop(self):
        """Enhanced update loop running in background."""
        while self.is_updating:
            if self.watchlist:
                self.root.after(0, lambda: self.status_label.config(text="Updating enhanced stock data..."))
                
                for symbol in self.watchlist.copy():
                    if not self.is_updating:
                        break
                    self.update_enhanced_stock_data(symbol)
                    time.sleep(2)  # Slightly longer delay for comprehensive data
                
                current_time = datetime.now().strftime("%H:%M:%S")
                self.root.after(0, lambda: self.last_update_label.config(text=f"Last update: {current_time}"))
                self.root.after(0, lambda: self.status_label.config(text="Ready - Enhanced Edition"))
            
            # Wait before next update cycle
            time.sleep(self.update_interval)
    
    def load_watchlist(self):
        """Load enhanced watchlist from file."""
        try:
            if os.path.exists(self.watchlist_file):
                with open(self.watchlist_file, 'r') as f:
                    data = json.load(f)
                    self.watchlist = data.get('watchlist', [])
        except Exception as e:
            print(f"Error loading enhanced watchlist: {e}")
            self.watchlist = []
    
    def save_watchlist(self):
        """Save enhanced watchlist to file."""
        try:
            data = {
                'watchlist': self.watchlist,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.watchlist_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving enhanced watchlist: {e}")
    
    def load_portfolio(self):
        """Load Seeking Alpha portfolio symbols."""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    data = json.load(f)
                    self.portfolio_symbols = data.get('portfolio', [])
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            self.portfolio_symbols = []
    
    def save_portfolio(self):
        """Save Seeking Alpha portfolio symbols."""
        try:
            data = {
                'portfolio': self.portfolio_symbols,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.portfolio_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving portfolio: {e}")
    
    def populate_initial_data(self):
        """Populate table with saved watchlist and enhanced data."""
        for symbol in self.watchlist:
            self.tree.insert('', tk.END, iid=symbol, values=(
                symbol, "Loading...", "Loading...", "", "", "", "", "", "", "", "", "", "", "🔗", ""
            ))
    
    def on_closing(self):
        """Handle application closing."""
        self.is_updating = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2)
        self.root.destroy()
    
    def run(self):
        """Run the enhanced application."""
        # Populate with saved stocks
        self.populate_initial_data()
        
        # Show instructions if empty
        if not self.watchlist:
            self.status_label.config(text="Add stock symbols (e.g., AAPL, GOOGL, TSLA) to start enhanced tracking")
        
        # Start the GUI
        self.root.mainloop()

def main():
    """Main function to run the Enhanced RSI Stock Tracker."""
    try:
        app = EnhancedRSIStockTracker()
        app.run()
    except Exception as e:
        print(f"Error starting enhanced application: {e}")
        messagebox.showerror("Error", f"Failed to start enhanced application: {e}")

if __name__ == "__main__":
    main()
