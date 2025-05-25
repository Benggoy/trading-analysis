# -*- coding: utf-8 -*-
"""
RSI Calculator - Simple ASCII Version
====================================
Basic RSI calculator without emojis - maximum compatibility
"""

import pandas as pd
import numpy as np
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

class RSICalculator:
    """RSI Calculator - Simple version"""
    
    def __init__(self, period=14):
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
        
        # Calculate average gain and loss
        avg_gain = gain.ewm(span=self.period, adjust=False).mean()
        avg_loss = loss.ewm(span=self.period, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_stock_data(self, symbol, period="6mo"):
        """Fetch stock data"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data
        except Exception as e:
            print("Error fetching data for {}: {}".format(symbol, str(e)))
            return pd.DataFrame()
    
    def analyze_stock(self, symbol):
        """Analyze a single stock"""
        print("\nAnalyzing {}...".format(symbol.upper()))
        
        # Get data
        data = self.get_stock_data(symbol)
        if data.empty:
            print("No data available for {}".format(symbol))
            return None
            
        # Calculate RSI
        rsi = self.calculate_rsi(data['Close'])
        current_rsi = rsi.iloc[-1]
        current_price = data['Close'].iloc[-1]
        
        # Determine signal
        if current_rsi > self.overbought_level:
            signal = "OVERBOUGHT"
            recommendation = "Consider selling"
        elif current_rsi < self.oversold_level:
            signal = "OVERSOLD"
            recommendation = "Consider buying"
        else:
            signal = "NEUTRAL"
            recommendation = "Hold or wait"
            
        # Print results
        print("Current Price: ${:.2f}".format(current_price))
        print("RSI({}): {:.2f}".format(self.period, current_rsi))
        print("Signal: {}".format(signal))
        print("Recommendation: {}".format(recommendation))
        
        return {
            'symbol': symbol.upper(),
            'price': current_price,
            'rsi': current_rsi,
            'signal': signal
        }
    
    def analyze_multiple_stocks(self, symbols):
        """Analyze multiple stocks"""
        results = []
        
        print("RSI Analysis Starting...")
        print("=" * 30)
        
        for symbol in symbols:
            try:
                result = self.analyze_stock(symbol)
                if result:
                    results.append(result)
            except Exception as e:
                print("Error analyzing {}: {}".format(symbol, str(e)))
                
        # Summary
        if results:
            print("\nSUMMARY:")
            print("-" * 20)
            for result in results:
                print("{}: RSI {:.2f} - {}".format(
                    result['symbol'], 
                    result['rsi'], 
                    result['signal']
                ))
                
        return results

def main():
    """Main function"""
    print("RSI Trading Analysis Tool")
    print("=" * 30)
    
    # Initialize calculator
    rsi_calc = RSICalculator(period=14)
    
    # Test with popular stocks
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    try:
        results = rsi_calc.analyze_multiple_stocks(test_symbols)
        
        print("\nAnalysis completed for {} stocks!".format(len(results)))
        print("\nTips:")
        print("- RSI > 70: Potentially overbought")
        print("- RSI < 30: Potentially oversold")
        print("- RSI 30-70: Neutral territory")
        
    except Exception as e:
        print("Error during analysis: {}".format(str(e)))
        print("Check your internet connection and try again.")

if __name__ == "__main__":
    main()
