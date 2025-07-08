from telebot import types

from bot.config.settings import engine, redis_cache, logger
from sqlalchemy import text
from typing import Optional, Union
from bot.config.config_data import START_BALANCE


def compile_rating_string() -> str:
    """
    Создает строчку рейтинга
    Получая информацию из sqlite
    :return:
    """
    query = """
    SELECT nickname, balance FROM users 
    ORDER BY balance DESC
    """
    string = "🏆 TOP 10"
    with engine.connect() as connection:
        result = connection.execute(text(query))
        for index, row in enumerate(result):
            print(row)
            if index >= 10:
                return string
            string += f"\n{index+1}. {row[0]}: ${row[1]}"
        if len(string) == 6:
            return string + "\nRating is empty"
        return string


def add_new_user(message: types.Message) -> None:
    query = text(
        """
                 INSERT INTO users (chat_id, nickname, balance)
                 VALUES (:chat_id, :nickname, :balance)
                 """
    )

    params = {
        "chat_id": message.chat.id,
        "nickname": message.from_user.username,
        "balance": START_BALANCE,  # Replace with START_BALANCE
    }
    with engine.connect() as connection:
        result = connection.execute(query, params)
        connection.commit()

        if result.rowcount > 0:
            logger.info(f"Added new user: {params['nickname']}")
        else:
            logger.warning(f"User {params['nickname']} already exists")


def update_cached_parameter(
    chat_id: int, parameter: str, value: Union[int, str]
) -> None:
    redis_cache.set(f"{parameter}:{chat_id}", value=value)
    logger.info(f"Updated cached parameter {parameter}:{chat_id} value {value}")


def get_cached_parameter(
    chat_id: int, parameter: str, table: str = "users"
) -> Optional[str]:
    redis_data = redis_cache.get(f"{parameter}:{chat_id}")
    if redis_data:
        return redis_data  # decode должен быть в конфиге redis
    query = f"""SELECT {parameter} FROM {table} WHERE chat_id = {chat_id}"""
    with engine.connect() as connection:
        result = connection.execute(text(query)).first()
        if not result:
            return None
        redis_cache.set(f"{parameter}:{chat_id}", value=result[0])
        return result[0]


def get_balance(chat_id: int) -> Optional[str]:
    return get_cached_parameter(chat_id, "balance")
