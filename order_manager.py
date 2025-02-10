from alpaca_trade_api.rest import REST
import os
import logging

# Load API credentials securely
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure API keys are set
if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    logging.error("Missing Alpaca API keys. Set ALPACA_API_KEY and ALPACA_SECRET_KEY as environment variables.")
    raise ValueError("Alpaca API credentials are missing.")

# Initialize Alpaca API client
alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)


def execute_trade(symbol, qty, side, order_type="market", time_in_force="gtc"):
    """
    Execute a trade order on Alpaca.

    Parameters:
        symbol (str): Stock symbol to trade.
        qty (int): Number of shares.
        side (str): "buy" or "sell".
        order_type (str): Order type (default: "market").
        time_in_force (str): Order duration (default: "gtc" - good till canceled).

    Returns:
        dict: Order confirmation or None if an error occurs.
    """
    try:
        order = alpaca.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force=time_in_force
        )
        logging.info(f"Order submitted: Symbol={symbol}, Qty={qty}, Side={side}, Type={order_type}, Time in Force={time_in_force}")
        return order
    except Exception as e:
        logging.error(f"Error placing order: {e}")
        return None
