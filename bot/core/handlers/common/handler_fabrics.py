from telebot.states import State
from telebot import types
from typing import Optional

from bot.config.config_data import CommonButtons, GameButtons
from bot.config.settings import bot
from bot.core.states.common import RedBlackState, UserState, SaperState
from bot.core.utils.game import OnePlayerSession
from bot.core.utils.helpers import exit_to_navigation


def make_exit_to_navigation(state: State, custom_button: Optional[str] = None):
    """
    Фабрика обработчиков кнопки выхода из игры
    :param state:
    :return:
    """
    button = custom_button if custom_button else GameButtons.exit

    @bot.message_handler(state=state, func=lambda message: message.text == button)
    def handler(message: types.Message):
        exit_to_navigation(message.chat.id)

    return handler


exit_red_black_handler = make_exit_to_navigation(state=RedBlackState.balance)
exit_saper_handler_1 = make_exit_to_navigation(state=SaperState.balance)
exit_saper_handler_2 = make_exit_to_navigation(state=SaperState.bombs)
exit_profile = make_exit_to_navigation(
    state=UserState.profile, custom_button=CommonButtons.profile["exit"]
)


def make_start_offline_game(
    current_state: State, need_state: State, check_button: str, start_text: str
):
    """
    Фабрика генерирующая обработчики начала игры,
    которые являются кольцевыми,
    если пользователь захочет играть снова.

    :param current_state:
    :param need_state:
    :param check_button:
    :param start_text:
    :return:
    """

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
            start_text="Продолжаем 🤑" if deposit else start_text,
        )

    return handler


start_red_black_handler = make_start_offline_game(
    current_state=UserState.games,
    need_state=RedBlackState.balance,
    check_button=CommonButtons.games["red_black"],
    start_text=f"Добро пожаловать!\nКлассическая рулетка, ставьте на что угодно.\n{GameButtons.red_black["red"]} {GameButtons.red_black["black"]} x2\n{GameButtons.red_black["green"]} x15",
)
start_saper_handler = make_start_offline_game(
    current_state=UserState.games,
    need_state=SaperState.balance,
    check_button=CommonButtons.games["saper"],
    start_text="Добро пожаловать!\n🍀 Чем больше пустых ячеек откроешь, тем больше выигрыш.\n💣 Если наткнешься на бомбу, то все потеряешь.\n🤯 Удачи.",
)


def make_continue_handlers(state: State, called_function):
    """
    Фабрика обработчиков,
    которые либо прекращают игру,
    либо начинают такую же новую.
    :param state:
    :param called_function:
    :return:
    """

    @bot.message_handler(
        state=state,
        func=lambda message: message.text in GameButtons.continue_game.values(),
    )
    def handler(message: types.Message):
        if message.text == GameButtons.continue_game["accept"]:
            called_function(message)
            return
        exit_to_navigation(message.chat.id)

    return handler


continue_red_black_handler = make_continue_handlers(
    state=RedBlackState.game_process, called_function=start_red_black_handler
)
continue_saper_handler = make_continue_handlers(
    state=SaperState.game_process, called_function=start_saper_handler
)
