from bot.config.settings import BOT, LOGGER

if __name__ == "__main__":
    try:
        from bot.core import handlers

        LOGGER.info("Бот успешно запущен")
        from telebot import custom_filters

        BOT.add_custom_filter(custom_filters.StateFilter(BOT))
        BOT.polling(none_stop=True)
    except Exception as e:
        LOGGER.error(f"Ошибка: {e}")
        LOGGER.error("Traceback:", exc_info=True)
