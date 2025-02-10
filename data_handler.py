import os
import logging
import pandas as pd
import yfinance as yf
import alpaca_trade_api as tradeapi

# Load API Keys from Environment Variables
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[logging.FileHandler("trading_bot.log"), logging.StreamHandler()])

def get_account_balance():
    """Fetch account balance from Alpaca."""
    try:
        account = api.get_account()
        return float(account.cash)
    except Exception as e:
        logging.error(f"Error fetching account balance: {e}")
        return None

def is_stock_delisted(symbol):
    """
    Check if a stock is delisted based on Yahoo Finance errors.
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1mo")
        return hist.empty  # If empty, it is likely delisted
    except:
        return True  # Assume delisted if error occurs

def get_yahoo_data(symbol):
    """Fetch market data from Yahoo Finance if Alpaca data is unavailable."""
    try:
        df = yf.download(symbol, period="1mo", interval="1d")
        if df.empty:
            logging.warning(f"{symbol} appears delisted. Skipping.")
            return None  # Stops further attempts for delisted stocks
        df.reset_index(inplace=True)
        df.rename(columns={"Adj Close": "Close"}, inplace=True)
        return df
    except Exception as e:
        logging.error(f"Error fetching market data for {symbol} from Yahoo Finance: {e}")
        return None

def get_market_data(symbol):
    """Fetch market data from Alpaca, fallback to Yahoo Finance only if needed."""
    try:
        bars = api.get_bars(symbol, timeframe="1Day", limit=30).df  # Fetch from Alpaca
        if not bars.empty:
            bars.rename(columns={"close": "Close"}, inplace=True)  # Ensure consistency
            logging.info(f"{symbol}: Using Alpaca data. Skipping Yahoo Finance.")
            return bars  # ✅ STOP here if Alpaca has data
    except Exception as e:
        logging.error(f"Error fetching market data for {symbol} from Alpaca: {e}. Falling back to Yahoo Finance.")

    # ✅ Check if stock is already flagged as delisted before calling Yahoo
    if is_stock_delisted(symbol):
        logging.warning(f"{symbol} appears delisted. Skipping Yahoo Finance lookup.")
        return None  

    # Only call Yahoo Finance if Alpaca data is empty
    yahoo_data = get_yahoo_data(symbol)
    if yahoo_data is None:
        logging.warning(f"{symbol} has no data from either Alpaca or Yahoo Finance. Skipping.")
        return None  

    return yahoo_data

def fetch_historical_data(symbol, start="2023-08-01", end="2024-02-01"):
    """Fetch historical stock data from Alpaca and save it to a CSV file."""
    try:
        bars = api.get_bars(symbol, timeframe="1Day", start=start, end=end).df
        if bars.empty:
            logging.warning(f"No historical data found for {symbol}.")
            return None
        
        bars.reset_index(inplace=True)
        bars["Date"] = bars.index.date  # Store date properly
        bars = bars[["Date", "close"]]  # Keep only necessary columns
        bars.rename(columns={"close": "Close"}, inplace=True)

        # Save to CSV
        filename = f"historical_data_{symbol}.csv"
        bars.to_csv(filename, index=False)
        logging.info(f"Saved {symbol} historical data to {filename}")
        return filename
    except Exception as e:
        logging.error(f"Error fetching historical data for {symbol}: {e}")
        return None




