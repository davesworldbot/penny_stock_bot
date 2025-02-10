import os
import logging
from data_handler import get_account_balance, get_market_data
from strategy import apply_strategy, calculate_indicators, INITIAL_CAPITAL
import time
import subprocess
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[logging.FileHandler("trading_bot.log"), logging.StreamHandler()])

def upload_logs():
    """Upload logs to Google Drive using rclone."""
    GDRIVE_FOLDER = "gdrive:/TradingBotLogs"
    try:
        subprocess.run(["rclone", "mkdir", GDRIVE_FOLDER], check=True)
        subprocess.run(["rclone", "copy", "trading_bot.log", GDRIVE_FOLDER, "--copy-links"], check=True)
        logging.info("Log files uploaded to Google Drive successfully.")
    except Exception as e:
        logging.error(f"Failed to upload logs: {e}")

def main():
    print("Running backtest...")

    # Load historical stock data
    data = pd.read_csv("historical_data.csv")  # Ensure this file exists
    data["Date"] = pd.to_datetime(data["Date"])

    # Run backtest
    balance = 100  # Start with $100
    pdt_limit = 3  # Max 3 trades per day

    trade_dates = []
    balance_history = []

    for index, row in data.iterrows():
        close_price = row["Close"]
        date = row["Date"]

        if balance >= close_price:
            shares = int(balance / close_price)
            balance = shares * close_price  # Invest entire balance

            trade_dates.append(date)
            balance_history.append(balance)

            if len(trade_dates) >= pdt_limit:
                break  # Stop trading to comply with PDT

    # Plot the backtest results
    plt.plot(trade_dates, balance_history, label="Balance Growth")
    plt.xlabel("Date")
    plt.ylabel("Account Balance")
    plt.title("Backtest Performance")
    plt.legend()
    plt.show()

    print("Backtest complete. Final balance:", balance)

