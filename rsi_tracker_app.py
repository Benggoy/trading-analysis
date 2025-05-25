#!/usr/bin/env python3
"""
Real-Time RSI Stock Tracker
A desktop application for tracking RSI of selected stocks in real-time.

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

class StockData:
    """Handle stock data fetching and processing."""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 60  # Cache data for 60 seconds
    
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
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except:
            # Fallback to recent close price
            data = self.get_stock_data(symbol, "1d")
            if data is not None and not data.empty:
                return float(data['Close'].iloc[-1])
            return None

class RSIStockTracker:
    """Main application class for RSI Stock Tracker."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RSI Stock Tracker - Real-Time Market Analysis")
        self.root.geometry("900x600")
        self.root.configure(bg='#1e1e1e')  # Dark theme
        
        # Data handlers
        self.stock_data = StockData()
        self.rsi_calculator = RSICalculator()
        
        # Watchlist
        self.watchlist = []
        self.watchlist_file = "watchlist.json"
        self.load_watchlist()
        
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
        """Setup custom styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('Treeview', 
                       background='#2d2d2d', 
                       foreground='white',
                       fieldbackground='#2d2d2d')
        style.configure('Treeview.Heading',
                       background='#404040',
                       foreground='white')
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="📈 Real-Time RSI Stock Tracker", 
                              font=('Arial', 16, 'bold'),
                              bg='#1e1e1e', fg='#00ff88')
        title_label.pack(pady=(0, 10))
        
        # Control frame
        control_frame = tk.Frame(main_frame, bg='#1e1e1e')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add stock section
        add_frame = tk.Frame(control_frame, bg='#1e1e1e')
        add_frame.pack(side=tk.LEFT)
        
        tk.Label(add_frame, text="Add Stock:", 
                bg='#1e1e1e', fg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.symbol_entry = tk.Entry(add_frame, width=10, font=('Arial', 10))
        self.symbol_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.symbol_entry.bind('<Return>', self.add_stock_event)
        
        tk.Button(add_frame, text="Add", command=self.add_stock,
                 bg='#00ff88', fg='black', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#1e1e1e')
        button_frame.pack(side=tk.RIGHT)
        
        tk.Button(button_frame, text="Remove Selected", command=self.remove_stock,
                 bg='#ff4444', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Refresh Now", command=self.manual_refresh,
                 bg='#4488ff', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg='#1e1e1e')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    bg='#1e1e1e', fg='#cccccc', font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        self.last_update_label = tk.Label(status_frame, text="", 
                                         bg='#1e1e1e', fg='#888888', font=('Arial', 9))
        self.last_update_label.pack(side=tk.RIGHT)
        
        # Stock data table
        self.setup_table(main_frame)
        
        # Legend
        self.setup_legend(main_frame)
    
    def setup_table(self, parent):
        """Setup the stock data table."""
        # Table frame
        table_frame = tk.Frame(parent, bg='#1e1e1e')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for stock data
        columns = ('Symbol', 'Price', 'Change', 'Change%', 'RSI', 'Status', 'Updated')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        headings = {
            'Symbol': ('Stock', 80),
            'Price': ('Price ($)', 100),
            'Change': ('Change ($)', 100), 
            'Change%': ('Change %', 100),
            'RSI': ('RSI', 80),
            'Status': ('RSI Status', 120),
            'Updated': ('Last Updated', 120)
        }
        
        for col, (heading, width) in headings.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_legend(self, parent):
        """Setup RSI interpretation legend."""
        legend_frame = tk.Frame(parent, bg='#1e1e1e')
        legend_frame.pack(pady=10)
        
        tk.Label(legend_frame, text="RSI Legend:", 
                bg='#1e1e1e', fg='white', font=('Arial', 10, 'bold')).pack()
        
        legend_text = "🔴 Overbought (>70)  🟡 Neutral (30-70)  🟢 Oversold (<30)"
        tk.Label(legend_frame, text=legend_text,
                bg='#1e1e1e', fg='#cccccc', font=('Arial', 9)).pack()
    
    def add_stock_event(self, event):
        """Handle Enter key press in symbol entry."""
        self.add_stock()
    
    def add_stock(self):
        """Add a stock to the watchlist."""
        symbol = self.symbol_entry.get().strip().upper()
        if not symbol:
            return
        
        if symbol in self.watchlist:
            messagebox.showwarning("Duplicate", f"{symbol} is already in your watchlist!")
            return
        
        # Validate symbol by trying to fetch data
        self.status_label.config(text=f"Validating {symbol}...")
        self.root.update()
        
        data = self.stock_data.get_stock_data(symbol, "5d")
        if data is None or data.empty:
            messagebox.showerror("Invalid Symbol", f"Could not find data for {symbol}")
            self.status_label.config(text="Ready")
            return
        
        # Add to watchlist
        self.watchlist.append(symbol)
        self.symbol_entry.delete(0, tk.END)
        self.save_watchlist()
        
        # Add to table
        self.tree.insert('', tk.END, iid=symbol, values=(symbol, "Loading...", "", "", "", "", ""))
        
        # Update display
        self.update_stock_data(symbol)
        self.status_label.config(text=f"Added {symbol} to watchlist")
    
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
            self.save_watchlist()
            self.status_label.config(text=f"Removed {symbol} from watchlist")
    
    def manual_refresh(self):
        """Manually refresh all stock data."""
        if not self.watchlist:
            messagebox.showinfo("Empty Watchlist", "Add some stocks to your watchlist first!")
            return
        
        self.status_label.config(text="Refreshing all stocks...")
        threading.Thread(target=self.refresh_all_stocks, daemon=True).start()
    
    def refresh_all_stocks(self):
        """Refresh data for all stocks in watchlist."""
        for symbol in self.watchlist:
            self.update_stock_data(symbol)
            time.sleep(0.5)  # Avoid rate limiting
        
        self.root.after(0, lambda: self.status_label.config(text="All stocks updated"))
    
    def update_stock_data(self, symbol: str):
        """Update data for a specific stock."""
        data = self.stock_data.get_stock_data(symbol, "1mo")  # Get more data for RSI
        if data is None or data.empty:
            self.root.after(0, lambda: self.update_table_row(symbol, "Error", "N/A", "N/A", "N/A", "N/A", "Error"))
            return
        
        try:
            # Calculate current values
            current_price = float(data['Close'].iloc[-1])
            previous_price = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price
            price_change = current_price - previous_price
            percent_change = (price_change / previous_price) * 100 if previous_price != 0 else 0
            
            # Calculate RSI
            rsi = self.rsi_calculator.calculate_rsi(data['Close'])
            
            # Determine RSI status and color
            if rsi > 70:
                rsi_status = "🔴 Overbought"
            elif rsi < 30:
                rsi_status = "🟢 Oversold"
            else:
                rsi_status = "🟡 Neutral"
            
            # Format values
            price_str = f"${current_price:.2f}"
            change_str = f"${price_change:+.2f}"
            percent_str = f"{percent_change:+.2f}%"
            rsi_str = f"{rsi:.1f}"
            updated_str = datetime.now().strftime("%H:%M:%S")
            
            # Update table in main thread
            self.root.after(0, lambda: self.update_table_row(
                symbol, price_str, change_str, percent_str, rsi_str, rsi_status, updated_str
            ))
            
        except Exception as e:
            print(f"Error updating {symbol}: {e}")
            self.root.after(0, lambda: self.update_table_row(symbol, "Error", "N/A", "N/A", "N/A", "N/A", "Error"))
    
    def update_table_row(self, symbol: str, price: str, change: str, percent: str, rsi: str, status: str, updated: str):
        """Update a row in the stock table."""
        try:
            self.tree.item(symbol, values=(symbol, price, change, percent, rsi, status, updated))
            
            # Color coding based on change
            if "+" in change:
                self.tree.set(symbol, 'Change', change)
                self.tree.set(symbol, 'Change%', percent)
            elif "-" in change:
                self.tree.set(symbol, 'Change', change)
                self.tree.set(symbol, 'Change%', percent)
                
        except tk.TclError:
            pass  # Item might have been deleted
    
    def start_updates(self):
        """Start automatic updates."""
        if not self.is_updating:
            self.is_updating = True
            self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
            self.update_thread.start()
    
    def update_loop(self):
        """Main update loop running in background."""
        while self.is_updating:
            if self.watchlist:
                self.root.after(0, lambda: self.status_label.config(text="Updating stocks..."))
                
                for symbol in self.watchlist.copy():  # Use copy to avoid modification during iteration
                    if not self.is_updating:
                        break
                    self.update_stock_data(symbol)
                    time.sleep(1)  # Rate limiting
                
                current_time = datetime.now().strftime("%H:%M:%S")
                self.root.after(0, lambda: self.last_update_label.config(text=f"Last update: {current_time}"))
                self.root.after(0, lambda: self.status_label.config(text="Ready"))
            
            # Wait before next update cycle
            time.sleep(self.update_interval)
    
    def load_watchlist(self):
        """Load watchlist from file."""
        try:
            if os.path.exists(self.watchlist_file):
                with open(self.watchlist_file, 'r') as f:
                    self.watchlist = json.load(f)
        except Exception as e:
            print(f"Error loading watchlist: {e}")
            self.watchlist = []
    
    def save_watchlist(self):
        """Save watchlist to file."""
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(self.watchlist, f)
        except Exception as e:
            print(f"Error saving watchlist: {e}")
    
    def populate_initial_data(self):
        """Populate table with saved watchlist."""
        for symbol in self.watchlist:
            self.tree.insert('', tk.END, iid=symbol, values=(symbol, "Loading...", "", "", "", "", ""))
    
    def on_closing(self):
        """Handle application closing."""
        self.is_updating = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        self.root.destroy()
    
    def run(self):
        """Run the application."""
        # Populate with saved stocks
        self.populate_initial_data()
        
        # Show instructions if empty
        if not self.watchlist:
            self.status_label.config(text="Add stock symbols (e.g., AAPL, GOOGL, TSLA) to start tracking")
        
        # Start the GUI
        self.root.mainloop()

def main():
    """Main function to run the RSI Stock Tracker."""
    try:
        app = RSIStockTracker()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
