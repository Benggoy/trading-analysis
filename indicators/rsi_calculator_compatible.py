#!/usr/bin/env python3
"""
RSI Calculator - Compatible Version
==================================
Fixed for all Python 3.x versions without type hints
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class RSICalculator:
    """RSI Calculator with comprehensive analysis capabilities"""
    
    def __init__(self, period=14):
        """Initialize RSI Calculator"""
        self.period = period
        self.overbought_level = 70
        self.oversold_level = 30
        
    def calculate_rsi(self, data):
        """Calculate RSI for given price data"""
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
    
    def get_stock_data(self, symbol, period="1y"):
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def analyze_stock(self, symbol):
        """Analyze a single stock and return RSI analysis"""
        print(f"\n📊 Analyzing {symbol.upper()}...")
        
        # Get data
        data = self.get_stock_data(symbol, period="6mo")
        if data.empty:
            print(f"❌ No data available for {symbol}")
            return None
            
        # Calculate RSI
        rsi = self.calculate_rsi(data['Close'])
        current_rsi = rsi.iloc[-1]
        current_price = data['Close'].iloc[-1]
        
        # Determine signal
        if current_rsi > self.overbought_level:
            signal = "🔴 OVERBOUGHT"
            recommendation = "Consider selling"
        elif current_rsi < self.oversold_level:
            signal = "🟢 OVERSOLD"
            recommendation = "Consider buying"
        else:
            signal = "🟡 NEUTRAL"
            recommendation = "Hold or wait"
            
        # Print results
        print(f"💰 Current Price: ${current_price:.2f}")
        print(f"📈 RSI({self.period}): {current_rsi:.2f}")
        print(f"🚦 Signal: {signal}")
        print(f"💡 Recommendation: {recommendation}")
        
        return {
            'symbol': symbol.upper(),
            'price': current_price,
            'rsi': current_rsi,
            'signal': signal,
            'recommendation': recommendation
        }
    
    def analyze_multiple_stocks(self, symbols):
        """Analyze multiple stocks"""
        results = []
        
        print("🚀 RSI Analysis Starting...")
        print("=" * 50)
        
        for symbol in symbols:
            try:
                result = self.analyze_stock(symbol)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
                
        # Summary
        if results:
            print("\n📋 SUMMARY:")
            print("-" * 30)
            for result in results:
                print(f"{result['symbol']}: RSI {result['rsi']:.2f} - {result['signal'].split()[1]}")
                
        return results

def main():
    """Example usage"""
    print("🎯 RSI Trading Analysis Tool")
    print("=" * 40)
    
    # Initialize calculator
    rsi_calc = RSICalculator(period=14)
    
    # Test with popular stocks
    test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    
    try:
        results = rsi_calc.analyze_multiple_stocks(test_symbols)
        
        print(f"\n✅ Analysis completed for {len(results)} stocks!")
        print("\n💡 Tips:")
        print("- RSI > 70: Potentially overbought (consider selling)")
        print("- RSI < 30: Potentially oversold (consider buying)")
        print("- RSI 30-70: Neutral territory")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("Check your internet connection and try again.")

if __name__ == "__main__":
    main()
