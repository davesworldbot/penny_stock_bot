import alpaca_trade_api.rest as tradeapi
import pandas as pd
import yfinance as yf
import os
import logging

# ... (API Key loading and Alpaca initialization - same as before)

def get_account_balance():
    try:
        # ... (code to get balance)
        return balance
    except Exception as e:
        logging.error(f"Error fetching account balance: {e}")
        return None  # Explicitly return None on error

def get_yahoo_data(symbol):
    try:
        # ... (code to get Yahoo data)
        return process_market_data(df, symbol)
    except Exception as e:
        logging.error(f"Error fetching market data for {symbol} from Yahoo Finance: {e}")
        return None  # Explicitly return None on error

def process_market_data(df, symbol):
    # ... (code to process data - same as before)
    return df

def get_market_data(symbol):
    try:
        # ... (code to get market data from Alpaca)
        return get_yahoo_data(symbol) # Return the result of get_yahoo_data
    except Exception as e:
        logging.error(f"Error fetching market data for {symbol} from Alpaca: {e}. Falling back to Yahoo Finance.")
        return get_yahoo_data(symbol) # Return the result of get_yahoo_data
    return process_market_data(df, symbol)