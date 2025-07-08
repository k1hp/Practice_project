from sqlalchemy.engine.base import Engine
from sqlalchemy import text


def create_tables(engine: Engine, logger) -> None:
    queries = (
        # """DROP TABLE IF EXISTS users""",
        """
        CREATE TABLE IF NOT EXISTS users (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            `chat_id` INTEGER NOT NULL UNIQUE ,
            `nickname` VARCHAR(100) NOT NULL UNIQUE,
            `balance` UNSIGNED BIG INT NOT NULL
        )
        """,
    )
    with engine.connect() as connection:
        for query in queries:
            connection.execute(text(query))
        connection.commit()
    logger.info("База данных очищена и создана заново")
