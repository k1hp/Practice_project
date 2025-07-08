from telebot.states import StatesGroup, State


class UserState(StatesGroup):
    navigation = State()
    games = State()
    profile = State()
