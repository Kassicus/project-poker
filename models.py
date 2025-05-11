from typing import List, Tuple

class Card:
    def __init__(self, suit: str, value: str):
        self.suit = suit
        self.value = value
        self.face_up = False
        self.image = None
        self.rect = None

    def __str__(self):
        return f"{self.value} of {self.suit}"

class Player:
    def __init__(self, name: str, position: Tuple[int, int]):
        self.name = name
        self.position = position
        self.hand: List[Card] = []
        self.chips = 1000
        self.bet = 0
        self.folded = False
        self.is_all_in = False 