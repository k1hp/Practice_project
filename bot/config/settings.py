import logging
import os
from sqlalchemy import create_engine
from pathlib import Path
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.storage import StateRedisStorage

load_dotenv()

StartPath = Path(__file__).parent.parent.parent

states_storage = StateRedisStorage(host="localhost", port=6379, db=0)
TOKEN = os.getenv("BOT_TOKEN")

bot = TeleBot(token=TOKEN, state_storage=states_storage)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

NAVIGATION_BUTTONS = {"echo": "LR1", "date_time": "LR2"}

db_path = StartPath / "database" / "bot.db"
engine = create_engine(f"sqlite:///{db_path}")

if __name__ == "__main__":
    print(TOKEN)
    print(db_path)
