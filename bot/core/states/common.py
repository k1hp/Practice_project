from telebot.states import StatesGroup, State


class UserState(StatesGroup):
    """
    Состояния навигации.
    """
    navigation = State()
    games = State()
    profile = State()


class KMNState(StatesGroup):
    """
    При наследовании от общего класса появляется непредсказуемость.
    Состояния для игры Камни Ножницы Бумага
    """
    balance = State()
    game_process = State()
    finish = State()  ## нужен или нет


class RedBlackState(StatesGroup):
    """
    При наследовании от общего класса появляется непредсказуемость.
    Состояния для игры Red | Black
    """

    balance = State()
    game_process = State()


class SaperState(StatesGroup):
    """
    При наследовании от общего класса появляется непредсказуемость.
    Состояния для игры Saper
    """

    balance = State()
    game_process = State()
