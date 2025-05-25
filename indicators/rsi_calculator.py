#!/usr/bin/env python3
"""
RSI (Relative Strength Index) Calculator
========================================

A comprehensive RSI calculation tool with multiple timeframes, 
signal detection, and visualization capabilities.

Author: Benggoy
License: MIT
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Union, Tuple, List, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RSICalculator:
    """
    Advanced RSI Calculator with multiple features:
    - Multiple timeframe analysis
    - Divergence detection
    - Signal generation
    - Visualization tools
    """
    
    def __init__(self, period: int = 14):
        """
        Initialize RSI Calculator
        
        Args:
            period (int): RSI calculation period (default: 14)
        """
        self.period = period
        self.overbought_level = 70
        self.oversold_level = 30
        
    def calculate_rsi(self, data: Union[pd.Series, List[float]]) -> pd.Series:
        """
        Calculate RSI for given price data
        
        Args:
            data: Price data (closing prices)
            
        Returns:
            pd.Series: RSI values
        """
        if isinstance(data, list):
            data = pd.Series(data)
            
        # Calculate price changes
        delta = data.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss using EMA
        avg_gain = gain.ewm(span=self.period, adjust=False).mean()
        avg_loss = loss.ewm(span=self.period, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetch stock data from Yahoo Finance
        
        Args:
            symbol (str): Stock ticker symbol
            period (str): Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            
        Returns:
            pd.DataFrame: Stock data with OHLCV
        """
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def analyze_multiple_timeframes(self, symbol: str, periods: List[int] = [14, 21, 50]) -> pd.DataFrame:
        """
        Calculate RSI for multiple timeframes
        
        Args:
            symbol (str): Stock ticker
            periods (List[int]): List of RSI periods to calculate
            
        Returns:
            pd.DataFrame: DataFrame with RSI for different periods
        """
        data = self.get_stock_data(symbol)
        if data.empty:
            return pd.DataFrame()
            
        results = data[['Close']].copy()
        
        for period in periods:
            temp_calculator = RSICalculator(period)
            results[f'RSI_{period}'] = temp_calculator.calculate_rsi(data['Close'])
            
        return results
    
    def detect_signals(self, rsi: pd.Series) -> pd.DataFrame:
        """
        Detect buy/sell signals based on RSI levels
        
        Args:
            rsi (pd.Series): RSI values
            
        Returns:
            pd.DataFrame: Signals dataframe
        """
        signals = pd.DataFrame(index=rsi.index)
        signals['RSI'] = rsi
        signals['Signal'] = 'HOLD'
        
        # Buy signals (oversold)
        signals.loc[rsi < self.oversold_level, 'Signal'] = 'BUY'
        
        # Sell signals (overbought)  
        signals.loc[rsi > self.overbought_level, 'Signal'] = 'SELL'
        
        # Signal changes
        signals['Signal_Change'] = signals['Signal'] != signals['Signal'].shift(1)
        
        return signals
    
    def detect_divergence(self, prices: pd.Series, rsi: pd.Series, window: int = 20) -> pd.DataFrame:
        """
        Detect bullish and bearish divergences
        
        Args:
            prices (pd.Series): Price data
            rsi (pd.Series): RSI values
            window (int): Lookback window for divergence detection
            
        Returns:
            pd.DataFrame: Divergence signals
        """
        divergence = pd.DataFrame(index=prices.index)
        divergence['Price'] = prices
        divergence['RSI'] = rsi
        divergence['Divergence'] = 'NONE'
        
        # Rolling windows for trend analysis
        price_trend = prices.rolling(window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        rsi_trend = rsi.rolling(window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        
        # Bullish divergence: price falling, RSI rising
        bullish_div = (price_trend < 0) & (rsi_trend > 0) & (rsi < 40)
        divergence.loc[bullish_div, 'Divergence'] = 'BULLISH'
        
        # Bearish divergence: price rising, RSI falling
        bearish_div = (price_trend > 0) & (rsi_trend < 0) & (rsi > 60)
        divergence.loc[bearish_div, 'Divergence'] = 'BEARISH'
        
        return divergence
    
    def plot_rsi_analysis(self, symbol: str, period: str = "6mo"):
        """
        Create comprehensive RSI analysis chart
        
        Args:
            symbol (str): Stock ticker
            period (str): Time period for analysis
        """
        # Get data
        data = self.get_stock_data(symbol, period)
        if data.empty:
            print(f"No data available for {symbol}")
            return
            
        # Calculate RSI
        rsi = self.calculate_rsi(data['Close'])
        signals = self.detect_signals(rsi)
        divergence = self.detect_divergence(data['Close'], rsi)
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
        
        # Price chart
        ax1.plot(data.index, data['Close'], label=f'{symbol} Price', linewidth=2)
        ax1.set_title(f'{symbol} - Price and RSI Analysis', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Add buy/sell signals on price chart
        buy_signals = signals[signals['Signal'] == 'BUY']
        sell_signals = signals[signals['Signal'] == 'SELL']
        
        if not buy_signals.empty:
            ax1.scatter(buy_signals.index, data.loc[buy_signals.index, 'Close'], 
                       color='green', marker='^', s=100, label='Buy Signal', zorder=5)
                       
        if not sell_signals.empty:
            ax1.scatter(sell_signals.index, data.loc[sell_signals.index, 'Close'], 
                       color='red', marker='v', s=100, label='Sell Signal', zorder=5)
        
        # RSI chart
        ax2.plot(rsi.index, rsi, label=f'RSI({self.period})', linewidth=2, color='purple')
        ax2.axhline(y=self.overbought_level, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
        ax2.axhline(y=self.oversold_level, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
        ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
        ax2.fill_between(rsi.index, self.oversold_level, rsi, where=(rsi < self.oversold_level), 
                        color='green', alpha=0.2, label='Oversold Zone')
        ax2.fill_between(rsi.index, self.overbought_level, rsi, where=(rsi > self.overbought_level), 
                        color='red', alpha=0.2, label='Overbought Zone')
        
        ax2.set_ylabel('RSI', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
        
        # Print summary statistics
        self.print_summary_stats(symbol, data, rsi, signals)
    
    def print_summary_stats(self, symbol: str, data: pd.DataFrame, rsi: pd.Series, signals: pd.DataFrame):
        """Print summary statistics and analysis"""
        
        print(f"\n{'='*60}")
        print(f"RSI ANALYSIS SUMMARY FOR {symbol.upper()}")
        print(f"{'='*60}")
        print(f"Analysis Period: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"RSI Period: {self.period} days")
        print(f"\n📊 CURRENT STATUS:")
        print(f"Current Price: ${data['Close'].iloc[-1]:.2f}")
        print(f"Current RSI: {rsi.iloc[-1]:.2f}")
        
        current_signal = signals['Signal'].iloc[-1]
        print(f"Current Signal: {current_signal}")
        
        if current_signal == 'BUY':
            print("🟢 RSI indicates potential buying opportunity (oversold)")
        elif current_signal == 'SELL':
            print("🔴 RSI indicates potential selling opportunity (overbought)")
        else:
            print("🟡 RSI is in neutral territory")
            
        print(f"\n📈 RSI STATISTICS:")
        print(f"Average RSI: {rsi.mean():.2f}")
        print(f"RSI Standard Deviation: {rsi.std():.2f}")
        print(f"Times Overbought (>70): {(rsi > 70).sum()} ({(rsi > 70).mean()*100:.1f}%)")
        print(f"Times Oversold (<30): {(rsi < 30).sum()} ({(rsi < 30).mean()*100:.1f}%)")
        
        print(f"\n🎯 SIGNAL SUMMARY:")
        buy_count = (signals['Signal'] == 'BUY').sum()
        sell_count = (signals['Signal'] == 'SELL').sum()
        print(f"Buy Signals Generated: {buy_count}")
        print(f"Sell Signals Generated: {sell_count}")
        
        print(f"{'='*60}")

def main():
    """Example usage of RSI Calculator"""
    
    # Initialize calculator
    rsi_calc = RSICalculator(period=14)
    
    # Example stocks to analyze
    symbols = ['AAPL', 'TSLA', 'SPY']
    
    print("🚀 RSI Analysis Tool")
    print("="*50)
    
    for symbol in symbols:
        print(f"\n📈 Analyzing {symbol}...")
        try:
            # Plot analysis
            rsi_calc.plot_rsi_analysis(symbol)
            
            # Multi-timeframe analysis
            multi_rsi = rsi_calc.analyze_multiple_timeframes(symbol, [14, 21, 50])
            if not multi_rsi.empty:
                print(f"\n📊 Multi-timeframe RSI for {symbol}:")
                print(multi_rsi.tail().round(2))
                
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
