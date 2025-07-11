class CommonButtons:
    navigation = {
        "games": "🎮 Play",
        "rating": "🏆 Rating",
        "profile": "🐵 Profile and Balance",
    }
    games = {"saper": "💣 Saper", "red_black": "❤️ Red | Black ♠️"}


class GameButtons:
    kmn: dict = {"stone": "Камень", "scissors": "Ножницы", "paper": "Бумага"}
    red_black: dict = {"red": "❤️ Красное", "black": "♠️ Черное", "green": "🍀 Зелёное"}
    continue_game: dict = {"accept": "Еще одну", "refuse": "Хватит"}
    exit: str = "Завершить игру"


class BalanceData:
    start: int = 10000
    minimum: int = 100
    middle: int = 500
    middle_plus: int = 2500
    high: int = 5000


class CallbackDataString:
    deposit: str = "deposit"


KMN_WIN_POSITIONS = (
    (GameButtons.kmn["stone"], GameButtons.kmn["scissors"]),
    (GameButtons.kmn["paper"], GameButtons.kmn["stone"]),
    (GameButtons.kmn["scissors"], GameButtons.kmn["paper"]),
)
