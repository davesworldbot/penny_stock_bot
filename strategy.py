import pandas as pd
import logging

# Strategy Parameters
SMA_PERIOD = 10
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
TRAILING_STOP_PERCENT = 0.03  # 3% trailing stop loss
INITIAL_CAPITAL = 100  # Starting capital per trade

def calculate_indicators(df):
    """Calculate trading indicators for strategy."""
    try:
        # Ensure 'Close' column exists
        if 'Close' not in df.columns:
            raise ValueError("Missing 'Close' column in market data")

        close_prices = df['Close'].astype(float)

        # Calculate MACD using pandas
        df['EMA_12'] = close_prices.ewm(span=MACD_FAST, adjust=False).mean()
        df['EMA_26'] = close_prices.ewm(span=MACD_SLOW, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=MACD_SIGNAL, adjust=False).mean()

        # Calculate RSI properly
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).ewm(span=RSI_PERIOD, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(span=RSI_PERIOD, adjust=False).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Calculate SMA
        df['SMA_50'] = close_prices.rolling(window=50).mean()
        df['SMA_200'] = close_prices.rolling(window=200).mean()

        logging.info(f"Indicators calculated successfully.")
        return df
    except Exception as e:
        logging.error(f"Error calculating indicators: {e}")
        return None  # Handle potential errors

def apply_strategy(df, symbol):
    """
    Trading strategy:
    - Buy when RSI < 30 and MACD crosses above the signal line
    - Sell when RSI > 70 or MACD crosses below the signal line
    """
    logging.info(f"Applying strategy for {symbol}...")

    try:
        df["Signal"] = 0  # Default to no action (0)
        
        # Buy Condition: RSI below 30 and MACD crosses above signal
        df.loc[(df["RSI"] < 30) & (df["MACD"] > df["MACD_Signal"]), "Signal"] = 1  # Buy

        # Sell Condition: RSI above 70 or MACD crosses below signal
        df.loc[(df["RSI"] > 70) | (df["MACD"] < df["MACD_Signal"]), "Signal"] = -1  # Sell

        return df
    except Exception as e:
        logging.error(f"Error applying strategy for {symbol}: {e}")
        return df
