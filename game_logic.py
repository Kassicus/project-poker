import random
from typing import List, Tuple
from models import Card

class PokerHand:
    @staticmethod
    def evaluate_hand(hole_cards: List[Card], community_cards: List[Card]) -> Tuple[int, List[int]]:
        """
        Evaluate a poker hand and return a tuple of (hand_rank, kickers)
        hand_rank: 0 (high card) to 9 (royal flush)
        kickers: list of card values used to break ties
        """
        all_cards = hole_cards + community_cards
        values = [card.value for card in all_cards]
        suits = [card.suit for card in all_cards]
        
        # Convert values to numbers for easier comparison
        value_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                    '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        numeric_values = [value_map[v] for v in values]
        
        # Check for flush
        flush = any(suits.count(suit) >= 5 for suit in set(suits))
        
        # Check for straight
        unique_values = sorted(set(numeric_values))
        straight = False
        for i in range(len(unique_values) - 4):
            if unique_values[i+4] - unique_values[i] == 4:
                straight = True
                break
        
        # Royal flush
        if flush and straight and max(numeric_values) == 14 and min(numeric_values) == 10:
            return (9, [])
        
        # Straight flush
        if flush and straight:
            return (8, [max(numeric_values)])
        
        # Four of a kind
        for value in set(numeric_values):
            if numeric_values.count(value) == 4:
                kickers = [v for v in numeric_values if v != value]
                return (7, [value] + sorted(kickers, reverse=True)[:1])
        
        # Full house
        three_kind = None
        pair = None
        for value in set(numeric_values):
            count = numeric_values.count(value)
            if count == 3:
                three_kind = value
            elif count == 2:
                pair = value
        if three_kind and pair:
            return (6, [three_kind, pair])
        
        # Flush
        if flush:
            flush_values = [v for v, s in zip(numeric_values, suits) 
                          if s == max(set(suits), key=suits.count)]
            return (5, sorted(flush_values, reverse=True)[:5])
        
        # Straight
        if straight:
            return (4, [max(numeric_values)])
        
        # Three of a kind
        if three_kind:
            kickers = [v for v in numeric_values if v != three_kind]
            return (3, [three_kind] + sorted(kickers, reverse=True)[:2])
        
        # Two pair
        pairs = [v for v in set(numeric_values) if numeric_values.count(v) == 2]
        if len(pairs) >= 2:
            pairs.sort(reverse=True)
            kickers = [v for v in numeric_values if v not in pairs[:2]]
            return (2, pairs[:2] + sorted(kickers, reverse=True)[:1])
        
        # One pair
        if pair:
            kickers = [v for v in numeric_values if v != pair]
            return (1, [pair] + sorted(kickers, reverse=True)[:3])
        
        # High card
        return (0, sorted(numeric_values, reverse=True)[:5])

class GameLogic:
    @staticmethod
    def shuffle_deck(deck: List[Card]) -> List[Card]:
        """Shuffle the deck of cards"""
        return random.sample(deck, len(deck))
    
    @staticmethod
    def deal_cards(deck: List[Card], num_players: int) -> Tuple[List[List[Card]], List[Card]]:
        """Deal 2 cards to each player and return the remaining deck"""
        hands = [[] for _ in range(num_players)]
        for _ in range(2):
            for i in range(num_players):
                if deck:
                    hands[i].append(deck.pop())
        return hands, deck
    
    @staticmethod
    def deal_community_cards(deck: List[Card], num_cards: int) -> Tuple[List[Card], List[Card]]:
        """Deal community cards and return the remaining deck"""
        community = []
        for _ in range(num_cards):
            if deck:
                community.append(deck.pop())
        return community, deck
    
    @staticmethod
    def get_winner(players: List[dict], community_cards: List[Card]) -> List[int]:
        """
        Determine the winner(s) of the hand
        Returns a list of player indices who won (for split pots)
        """
        best_hand = -1
        winners = []
        
        for i, player in enumerate(players):
            if player['folded']:
                continue
                
            hand_rank, kickers = PokerHand.evaluate_hand(player['hand'], community_cards)
            
            if hand_rank > best_hand:
                best_hand = hand_rank
                winners = [i]
            elif hand_rank == best_hand:
                # Compare kickers
                if kickers > winners_kickers:
                    winners = [i]
                elif kickers == winners_kickers:
                    winners.append(i)
                winners_kickers = kickers
        
        return winners 