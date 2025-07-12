from telebot import types
from telebot.states import State
from typing import Union, TYPE_CHECKING

from telebot.types import ReplyKeyboardRemove

from bot.config.config_data import CommonButtons, GameButtons
from bot.config.settings import bot, logger
from bot.core.keyboards.universal import UniversalReplyKeyboard
from bot.core.states.common import UserState
from database.crud import get_balance

if TYPE_CHECKING:
    from bot.core.utils.game import Player


def transition_need_state(
    chat_id: int,
    need_state: State,
    text: str,
    buttons: Union[tuple[str], list[str]] | None = None,
    markup: Union[types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup] | None = None,
    delete: bool = True,
):
    if delete:
        bot.delete_state(chat_id)
    bot.set_state(chat_id, need_state)
    if buttons is None and markup is None:
        bot.send_message(chat_id, text=text)
        return
    if markup is None:
        markup = UniversalReplyKeyboard(buttons).markup
    bot.send_message(chat_id, text=text, reply_markup=markup)


def transition_remove_keyboard(message: types.Message, need_state: State, text: str):
    bot.delete_state(message.chat.id)
    bot.set_state(message.chat.id, need_state)
    bot.send_message(message.chat.id, text=text, reply_markup=ReplyKeyboardRemove())


def exit_to_navigation(chat_id: int):
    user_balance = get_balance(chat_id)
    transition_need_state(
        chat_id,
        need_state=UserState.navigation,
        text=f"Your balance: {f"${user_balance}" if user_balance else "$0"}",
        buttons=CommonButtons.navigation.values(),
    )


def transition_game_state(
    player: "Player", need_state: State, text: str, opponent: "Player"
) -> None:  # кнопка выход из игры
    logger.info(f"player - {player}\nopponent - {opponent}")
    transition_need_state(player.chat_id, need_state=need_state, text=text)
    transition_need_state(opponent.chat_id, need_state=need_state, text=text)
    with bot.retrieve_data(player.chat_id) as data:
        data["opponent_name"] = opponent.username
        data["opponent_id"] = opponent.chat_id
        data["ready"] = False

    with bot.retrieve_data(opponent.chat_id) as data:
        data["opponent_name"] = player.username
        data["opponent_id"] = player.chat_id
        data["ready"] = False


def continue_game(message: types.Message):
    bot.send_message(
        message.chat.id,
        text="Сыграем еще?",
        reply_markup=UniversalReplyKeyboard(GameButtons.continue_game.values()).markup,
    )
