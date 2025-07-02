from abc import ABC, abstractmethod, abstractproperty
from typing import Union
from telebot import types

class UniversalKeyboard(ABC):
    def __init__(self, buttons: Union[list[str], tuple[str]], row_width: int = 2):
        self._markup = self._create_markup()
        self._row_width = row_width
        self._buttons = buttons
        self._create()

    @abstractmethod
    def _create_markup(self):
        pass

    @abstractmethod
    def _create(self):
        pass

    @property
    def markup(self):
        return self._markup


class UniversalReplyKeyboard(UniversalKeyboard):
    def _create(self) -> None:
        self._markup.add(*self._buttons, row_width=self._row_width)

    def _create_markup(self) -> types.ReplyKeyboardMarkup:
        return types.ReplyKeyboardMarkup(resize_keyboard=True)