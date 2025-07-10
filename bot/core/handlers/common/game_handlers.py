from telebot import types
from telebot.types import InlineKeyboardMarkup

from bot.core.keyboards.universal import UniversalReplyKeyboard
from bot.core.states.common import UserState, KMNState
from bot.core.utils.helpers import transition_need_state
from bot.core.utils.game import GameTimerSession
from bot.config.settings import bot, logger
from bot.core.states.common import GameState
from bot.core.keyboards.inline import InlineDepositKeyboard
from bot.config.config_data import CommonButtons
from database.crud import get_balance, add_new_user


@bot.message_handler(commands=["game_test"])
def game_test(message: types.Message):
    GameTimerSession(
        bot=bot,
        message=message,
        game_redis_name="test+game",
        game_state=GameState.test,
        start_text="Start game",
    )
    # with bot.retrieve_data(message.chat.id) as data:
    #     opponent_id = data.get("opponent_id")
    # keyboards = InlineDepositKeyboards(message.chat.id, opponent_id)
    # bot.send_message(
    #     message.chat.id, text="Сделайте ставку", reply_markup=keyboards.player_markup
    # )
    # bot.send_message(
    #     opponent_id, text="Сделайте ставку", reply_markup=keyboards.opponent_markup
    # )

    # пользователь не может быть одновременно в нескольких сессиях !!
    # пользователь не может играть если баланс < 1
    # текущий баланс
    # сделайте ставки (максимальная ставка - это максимум у самого бедного), чтобы ничего не повалить
    # выводится общий банк и игра начинается, когда у каждого ready = True
    # дальше чисто процесс игры
    # для kmn сделать жизни


# нужна фабрика callback
@bot.callback_query_handler(state=KMNState.balance, func=lambda call: True)
def handle_balance_kmn(call: types.CallbackQuery):
    ...
    # если у противника есть ответ, то сравниваем
    # когда выбрали, то ready = True
