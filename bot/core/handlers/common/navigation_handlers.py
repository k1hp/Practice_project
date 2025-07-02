from telebot import types

from bot.core.keyboards.universal import UniversalReplyKeyboard
from bot.core.states.common import UserState
from bot.core.utils.helpers import transition_need_state
from bot.config.settings import BOT, LOGGER, NAVIGATION_BUTTONS


@BOT.message_handler(commands=["start"])
def handle_start(message: types.Message):
    """
    Срабатывает один раз при запуске
    :param message:
    :return:
    """
    if BOT.get_state(message.from_user.id, message.chat.id) is None:
        LOGGER.info(f"Start user: {message.from_user.username}")
        BOT.set_state(message.chat.id, state=UserState.navigation)
        BOT.send_message(
            message.chat.id,
            text="Добро пожаловать в бота",
            reply_markup=UniversalReplyKeyboard(
                buttons=NAVIGATION_BUTTONS.values()
            ).markup,
        )
    return


@BOT.message_handler(commands=["navigation"])
def handle_navigation(message: types.Message):
    transition_need_state(
        message,
        need_state=UserState.navigation,
        text="Navigation",
        buttons=NAVIGATION_BUTTONS.values(),
    )
