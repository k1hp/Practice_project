from telebot import types

from bot.core.keyboards.universal import UniversalReplyKeyboard
from bot.core.states.common import UserState
from bot.core.utils.helpers import transition_need_state
from bot.config.settings import bot, logger
from bot.config.config_data import CommonButtons
from database.crud import get_balance, add_new_user


@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    """
    Срабатывает один раз при запуске
    :param message:
    :return:
    """
    if bot.get_state(message.from_user.id, message.chat.id) is None:
        logger.info(f"Start user: {message.from_user.username}")
        add_new_user(message=message)
        bot.set_state(message.chat.id, state=UserState.navigation)
        bot.send_message(
            message.chat.id,
            text="🎰 Добро пожаловать! 🎲",
            reply_markup=UniversalReplyKeyboard(
                buttons=CommonButtons.navigation.values()
            ).markup,
        )

    return


@bot.message_handler(commands=["navigation"])
def handle_navigation(message: types.Message):
    if bot.get_state(message.from_user.id, message.chat.id):
        # получение баланса отдельной функцией с кешированием
        user_balance = get_balance(message.chat.id)
        transition_need_state(
            message.chat.id,
            need_state=UserState.navigation,
            text=f"Navigation\nYour balance: {f"${user_balance}" if user_balance else "$0"}",
            buttons=CommonButtons.navigation.values(),
        )


@bot.callback_query_handler(func=lambda call: call.data == "ignore")
def ignore_callback(call):
    """
    Обработка пустых кнопок
    :param call:
    :return:
    """
    bot.answer_callback_query(call.id)  # Просто закрываем уведомление
