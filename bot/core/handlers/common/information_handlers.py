from telebot import types, State
from typing import Optional, Union
from datetime import datetime

from bot.config.settings import bot
from bot.config.config_data import CommonButtons, BalanceData
from bot.core.states.common import UserState
from bot.core.utils.helpers import (
    transition_need_state,
    transition_remove_keyboard,
)
from database.crud import compile_rating_string, get_balance


def make_button_handlers(
    button: str,
    need_state: Optional[State] = None,
    current_state: State = UserState.navigation,
    text: Optional[str] = None,
    buttons: Union[list[str], tuple[str], None] = None,
):
    """
    Фабрика обработчиков кнопок
    :param button:
    :param need_state:
    :param current_state:
    :return:
    """
    func = lambda message: message.text == button

    @bot.message_handler(state=current_state, func=func)
    def handler(message: types.Message):
        if (
            button == CommonButtons.navigation["games"]
            and get_balance(message.chat.id) < BalanceData.minimum
        ):
            bot.send_message(
                message.chat.id,
                text="Ваш баланс не позволяет играть.\nМожете пополнить его в профиле.",
            )
            return

        if need_state is None and text is not None:
            bot.send_message(message.chat.id, text=text)
        elif text is None:
            transition_remove_keyboard(
                message, need_state=need_state, text=f"State: {button}"
            )
        else:
            transition_need_state(
                message.chat.id, need_state=need_state, text=text, buttons=buttons
            )

    return handler


game_handler = make_button_handlers(
    button=CommonButtons.navigation["games"],
    need_state=UserState.games,
    text="Choose game",
    buttons=CommonButtons.games.values(),
)


@bot.message_handler(
    state=UserState.navigation,
    func=lambda message: message.text == CommonButtons.navigation["rating"],
)
def handle_rating(message: types.Message):
    bot.send_message(message.chat.id, text=compile_rating_string())
