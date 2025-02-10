# ... (order_manager.py content - same as previous response)
from alpaca_trade_api.rest import REST, Order
import os
import logging

from alpaca_trade_api.rest import REST
import os
import logging

# Load API credentials securely
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    logging.error("Missing Alpaca API keys. Set ALPACA_API_KEY and ALPACA_SECRET_KEY as environment variables.")
    exit(1)

alpaca = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)

def execute_trade(symbol, qty, side, order_type='market', time_in_force='gtc'): # Added parameters
    try:
        order = alpaca.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type, # Use parameter here
            time_in_force=time_in_force # Use parameter here
        )
        logging.info(f"Order submitted: {order}")
        return order
    except Exception as e:
        logging.error(f"Error placing order: {e}")
        return None