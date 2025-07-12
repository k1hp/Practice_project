import random

from telebot import types
from telebot.types import InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup

from bot.core.keyboards.universal import UniversalReplyKeyboard
from bot.core.states.common import UserState, KMNState, RedBlackState, SaperState
from bot.core.utils.helpers import (
    transition_need_state,
    exit_to_navigation,
    continue_game,
)
from bot.core.utils.game import GameTimerSession, OnePlayerSession
from bot.config.settings import bot, logger
from bot.core.keyboards.inline import (
    InlineDepositKeyboard,
    InlineBombsKeyboard,
    InlineSaperKeyboard,
)
from bot.config.config_data import (
    CommonButtons,
    CallbackDataString,
    GameButtons,
    KMN_WIN_POSITIONS,
    BalanceData,
    COEFFICIENTS,
)
from database.crud import get_balance, update_balance


@bot.callback_query_handler(
    state=SaperState.balance,
    func=lambda call: call.data.split(":")[0] == CallbackDataString.deposit,
)
def handle_deposit(call: types.CallbackQuery):
    transition_need_state(
        call.message.chat.id,
        SaperState.bombs,
        text="5x5 Выберите количество бомб:\n💣 Больше бомб - больше выигрыш\n🎰 Кто не рискует - тот не рискует.",
        markup=InlineBombsKeyboard(),
        delete=False,
    )
    with bot.retrieve_data(call.message.chat.id) as user_data:
        user_data["deposit"] = int(call.data.split(":")[1])


@bot.callback_query_handler(
    state=SaperState.bombs,
    func=lambda call: call.data.split(":")[0] == CallbackDataString.bombs,
)
def handle_bombs_count(call: types.CallbackQuery):
    bombs_count = int(call.data.split(":")[1])
    logger.info(f"Bombs count: {bombs_count}")
    with bot.retrieve_data(call.message.chat.id) as user_data:
        user_data["coefficient"] = COEFFICIENTS[str(bombs_count)]
    bot.send_message(
        call.message.chat.id,
        ".",
        reply_markup=UniversalReplyKeyboard(buttons=(GameButtons.pick_jackpot,)).markup,
    )
    # bot.delete_message(call.message.chat.id, call.message.id)
    transition_need_state(
        call.message.chat.id,
        SaperState.game_process,
        text="💣 Приступим к игре",
        markup=InlineSaperKeyboard(bombs_count),
        delete=False,
    )


# кнопка забрать куш, и обновляем сколько человек получит денег
@bot.callback_query_handler(
    state=SaperState.game_process,
    func=lambda call: call.data.split(":")[0] == CallbackDataString.cell,
)
def handle_cell(call: types.CallbackQuery):
    with bot.retrieve_data(call.message.chat.id) as user_data:
        deposit = user_data.get("deposit", "Нет депозита")
        k = user_data.get("coefficient")
        jackpot = int(deposit * k)
        user_data["jackpot"] = jackpot

    current_markup = call.message.reply_markup
    if call.data.split(":")[1] == "bomb":
        new_balance = get_balance(call.message.chat.id) - deposit
        update_balance(call.message.chat.id, new_balance)

        for row in current_markup.keyboard:
            for button in row:
                if button.callback_data == call.data:
                    button.text = f"💣"
                    button.callback_data = "ignore"  # Делаем неактивной

        # Обновляем сообщение
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"💣 Jackpot: {jackpot}",
            reply_markup=current_markup,
        )
        if new_balance >= BalanceData.minimum:
            bot.send_message(
                call.message.chat.id,
                text=f"В другой раз повезет.\nНе желаете отыграться?",
                reply_markup=UniversalReplyKeyboard(
                    GameButtons.continue_game.values()
                ).markup,
            )
            return

        bot.send_message(
            call.message.chat.id,
            text=f"Эх. Теперь ваш баланс не позволяет играть. Бывает.",
        )
        exit_to_navigation(call.message.chat.id)
        return

    # current_markup = call.message.reply_markup

    # Меняем только нажатую кнопку
    for row in current_markup.keyboard:
        for button in row:
            if button.callback_data == call.data:
                button.text = f"💰"
                button.callback_data = "ignore"  # Делаем неактивной

    # Обновляем сообщение
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"💣 Jackpot: {jackpot}",
        reply_markup=current_markup,
    )


@bot.message_handler(
    state=SaperState.game_process,
    func=lambda message: message.text == GameButtons.pick_jackpot,
)
def handle_stop(message: types.Message):
    with bot.retrieve_data(message.chat.id) as user_data:
        jackpot = user_data.get("jackpot", 0)

    update_balance(message.chat.id, get_balance(message.chat.id) + jackpot)
    bot.send_message(
        message.chat.id, text=f"Поздравляю!\nВаш выигрыш составил: ${jackpot}"
    )
    continue_game(message)
