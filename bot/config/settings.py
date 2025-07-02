import logging
import os
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.storage import StateRedisStorage

load_dotenv()

states_storage = StateRedisStorage(host="localhost", port=6379, db=0)
TOKEN = os.getenv("BOT_TOKEN")

BOT = TeleBot(token=TOKEN, state_storage=states_storage)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

NAVIGATION_BUTTONS = {"echo": "LR1", "date_time": "LR2"}

if __name__ == "__main__":
    print(TOKEN)