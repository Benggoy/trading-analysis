import pandas as pd
import yfinance as yf

print('RSI Analysis Test')
print('================')

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(span=period).mean()
    avg_loss = loss.ewm(span=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

try:
    print('Downloading AAPL data...')
    data = yf.download('AAPL', period='3mo', progress=False)['Close']
    rsi = calculate_rsi(data)
    
    # Convert to float to avoid formatting issues
    current_price = float(data.iloc[-1])
    current_rsi = float(rsi.iloc[-1])
    
    print('AAPL Current Price: ${:.2f}'.format(current_price))
    print('AAPL RSI: {:.2f}'.format(current_rsi))
    
    if current_rsi > 70:
        print('Status: OVERBOUGHT (potential sell signal)')
    elif current_rsi < 30:
        print('Status: OVERSOLD (potential buy signal)')
    else:
        print('Status: NEUTRAL')
        
    print('SUCCESS: RSI calculator working!')
    
    # Test with more stocks
    print('\nTesting additional stocks...')
    for symbol in ['MSFT', 'GOOGL']:
        try:
            print('Analyzing {}...'.format(symbol))
            stock_data = yf.download(symbol, period='3mo', progress=False)['Close']
            stock_rsi = calculate_rsi(stock_data)
            
            price = float(stock_data.iloc[-1])
            rsi_val = float(stock_rsi.iloc[-1])
            
            print('{} Price: ${:.2f}, RSI: {:.2f}'.format(symbol, price, rsi_val))
            
        except Exception as stock_error:
            print('Error with {}: {}'.format(symbol, str(stock_error)))
    
    print('\nRSI Analysis Complete!')
    
except Exception as e:
    print('Error: {}'.format(str(e)))
