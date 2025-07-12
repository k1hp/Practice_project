import random
from abc import abstractmethod, ABC
from telebot import types
from telebot.types import InlineKeyboardButton

from bot.config.config_data import BalanceData, CallbackDataString
from database.crud import get_balance


class CustomInlineKeyboard(ABC, types.InlineKeyboardMarkup):
    @abstractmethod
    def _create(self) -> list[list[types.InlineKeyboardButton]]:
        pass


class InlineDepositKeyboard(CustomInlineKeyboard):
    def __init__(self, chat_id: int) -> None:
        self._balance = get_balance(chat_id=chat_id)
        super().__init__(keyboard=self._create())

    def _create(self):
        return self._get_buttons_by_balance(self._balance)

    @staticmethod
    def _get_buttons_by_balance(
        balance: int,
    ) -> list[list[types.InlineKeyboardButton]]:
        result = []
        deposits = []
        for stage in (
            BalanceData.minimum,
            BalanceData.middle,
            BalanceData.middle_plus,
            BalanceData.high,
        ):
            if len(deposits) == 2:
                result.append(deposits)
                deposits = []
            if balance >= stage:
                deposits.append(
                    types.InlineKeyboardButton(
                        text=f"${stage}",
                        callback_data=f"{CallbackDataString.deposit}:{stage}",
                    )
                )
        result.append(deposits)
        result.append(
            [
                types.InlineKeyboardButton(
                    text=f"All In",
                    callback_data=f"{CallbackDataString.deposit}:{balance}",
                ),
            ]
        )
        return result


class InlineSaperKeyboard(CustomInlineKeyboard):
    """
    Создает поле (по умолчанию 5 x 5)
    С указанным количеством бомб
    Для игры в сапера.
    """

    def __init__(self, bombs_count: int, sight: int = 5):
        self._sight = sight
        self._bombs_count = bombs_count
        super().__init__(keyboard=self._create())

    def _create(self) -> list[list[types.InlineKeyboardButton]]:
        result = []
        counter = 0
        bomb_numbers: list[int] = self._generate_bomb_numbers(
            self._bombs_count, self._sight
        )
        for high in range(0, self._sight):
            buffer = []
            for length in range(0, self._sight):
                if counter in bomb_numbers:
                    buffer.append(
                        InlineKeyboardButton(
                            text="🛡️", callback_data=f"{CallbackDataString.cell}:bomb"
                        )
                    )
                else:
                    buffer.append(
                        InlineKeyboardButton(
                            text="🛡️",
                            callback_data=f"{CallbackDataString.cell}:{counter}",
                        )
                    )
                counter += 1
            result.append(buffer)

        return result

    @staticmethod
    def _generate_bomb_numbers(bombs_count: int, sight: int) -> list[int]:
        numbers: tuple[int] = tuple(range(sight * sight))
        return random.choices(numbers, k=bombs_count)


class InlineBombsKeyboard(CustomInlineKeyboard):
    """
    Клавиатура для выбора количества бомб на поле.
    """

    def __init__(self, row_width: int = 3, sight: int = 5):
        self._sight = sight
        self._size = sight * sight
        self._row_width = row_width
        super().__init__(keyboard=self._create())

    def _create(self) -> list[list[types.InlineKeyboardButton]]:
        result = []
        counter = 0
        buffer = []
        for index in range(self._size):
            if counter == self._row_width:
                result.append(buffer)
                buffer = []
                counter = 0
            number = 2**index

            if number >= self._size:
                result.append(buffer)
                break
            else:
                buffer.append(
                    InlineKeyboardButton(
                        text=f"x{number}",
                        callback_data=f"{CallbackDataString.bombs}:{number}",
                    )
                )
            counter += 1
        result.append(
            [
                InlineKeyboardButton(
                    text=f"x{self._size - 1}",
                    callback_data=f"{CallbackDataString.bombs}:{self._size - 1}",
                )
            ],
        )
        return result
