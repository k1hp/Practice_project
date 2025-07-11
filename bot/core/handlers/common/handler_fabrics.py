from telebot.states import StatesGroup, State
from telebot import types

from bot.config.config_data import CommonButtons, GameButtons
from bot.config.settings import bot, logger
from bot.core.states.common import RedBlackState, UserState
from bot.core.utils.game import OnePlayerSession
from bot.core.utils.helpers import exit_to_navigation

# from bot.core.handlers.game_handlers.red_black_handlers import red_black_handler


def make_exit_to_navigation(state_class: StatesGroup):
    @bot.message_handler(
        state=state_class.balance, func=lambda message: message.text == GameButtons.exit
    )
    def handler(message: types.Message):
        exit_to_navigation(message.chat.id)

    return handler


exit_red_black_handler = make_exit_to_navigation(state_class=RedBlackState)


def make_start_offline_game(
    current_state: State, need_state: State, check_button: str, start_text: str
):
    @bot.message_handler(
        state=current_state,
        func=lambda message: message.text == check_button,
    )
    def handler(message: types.Message):
        with bot.retrieve_data(message.chat.id) as data:
            deposit = data.get("deposit")
        OnePlayerSession(
            bot,
            message=message,
            game_state=need_state,
            start_text="Продолжаем" if deposit else start_text,
        )

    return handler


start_red_black_handler = make_start_offline_game(
    current_state=UserState.games,
    need_state=RedBlackState.balance,
    check_button=CommonButtons.games["red_black"],
    start_text="Добро пожаловать в рулетку",
)


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


continue_red_black_handler = make_continue_handlers(
    state_class=RedBlackState, called_function=start_red_black_handler
)
