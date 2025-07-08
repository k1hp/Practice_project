from telebot import types

from bot.core.keyboards.universal import UniversalReplyKeyboard
from bot.core.states.common import UserState
from bot.core.utils.helpers import transition_need_state
from bot.config.settings import bot, logger, NAVIGATION_BUTTONS


@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    """
    Срабатывает один раз при запуске
    :param message:
    :return:
    """
    if bot.get_state(message.from_user.id, message.chat.id) is None:
        logger.info(f"Start user: {message.from_user.username}")
        bot.set_state(message.chat.id, state=UserState.navigation)
        bot.send_message(
            message.chat.id,
            text="Добро пожаловать в бота",
            reply_markup=UniversalReplyKeyboard(
                buttons=NAVIGATION_BUTTONS.values()
            ).markup,
        )
    return


@bot.message_handler(commands=["navigation"])
def handle_navigation(message: types.Message):
    transition_need_state(
        message,
        need_state=UserState.navigation,
        text="Navigation",
        buttons=NAVIGATION_BUTTONS.values(),
    )
