from abc import ABC, abstractmethod
from telebot import TeleBot
from telebot.types import Message
from telebot.states import State

from bot.config.config_data import BalanceData, GameButtons
from bot.config.settings import redis_sessions
from bot.core.keyboards.inline import InlineDepositKeyboard
from bot.core.utils.helpers import transition_game_state, transition_need_state
from database.crud import get_balance


class Player(ABC):
    def __init__(self, username: str, chat_id: int):
        self._username: str = username
        self._chat_id: int = chat_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def chat_id(self) -> int:
        return self._chat_id

    def pack_player_string(self) -> str:
        return f"{self._chat_id}:{self._username}"

    def __str__(self) -> str:
        return f"Player {self._username}, id: {self._chat_id} "


class MessagePlayer(Player):
    def __init__(self, message: Message):
        self._message: Message = message
        super().__init__(
            username=self._message.from_user.username, chat_id=message.chat.id
        )


class StringPlayer(Player):
    def __init__(self, string: str):
        self._string: str = string
        super().__init__(*self._unpack_player_string(string))

    @property
    def string(self) -> str:
        return self._string

    @staticmethod
    def _unpack_player_string(string: str) -> tuple[str, int]:
        id, name = string.split(":")
        return name, int(id)


class GameSession(ABC):
    def __init__(
        self, bot: TeleBot, message: Message, game_state: State, start_text: str
    ):
        self._bot: TeleBot = bot
        self._message: Message = message
        self._player: Player = MessagePlayer(message)
        self._game_state: State = game_state
        self._start_text: str = start_text

    @abstractmethod
    def _start_game(self):
        pass

    @abstractmethod
    def _provide_deposits(self):
        pass


class MultiplayerSession(GameSession):
    def __init__(
        self,
        bot: TeleBot,
        message: Message,
        game_redis_name: str,
        game_state: State,
        start_text: str,
    ):
        self._game_name: str = game_redis_name
        super().__init__(bot, message, game_state, start_text)
        self._search_session()

    @abstractmethod
    def _start_game(self) -> None:
        pass

    def _provide_deposits(self, opponent: Player) -> None:
        self._bot.send_message(
            self._player.chat_id,
            text="Сделайте ставку",
            reply_markup=InlineDepositKeyboard(chat_id=self._player.chat_id),
        )
        self._bot.send_message(
            opponent.chat_id,
            text="Сделайте ставку",
            reply_markup=InlineDepositKeyboard(chat_id=opponent.chat_id),
        )

    def _search_session(self) -> None:
        balance = get_balance(self._player.chat_id)
        if balance < BalanceData.minimum:
            self._bot.send_message(
                self._player.chat_id,
                text=f"Вы не можете играть multiplayer.\nМинимальная ставка ${BalanceData.minimum}\nВаш баланс ${balance}\nВам не хватает всего лишь: ${BalanceData.minimum - balance}",
            )
            return
        session = redis_sessions.lrange("session:" + self._game_name, 0, -1)
        print(session, session.__class__)
        if self._player.pack_player_string() in session:
            self._bot.send_message(
                self._player.chat_id, text="Вы уже в очереди для данной игры"
            )
            return

        if not session or len(session) == 0:
            redis_sessions.rpush(
                "session:" + self._game_name, self._player.pack_player_string()
            )
            self._bot.send_message(
                self._message.chat.id, text="Вы были добавлены в очередь."
            )
        elif len(session) >= 1:
            opponent, *new_session = session
            redis_sessions.delete("session:" + self._game_name)
            if new_session:
                redis_sessions.rpush("session:" + self._game_name, *new_session)
            self._start_game(opponent=StringPlayer(string=opponent))


class OnePlayerSession(GameSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_game()

    def _search_session(self) -> None: ...

    def _provide_deposits(self) -> None:
        self._bot.send_message(
            self._player.chat_id,
            text="Сделайте ставку",
            reply_markup=InlineDepositKeyboard(chat_id=self._player.chat_id),
        )

    def _start_game(self) -> None:
        transition_need_state(
            self._player.chat_id,
            self._game_state,
            text=self._start_text,
            buttons=(GameButtons.exit,),
        )
        self._provide_deposits()


class GameTimerSession(MultiplayerSession):
    round_time = 10

    def _start_game(self, opponent: Player) -> None:
        transition_game_state(
            self._player, self._game_state, self._start_text, opponent
        )
        # super()._start_game()
        super()._provide_deposits(opponent=opponent)
        ## какая-то дополнительная логика


class GameAlternateSession(MultiplayerSession): ...
