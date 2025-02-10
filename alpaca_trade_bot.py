import logging
import openai
import talib
import pandas as pd
import yfinance as yf
import numpy as np
import os
import subprocess
from alpaca_trade_api.rest import REST, TimeFrame, Order
import time
import json
from multiprocessing import Pool

# Load API credentials securely
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    logging.error("Missing Alpaca API keys. Set ALPACA_API_KEY and ALPACA_SECRET_KEY as environment variables.")
    exit(1)

alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", 
                    handlers=[logging.FileHandler("trading_bot.log"), logging.StreamHandler()])

def log_debug_report(message):
    with open("debug_report.txt", "a") as f:
        f.write(message + "\n")

def upload_logs():
    GDRIVE_FOLDER = "gdrive:/TradingBotLogs"
    try:
        subprocess.run(["rclone", "mkdir", GDRIVE_FOLDER], check=True)
        subprocess.run(["rclone", "copy", "trading_bot.log", GDRIVE_FOLDER, "--copy-links"], check=True)
        subprocess.run(["rclone", "copy", "debug_report.txt", GDRIVE_FOLDER, "--copy-links"], check=True)
        logging.info("Log files uploaded to Google Drive successfully.")
    except Exception as e:
        logging.error(f"Failed to upload logs: {e}")

# Define penny stock symbols
penny_stocks = ["MULN", "CEI", "HCMC", "SNDL", "OCGN"]

# Strategy Parameters
SMA_PERIOD = 10
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
TRAILING_STOP_PERCENT = 0.03  # 3% trailing stop loss
INITIAL_CAPITAL = 100  # Starting capital per trade

def get_account_balance():
    try:
        logging.info("Fetching account balance from Alpaca...")
        account = alpaca.get_account()
        balance = float(account.cash)
        logging.info(f"Account balance: ${balance}")
        return balance
    except Exception as e:
        logging.error(f"Error fetching account balance: {e}")
        log_debug_report(f"Error fetching account balance: {e}")
        return 0.0

def get_yahoo_data(symbol):
    try:
        logging.info(f"Fetching {symbol} data from Yahoo Finance...")
        df = yf.download(symbol, period="6mo", interval="1d")
        if df.empty:
            logging.warning(f"No data found for {symbol} on Yahoo Finance.")
            return None
        return process_market_data(df, symbol)
    except Exception as e:
        logging.error(f"Error fetching market data for {symbol} from Yahoo Finance: {e}")
        log_debug_report(f"Error fetching market data for {symbol} from Yahoo Finance: {e}")
        return None

def process_market_data(df, symbol):
    df.reset_index(inplace=True)
    if 'Close' not in df.columns:
        logging.error(f"No 'Close' price data found for {symbol}")
        return None
    close_prices = df['Close'].dropna().values
    if close_prices.size == 0:
        logging.error(f"No valid close prices for {symbol}, skipping.")
        return None
    close_prices = close_prices.astype(float).reshape(-1)  # Ensure it's a 1D NumPy array
    df['MACD'], df['MACD_Signal'], _ = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    df['RSI'] = talib.RSI(close_prices, timeperiod=14)
    df['SMA_50'] = talib.SMA(close_prices, timeperiod=50)
    df['SMA_200'] = talib.SMA(close_prices, timeperiod=200)
    logging.info(f"Indicators calculated for {symbol}.")
    return df

def get_market_data(symbol):
    try:
        logging.info(f"Fetching market data for {symbol} from Alpaca...")
        bars = alpaca.get_barset(symbol, "1D", limit=100).df
        if bars.empty or "close" not in bars.columns:
            logging.warning(f"Not enough data for {symbol} from Alpaca. Falling back to Yahoo Finance.")
            return get_yahoo_data(symbol)
        df = bars[['close']].copy()
        df.rename(columns={"close": "Close"}, inplace=True)
    except Exception as e:
        logging.error(f"Error fetching market data for {symbol} from Alpaca: {e}. Falling back to Yahoo Finance.")
        return get_yahoo_data(symbol)
    return process_market_data(df, symbol)

def main():
    balance = get_account_balance()
    logging.info(f"Current account balance: ${balance}")
    for symbol in penny_stocks:
        logging.info(f"Analyzing {symbol}...")
        market_data = get_market_data(symbol)
        final_value = apply_strategy(market_data, symbol)
        logging.info(f"Final Portfolio Value: ${final_value:.2f}")
    upload_logs()
    logging.info("Bot execution complete. Exiting.")

if __name__ == "__main__":
    logging.info("Starting trading bot...")
    main()
