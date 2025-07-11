import random

from telebot import types
from telebot.types import InlineKeyboardMarkup

from bot.core.keyboards.universal import UniversalReplyKeyboard
from bot.core.states.common import UserState, KMNState, RedBlackState
from bot.core.utils.helpers import (
    transition_need_state,
    exit_to_navigation,
    continue_game,
)
from bot.core.utils.game import GameTimerSession, OnePlayerSession
from bot.config.settings import bot, logger
from bot.core.keyboards.inline import InlineDepositKeyboard
from bot.config.config_data import (
    CommonButtons,
    CallbackDataString,
    GameButtons,
    KMN_WIN_POSITIONS,
    BalanceData,
)
from database.crud import get_balance, update_balance


@bot.callback_query_handler(
    state=RedBlackState.balance,
    func=lambda call: call.data.split(":")[0] == CallbackDataString.deposit,
)
def handle_deposit(call: types.CallbackQuery):
    transition_need_state(
        call.message.chat.id,
        RedBlackState.game_process,
        text=f"Выберите куда выпадет:\n{GameButtons.red_black["red"]}, {GameButtons.red_black["black"]} или {GameButtons.red_black["green"]}?",
        buttons=GameButtons.red_black.values(),
    )
    with bot.retrieve_data(call.message.chat.id) as user_data:
        user_data["deposit"] = int(call.data.split(":")[1])


@bot.message_handler(
    state=RedBlackState.game_process,
    func=lambda message: message.text in GameButtons.red_black.values(),
)
def end_red_black(message: types.Message):
    deposit = None
    with bot.retrieve_data(message.chat.id) as user_data:
        deposit = user_data.get("deposit", "Нет депозита")

    result = random.choice(list(GameButtons.red_black.values()))
    RESULT_STRING = f"Выпало: {result}!"
    logger.info(f"Выпало: {RESULT_STRING}")

    if message.text == result and result in (
        GameButtons.red_black["red"],
        GameButtons.red_black["black"],
    ):
        update_balance(message.chat.id, get_balance(message.chat.id) + deposit)
        bot.send_message(
            message.chat.id,
            text=f"Мои поздравления.\n{RESULT_STRING} +{deposit} 💰",
        )

    elif message.text == result and result == GameButtons.red_black["green"]:
        update_balance(message.chat.id, get_balance(message.chat.id) + deposit * 14)
        bot.send_message(
            message.chat.id,
            text=f"Воу, а вы азартный игрок!\n{RESULT_STRING} +{deposit * 15} 💰",
        )

    else:
        new_balance = get_balance(message.chat.id) - deposit
        update_balance(message.chat.id, new_balance)
        if new_balance >= BalanceData.minimum:
            bot.send_message(
                message.chat.id,
                text=f"В другой раз повезет.\n{RESULT_STRING}\nНе желаете отыграться?",
                reply_markup=UniversalReplyKeyboard(
                    GameButtons.continue_game.values()
                ).markup,
            )
            return

        bot.send_message(
            message.chat.id,
            text=f"Эх. {RESULT_STRING}\nТеперь ваш баланс не позволяет играть. Бывает.",
        )
        exit_to_navigation(message.chat.id)
        return
    continue_game(message)
