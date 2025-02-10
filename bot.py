import logging
from data_handler import get_account_balance, get_market_data
from strategy import apply_strategy, calculate_indicators, INITIAL_CAPITAL, penny_stocks # Import everything you need
from order_manager import execute_trade # Import execute_trade
import time
import json
import subprocess
from multiprocessing import Pool

# Logging setup (same as your original code)
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

def main():
    balance = get_account_balance()
    if balance is None: # Handle if no balance is available.
        logging.error("Could not retrieve account balance. Exiting.")
        return # Stop execution if balance cannot be fetched.

    logging.info(f"Current account balance: ${balance}")
    for symbol in penny_stocks:
        logging.info(f"Analyzing {symbol}...")
        market_data = get_market_data(symbol)
        if market_data is not None:
            market_data = calculate_indicators(market_data)
            if market_data is not None:  # Check if indicators were calculated successfully
                final_value = apply_strategy(market_data, symbol)
                if final_value is not None:  # Check if apply_strategy executed successfully
                    logging.info(f"Analysis complete for {symbol}.")
                else:
                    logging.warning(f"apply_strategy returned None for {symbol}. Check the logs for errors.")
            else:
                logging.warning(f"calculate_indicators returned None for {symbol}. Check the logs for errors.")
        else:
            logging.warning(f"No market data available for {symbol}. Skipping.")

    upload_logs()
    logging.info("Bot execution complete. Exiting.")

if __name__ == "__main__":
    logging.info("Starting trading bot...")
    main()