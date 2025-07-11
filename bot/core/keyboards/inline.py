from typing import Union
from telebot import types

from bot.config.config_data import BalanceData, CallbackDataString
from bot.config.settings import bot
from database.crud import get_balance


# class InlineDepositKeyboards:
#     def __init__(self, player_chat_id: int, opponent_chat_id: int) -> None:
#         player_balance, opponent_balance = self._get_balances(
#             player_chat_id, opponent_chat_id
#         )
#         self._player_markup = types.InlineKeyboardMarkup(
#             keyboard=self._get_buttons_by_balance(player_balance)
#         )
#         self._opponent_markup = types.InlineKeyboardMarkup(
#             keyboard=self._get_buttons_by_balance(opponent_balance)
#         )
#
#     @staticmethod
#     def _get_balances(user_id: int, opp_id: int) -> tuple[int, int]:
#         user_balance = get_balance(chat_id=user_id)
#         opponent_balance = get_balance(chat_id=opp_id)
#         print(user_balance, opponent_balance)
#         return user_balance, opponent_balance
#
#     @staticmethod
#     def _get_buttons_by_balance(
#         balance: int,
#     ) -> list[list[types.InlineKeyboardButton]]: ...
#
#     @property
#     def player_markup(self):
#         return self._player_markup
#
#     @property
#     def opponent_markup(self):
#         return self._opponent_markup


class InlineDepositKeyboard(types.InlineKeyboardMarkup):
    def __init__(self, chat_id: int) -> None:
        balance = get_balance(chat_id=chat_id)
        super().__init__(keyboard=self._get_buttons_by_balance(balance))

    @staticmethod
    def _get_buttons_by_balance(
        balance: int,
    ) -> list[list[types.InlineKeyboardButton]]:
        # придумать что с offline и как тогда пополнять баланс
        # последняя all in
        # if balance in range(BalanceData.minimum, BalanceData.middle):
        #     return [[types.InlineKeyboardButton(text=f"${balance}", callback_data=f"deposit:{balance}")]]
        # elif abs(BalanceData.minimum - balance) <= 250:
        #     buttons = [[BalanceData.minimum,], [], []]
        # else:
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
