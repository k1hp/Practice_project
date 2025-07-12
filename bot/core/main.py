from bot.config.settings import bot, logger, engine
from database.creation import create_tables
from telebot import types

if __name__ == "__main__":
    try:
        create_tables(engine=engine, logger=logger)
        from bot.core import handlers

        logger.info("Бот успешно запущен")
        from telebot import custom_filters

        bot.add_custom_filter(custom_filters.StateFilter(bot))
        commands = [
            types.BotCommand("navigation", "Вернуться в меню"),
            types.BotCommand("balance", "Проверить баланс"),
        ]

        # Устанавливаем команды
        bot.set_my_commands(commands)
        # bot.polling(none_stop=True)
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        logger.error("Traceback:", exc_info=True)
