from telebot.states import StatesGroup, State


class UserState(StatesGroup):
    navigation = State()
    games = State()
    profile = State()


class GameState(StatesGroup):
    black_jack = State()
    saper = State()
    test = State()


class KMNState(StatesGroup):
    balance = State()
    game_process = State()
    finish = State()  ## нужен или нет


class RedBlackState(StatesGroup):
    balance = State()
    game_process = State()
