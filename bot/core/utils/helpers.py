from telebot import types
from telebot.states import State
from typing import Union, TYPE_CHECKING

from telebot.types import ReplyKeyboardRemove

from bot.config.settings import bot, logger
from bot.core.keyboards.universal import UniversalReplyKeyboard

if TYPE_CHECKING:
    from bot.core.utils.game import Player


def transition_need_state(
    chat_id: int,
    need_state: State,
    text: str,
    buttons: Union[tuple[str], list[str]],
):
    bot.delete_state(chat_id)
    bot.set_state(chat_id, need_state)
    bot.send_message(
        chat_id, text=text, reply_markup=UniversalReplyKeyboard(buttons).markup
    )


def transition_remove_keyboard(message: types.Message, need_state: State, text: str):
    bot.delete_state(message.chat.id)
    bot.set_state(message.chat.id, need_state)
    bot.send_message(message.chat.id, text=text, reply_markup=ReplyKeyboardRemove())


def transition_game_state(
    player: "Player", need_state: State, text: str, opponent: "Player"
) -> None:  # кнопка выход из игры
    logger.info(f"player - {player}\nopponent - {opponent}")
    transition_need_state(
        player.chat_id, need_state=need_state, text=text, buttons=("Выход_1",)
    )
    transition_need_state(
        opponent.chat_id, need_state=need_state, text=text, buttons=("Выход_2",)
    )
    with bot.retrieve_data(player.chat_id) as data:
        data["opponent_name"] = opponent.username
        data["opponent_id"] = opponent.chat_id
        data["ready"] = False

    with bot.retrieve_data(opponent.chat_id) as data:
        data["opponent_name"] = player.username
        data["opponent_id"] = player.chat_id
        data["ready"] = False
