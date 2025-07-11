from telebot.states import StatesGroup
from telebot import types

from bot.config.config_data import CommonButtons, GameButtons
from bot.config.settings import bot, logger
from bot.core.states.common import RedBlackState
from bot.core.utils.helpers import exit_to_navigation
from bot.core.handlers.game_handlers.red_black_handlers import red_black_handler


def make_continue_handlers(state_class: StatesGroup, called_function):
    if not "game_process" in state_class.__dict__:
        logger.warning("In handler creation game_process is not defined")
        return

    @bot.message_handler(
        state=state_class.game_process,
        func=lambda message: message.text in GameButtons.continue_game.values(),
    )
    def handler(message: types.Message):
        if message.text == GameButtons.continue_game["accept"]:
            called_function(message)
            return
        exit_to_navigation(message.chat.id)

    return handler


continue_handler_1 = make_continue_handlers(
    state_class=RedBlackState, called_function=red_black_handler
)


def make_exit_to_navigation(state_class: StatesGroup):
    @bot.message_handler(
        state=state_class.balance, func=lambda message: message.text == GameButtons.exit
    )
    def handler(message: types.Message):
        exit_to_navigation(message.chat.id)

    return handler


exit_handler_1 = make_exit_to_navigation(state_class=RedBlackState)
