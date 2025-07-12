from telebot import types

from bot.config.settings import bot
from bot.config.config_data import CommonButtons, BalanceData
from bot.core.states.common import UserState
from bot.core.utils.helpers import (
    exit_to_navigation,
)
from database.crud import (
    get_balance,
    get_username,
    update_balance,
)


@bot.message_handler(
    state=UserState.profile,
    func=lambda message: message.text == CommonButtons.profile["info"],
)
def profile(message: types.Message):
    bot.send_message(
        message.chat.id,
        text=f"🗃️ Ваши данные:\n🐵 Username: {get_username(message.chat.id)}\n💰 Balance: {get_balance(message.chat.id)}",
    )


@bot.message_handler(
    state=UserState.profile,
    func=lambda message: message.text == CommonButtons.profile["replenish"],
)
def replenish(message: types.Message):
    if get_balance(message.chat.id) < BalanceData.start:
        update_balance(message.chat.id, BalanceData.start)
        bot.send_message(
            message.chat.id, text="Баланс был успешно пополнен.\nПриятной игры."
        )
    else:
        bot.send_message(
            message.chat.id,
            text=f"На данный момент ваш баланс является достаточным для игры.",
        )
    exit_to_navigation(message.chat.id)
