from telebot import types
from telebot.states import State
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
import time
import threading
from typing import Optional, Union

from bot.core.keyboards.universal import UniversalReplyKeyboard
from bot.core.states.common import UserState, KMNState
from bot.core.utils.helpers import transition_need_state, exit_to_navigation
from bot.core.utils.game import GameTimerSession
from bot.config.settings import bot, logger
from bot.core.keyboards.inline import InlineDepositKeyboard
from bot.config.config_data import (
    CommonButtons,
    CallbackDataString,
    GameButtons,
    KMN_WIN_POSITIONS,
)
from database.crud import get_balance, add_new_user, update_balance


# валидация, что user не находится в другом подборе
@bot.message_handler(commands=["game_test"])
def game_test(message: types.Message):
    GameTimerSession(
        bot=bot,
        message=message,
        game_redis_name="test+game",
        game_state=KMNState.balance,
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


# в фабрику передадим класс, а от него вызовем соответствующие состояния
@bot.callback_query_handler(
    state=KMNState.balance,
    func=lambda call: call.data.split(":")[0] == CallbackDataString.deposit,
)
def handle_balance_kmn(call: types.CallbackQuery):
    with bot.retrieve_data(call.message.chat.id) as user_data:
        user_data["deposit"] = int(call.data.split(":")[1])
        user_data["ready"] = True
        opponent_id = user_data.get("opponent_id")

        with bot.retrieve_data(opponent_id) as opponent_data:
            ready = opponent_data["ready"]

    if ready:  # Оба готовы - начинаем игру
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*GameButtons.kmn.values())
        insert_users_in_game(
            user_ids=(call.message.chat.id, opponent_id),
            state=KMNState.game_process,
            text="Игра началась!",
            markup=markup,
        )
        do_game_loop(call.message.chat.id, opponent_id)
    else:
        bot.send_message(call.message.chat.id, text="Ожидаем ставку соперника")


def insert_users_in_game(
    user_ids: Union[list[int], tuple[int]],
    state: State,
    text: str,
    markup: types.ReplyKeyboardMarkup,
):
    for user_id in user_ids:
        bot.set_state(user_id, state)
        with bot.retrieve_data(user_id) as data:
            data["ready"] = False
            data["lives"] = 2
        bot.send_message(user_id, text=text, reply_markup=markup)


def do_game_loop(user_id, opponent_id):
    # bot.set_state(user_id, KMNState.game_process)
    # bot.set_state(opponent_id, KMNState.game_process)
    # # Сохраняем данные перед запуском потока
    # with bot.retrieve_data(user_id) as user_data:
    #     user_data["ready"] = False
    #     user_data["lives"] = 2  # get("lives", 2)
    #
    #     # bot.storage.set_data(user_id, user_data)
    #     # bot.storage.set_data(opponent_id, opponent_data)
    # with bot.retrieve_data(opponent_id) as opponent_data:
    #     opponent_data["ready"] = False
    #     opponent_data["lives"] = 2
    #
    # markup = ReplyKeyboardMarkup()
    # markup.add(*GameButtons.kmn.values())
    #
    # bot.send_message(
    #     user_id, "Игра началась! У вас 10 секунд чтобы сделать ход", reply_markup=markup
    # )
    # bot.send_message(
    #     opponent_id,
    #     "Игра началась! У вас 10 секунд чтобы сделать ход",
    #     reply_markup=markup,
    # )

    # Запускаем поток с таймером
    game_thread = threading.Thread(
        target=run_game_timer, args=(user_id, opponent_id, 10)
    )
    game_thread.start()
    print("конец")


def run_game_timer(user_id, opponent_id, timeout) -> None:
    """Отдельный поток с таймером"""
    stop_tread = False
    reward = 0
    while True:
        bot.send_message(
            user_id,
            text="Сделайте ход в течении 10 секунд.",
        )
        bot.send_message(
            opponent_id,
            text="Сделайте ход в течении 10 секунд.",
        )
        time.sleep(timeout)

        # Получаем свежие данные
        with (
            bot.retrieve_data(user_id) as user_data,
            bot.retrieve_data(opponent_id) as opponent_data,
        ):
            # Проверяем готовность
            if not user_data.get("ready", False):
                send_round_results(opponent_id, user_id)
                print("user loose")
                user_data["lives"] -= 1

            if not opponent_data.get("ready", False):
                send_round_results(user_id, opponent_id)
                print("opponent loose")
                opponent_data["lives"] -= 1

            # сброс
            user_data["ready"] = False
            opponent_data["ready"] = False

            if user_data["lives"] <= 0:
                stop_tread = True
                # reward = user_data["deposit"]
                # winner_id = opponent_id

                # send_results(opponent_id, user_data)

                # update balance у обоих
                # back to lobby функция
            elif opponent_data["lives"] <= 0:
                stop_tread = True
                # reward = opponent_data["deposit"]
                # winner_id = user_id

        if stop_tread:
            # update_balance(
            #     opponent_id if user_id == winner_id else user_id,
            #     new_balance=get_balance(user_id) - reward,
            # )
            # update_balance(winner_id, new_balance=get_balance(opponent_id) + reward)
            exit_to_navigation(user_id)
            exit_to_navigation(opponent_id)
            return
            # то же самое

    # do_game_loop(user_id, opponent_id)


@bot.message_handler(
    state=KMNState.game_process,
    func=lambda message: message.text in (GameButtons.kmn.values()),
)
def fight(message: types.Message):
    # раздаем True false
    with bot.retrieve_data(message.chat.id) as user_data:
        user_data["ready"] = True
        opponent_id = user_data.get("opponent_id")

        with bot.retrieve_data(opponent_id) as opponent_data:
            if opponent_data.get("ready"):
                damage_looser(
                    user_data=(user_data, message.text),
                    opponent_data=(opponent_data, opponent_data.get("response")),
                )

            else:
                user_data["response"] = message.text


def damage_looser(user_data: tuple[dict, str], opponent_data: tuple[dict, str]) -> None:
    user_id, opponent_id = opponent_data[0]["opponent_id"], user_data[0]["opponent_id"]
    if user_data[1] == opponent_data[1]:
        logger.info("Draw")
        send_draw(user_id, opponent_id)
        return
    elif (user_data[1], opponent_data[1]) in KMN_WIN_POSITIONS:
        opponent_data[0]["lives"] -= 1
        send_round_results(user_id, opponent_id)
        logger.info(f"User {opponent_data[0]["opponent_name"]} wins")

    elif (opponent_data[1], user_data[1]) in KMN_WIN_POSITIONS:
        user_data[0]["lives"] -= 1
        send_round_results(opponent_id, user_id)
        logger.info(f"User {user_data[0]["opponent_name"]} wins")

    else:
        logger.warning(f"In kmn random symbols {user_data[1], opponent_data[1]}")


def send_round_results(winner_id, looser_id):
    bot.send_message(winner_id, text="В данном раунде вы победили")
    bot.send_message(looser_id, text="В данном раунде вы проиграли")


def send_results(winner_id, looser_id):
    bot.send_message(winner_id, text="Вы победили!")
    bot.send_message(looser_id, text="Эх, проиграли!")


def send_draw(user_id, opponent_id):
    bot.send_message(user_id, text="В данном раунде: Ничья")
    bot.send_message(opponent_id, text="В данном раунде: Ничья")
