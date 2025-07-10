from telebot import types, State
from typing import Optional, Union
from datetime import datetime

from bot.config.settings import bot, NAVIGATION_BUTTONS
from bot.core.states.common import UserState
from bot.core.utils.helpers import transition_need_state, transition_remove_keyboard


@bot.message_handler(state=UserState.echo, content_types=["text"])
def handle_echo(message: types.Message):
    """
    Обрабатывает и выводит текст введенный пользователем
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, text=f"Я получил сообщение {message.text}")


def make_button_handlers(
    button: str,
    need_state: State,
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
        if text is None:
            transition_remove_keyboard(
                message, need_state=need_state, text=f"Состояние {button}"
            )
        else:
            transition_need_state(
                message.chat.id, need_state=need_state, text=text, buttons=buttons
            )

    return handler


DATE_TIME_BUTTONS = {"date": "Дата", "time": "Время"}

button_handler_1 = make_button_handlers(
    NAVIGATION_BUTTONS["echo"], need_state=UserState.echo
)
button_handler_2 = make_button_handlers(
    NAVIGATION_BUTTONS["date_time"],
    need_state=UserState.date_time,
    text="Что вы хотите узнать: дату или время",
    buttons=DATE_TIME_BUTTONS.values(),
)


@bot.message_handler(
    state=UserState.date_time,
    func=lambda message: message.text == DATE_TIME_BUTTONS["date"],
)
def show_current_date(message: types.Message):
    bot.send_message(
        message.chat.id, text=datetime.today().strftime("📅 Дата: %d.%m.%Y")
    )


@bot.message_handler(
    state=UserState.date_time,
    func=lambda message: message.text == DATE_TIME_BUTTONS["time"],
)
def show_current_date(message: types.Message):
    bot.send_message(
        message.chat.id, text=datetime.today().strftime("🕒 Время: %H:%M:%S")
    )
