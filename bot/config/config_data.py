class CommonButtons:
    navigation = {
        "games": "🎮 Play",
        "rating": "🏆 Rating",
        "profile": "🐵 Profile and Balance",
    }
    games = {"saper": "💣 Saper", "red_black": "Red | Black"}


class GameButtons:
    kmn = {"stone": "Камень", "scissors": "Ножницы", "paper": "Бумага"}


class BalanceData:
    start: int = 100
    minimum: int = 100
    middle: int = 1000
    high: int = 5000


class CallbackDataString:
    deposit: str = "deposit"


KMN_WIN_POSITIONS = (
    (GameButtons.kmn["stone"], GameButtons.kmn["scissors"]),
    (GameButtons.kmn["paper"], GameButtons.kmn["stone"]),
    (GameButtons.kmn["scissors"], GameButtons.kmn["paper"]),
)
