from telebot import types
from telebot.states import State
from typing import Union

from telebot.types import ReplyKeyboardRemove

from bot.config.settings import bot
from bot.core.keyboards.universal import UniversalReplyKeyboard


def transition_need_state(
    message: types.Message,
    need_state: State,
    text: str,
    buttons: Union[tuple[str], list[str]],
):
    bot.delete_state(message.chat.id)
    bot.set_state(message.chat.id, need_state)
    bot.send_message(
        message.chat.id, text=text, reply_markup=UniversalReplyKeyboard(buttons).markup
    )


def transition_remove_keyboard(message: types.Message, need_state: State, text: str):
    bot.delete_state(message.chat.id)
    bot.set_state(message.chat.id, need_state)
    bot.send_message(message.chat.id, text=text, reply_markup=ReplyKeyboardRemove())
