import os
import subprocess
import sys

# Define the bot directory
BOT_DIR = os.path.expanduser("~/penny_stock_bot")

def update_bot():
    try:
        print("🔄 Fetching latest updates for the trading bot...")

        # Change to bot directory
        os.chdir(BOT_DIR)

        # Pull the latest code (If using GitHub or another repo)
        subprocess.run(["git", "pull", "origin", "main"], check=True)

        # Activate virtual environment
        venv_activate = f"source {BOT_DIR}/.venv/bin/activate"

        # Ensure dependencies are installed
        subprocess.run(f"{venv_activate} && pip install -r requirements.txt", shell=True, check=True)

        print("✅ Update complete. Restarting the bot...")

        # Restart the bot
        subprocess.run(f"{venv_activate} && python3 bot.py", shell=True, check=True)

    except Exception as e:
        print(f"❌ Update failed: {e}")

if __name__ == "__main__":
    update_bot()
