from telebot.states import StatesGroup, State


class UserState(StatesGroup):
    navigation = State()
    echo = State()
    date_time = State()