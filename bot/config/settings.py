import logging
import os
from sqlalchemy import create_engine
from pathlib import Path
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.storage import StateRedisStorage
from redis import Redis

load_dotenv()

StartPath = Path(__file__).parent.parent.parent
REDIS_PORT = int(os.getenv("REDIS_PORT"))

states_storage = StateRedisStorage(host="localhost", port=REDIS_PORT, db=0)
TOKEN = os.getenv("BOT_TOKEN")

redis_cache = Redis(
    host="localhost", port=REDIS_PORT, db=1
)  # разделяем, чтобы не путать

bot = TeleBot(token=TOKEN, state_storage=states_storage)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

db_path = StartPath / "database" / "bot.db"
engine = create_engine(f"sqlite:///{db_path}")

if __name__ == "__main__":
    print(TOKEN)
    print(db_path)
