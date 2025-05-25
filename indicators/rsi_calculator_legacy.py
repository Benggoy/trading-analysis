#!/usr/bin/env python3
"""
RSI Calculator - Maximum Compatibility Version
==============================================
Works with Python 3.x versions (no f-strings, no type hints)
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
            print("Error fetching data for {}: {}".format(symbol, str(e)))
            return pd.DataFrame()
    
    def analyze_stock(self, symbol):
        """Analyze a single stock and return RSI analysis"""
        print("\n📊 Analyzing {}...".format(symbol.upper()))
        
        # Get data
        data = self.get_stock_data(symbol, period="6mo")
        if data.empty:
            print("❌ No data available for {}".format(symbol))
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
        print("💰 Current Price: ${:.2f}".format(current_price))
        print("📈 RSI({}): {:.2f}".format(self.period, current_rsi))
        print("🚦 Signal: {}".format(signal))
        print("💡 Recommendation: {}".format(recommendation))
        
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
                print("❌ Error analyzing {}: {}".format(symbol, str(e)))
                
        # Summary
        if results:
            print("\n📋 SUMMARY:")
            print("-" * 30)
            for result in results:
                print("{}: RSI {:.2f} - {}".format(
                    result['symbol'], 
                    result['rsi'], 
                    result['signal'].split()[1]
                ))
                
        return results

def main():
    """Example usage"""
    print("🎯 RSI Trading Analysis Tool")
    print("=" * 40)
    
    # Initialize calculator
    rsi_calc = RSICalculator(period=14)
    
    # Test with popular stocks
    test_symbols = ['AAPL', 'GOOGL', 'MSFT']
    
    try:
        results = rsi_calc.analyze_multiple_stocks(test_symbols)
        
        print("\n✅ Analysis completed for {} stocks!".format(len(results)))
        print("\n💡 Tips:")
        print("- RSI > 70: Potentially overbought (consider selling)")
        print("- RSI < 30: Potentially oversold (consider buying)")
        print("- RSI 30-70: Neutral territory")
        
    except Exception as e:
        print("❌ Error during analysis: {}".format(str(e)))
        print("Check your internet connection and try again.")

if __name__ == "__main__":
    main()
