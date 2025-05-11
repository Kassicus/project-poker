import pygame
import sys
from typing import List, Tuple, Optional
from game_logic import GameLogic, PokerHand
from ui import UI
from models import Card, Player

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900  # Changed to create a 16:9 aspect ratio with WINDOW_WIDTH
CARD_WIDTH = 100
CARD_HEIGHT = 140
FPS = 60

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
WHITE = (255, 255, 255)

class PokerGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Poker Game")
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)
        self.players: List[Player] = []
        self.deck: List[Card] = []
        self.community_cards: List[Card] = []
        self.current_player = 0
        self.pot = 0
        self.current_bet = 0
        self.small_blind = 10
        self.big_blind = 20
        self.dealer = 0
        self.game_phase = "preflop"  # preflop, flop, turn, river, showdown
        self.setup_game()

    def setup_game(self):
        # Create players in a horizontal line across the middle of the screen
        center_y = WINDOW_HEIGHT // 2
        # Add margins on the sides and divide remaining space into 4 sections
        margin = 200  # Increased margin from screen edges
        usable_width = WINDOW_WIDTH - (2 * margin)
        spacing = usable_width // 3  # Divide into 3 spaces for 4 players
        
        positions = [
            (margin, center_y),                    # Player 1 (left)
            (margin + spacing, center_y),          # Player 2
            (margin + (spacing * 2), center_y),    # Player 3
            (margin + (spacing * 3), center_y)     # Player 4 (right)
        ]
        
        for i in range(4):
            self.players.append(Player(f"Player {i+1}", positions[i]))

        self.start_new_hand()

    def start_new_hand(self):
        # Reset game state
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.game_phase = "preflop"
        
        # Reset player states
        for player in self.players:
            player.hand = []
            player.bet = 0
            player.folded = False
            player.is_all_in = False

        # Initialize and shuffle deck
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = [Card(suit, value) for suit in suits for value in values]
        self.deck = GameLogic.shuffle_deck(self.deck)

        # Deal cards
        hands, self.deck = GameLogic.deal_cards(self.deck, len(self.players))
        for i, player in enumerate(self.players):
            player.hand = hands[i]
            for card in player.hand:
                card.face_up = True

        # Post blinds
        sb_pos = (self.dealer + 1) % len(self.players)
        bb_pos = (self.dealer + 2) % len(self.players)
        
        self.players[sb_pos].chips -= self.small_blind
        self.players[sb_pos].bet = self.small_blind
        self.players[bb_pos].chips -= self.big_blind
        self.players[bb_pos].bet = self.big_blind
        
        self.pot = self.small_blind + self.big_blind
        self.current_bet = self.big_blind
        self.current_player = (bb_pos + 1) % len(self.players)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    action = self.ui.handle_click(event.pos)
                    if action:
                        self.handle_player_action(action)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    self.ui.handle_mouse_up()
            elif event.type == pygame.MOUSEMOTION:
                self.ui.handle_mouse_motion(event.pos)
        return True

    def handle_player_action(self, action: str):
        current_player = self.players[self.current_player]
        
        if action == "fold":
            current_player.folded = True
            # Hide the player's cards when they fold
            for card in current_player.hand:
                card.face_up = False
            self.next_player()
            
        elif action == "check":
            # Only allow check if no bet has been made in this round
            if self.current_bet == current_player.bet:
                self.next_player()
            else:
                # If there's a bet, this should be a call instead
                self.handle_call(current_player)
                
        elif action == "call":
            self.handle_call(current_player)
            
        elif action == "raise":
            # Minimum raise must be at least the size of the previous bet/raise
            min_raise = self.current_bet + (self.current_bet - current_player.bet)
            max_raise = current_player.chips + current_player.bet
            raise_amount = self.ui.get_bet_amount(min_raise, max_raise)
            
            if raise_amount > self.current_bet:
                self.current_bet = raise_amount
                call_amount = raise_amount - current_player.bet
                
                if current_player.chips >= call_amount:
                    current_player.chips -= call_amount
                    current_player.bet += call_amount
                    self.pot += call_amount
                else:
                    # All-in
                    all_in_amount = current_player.chips
                    current_player.chips = 0
                    current_player.bet += all_in_amount
                    self.pot += all_in_amount
                    current_player.is_all_in = True
                self.next_player()

    def handle_call(self, player: Player):
        """Handle a call action for a player"""
        call_amount = self.current_bet - player.bet
        if call_amount > 0:
            if player.chips >= call_amount:
                player.chips -= call_amount
                player.bet += call_amount
                self.pot += call_amount
            else:
                # All-in
                all_in_amount = player.chips
                player.chips = 0
                player.bet += all_in_amount
                self.pot += all_in_amount
                player.is_all_in = True
        self.next_player()

    def get_active_players(self) -> List[Player]:
        """Get list of players who haven't folded"""
        return [p for p in self.players if not p.folded]

    def next_player(self):
        # Find next active player
        next_player = (self.current_player + 1) % len(self.players)
        active_players = self.get_active_players()
        
        # If only one player remains, go to showdown
        if len(active_players) == 1:
            self.showdown()
            return
            
        # Skip folded players and players who are all-in
        while (self.players[next_player].folded or 
               self.players[next_player].is_all_in):
            next_player = (next_player + 1) % len(self.players)
            if next_player == self.current_player:
                # Round is complete
                self.next_phase()
                return
        
        # Check if we've completed a round of betting
        if self.is_betting_round_complete():
            self.next_phase()
            return
        
        self.current_player = next_player

    def is_betting_round_complete(self) -> bool:
        """Check if the current betting round is complete according to Texas Hold'em rules."""
        active_players = self.get_active_players()
        
        # If only one player remains, round is complete
        if len(active_players) == 1:
            return True
            
        # Get the last player to act in this round (varies by phase)
        last_to_act = self.get_last_to_act()
        
        # If we've gone all the way around to the last player to act
        if self.current_player == last_to_act:
            # Check if all active players have either:
            # 1. Matched the current bet
            # 2. Are all-in
            # 3. Have folded
            for player in active_players:
                if not player.folded and not player.is_all_in and player.bet != self.current_bet:
                    return False
            return True
            
        # If we've gone all the way around and all active players have acted
        if self.have_all_active_players_acted():
            # Check if all active players have either:
            # 1. Matched the current bet
            # 2. Are all-in
            # 3. Have folded
            for player in active_players:
                if not player.folded and not player.is_all_in and player.bet != self.current_bet:
                    return False
            return True
            
        return False

    def have_all_active_players_acted(self) -> bool:
        """Check if all active players have had a chance to act in the current betting round."""
        active_players = self.get_active_players()
        if not active_players:
            return True
            
        # Get the last player to act in this round
        last_to_act = self.get_last_to_act()
        
        # If we've gone all the way around to the last player to act
        if self.current_player == last_to_act:
            return True
            
        # Check if we've gone all the way around the table
        # Start from the last player who made a bet/raise
        last_bettor = self.get_last_bettor()
        if last_bettor is None:
            return False
            
        # If we've gone all the way around from the last bettor
        return self.current_player == last_bettor

    def get_last_bettor(self) -> Optional[int]:
        """Get the position of the last player who made a bet or raise."""
        active_players = self.get_active_players()
        if not active_players:
            return None
            
        # Find the last player who made a bet
        last_bettor = None
        for i, player in enumerate(self.players):
            if not player.folded and player.bet == self.current_bet:
                last_bettor = i
                
        return last_bettor

    def get_last_to_act(self) -> int:
        """Determine who should be the last to act in the current betting round."""
        if self.game_phase == "preflop":
            # In preflop, the big blind acts last
            return (self.dealer + 2) % len(self.players)
        else:
            # In other phases, the dealer acts last
            return self.dealer

    def next_phase(self):
        if self.game_phase == "preflop":
            self.game_phase = "flop"
            self.deal_community_cards(3)
        elif self.game_phase == "flop":
            self.game_phase = "turn"
            self.deal_community_cards(1)
        elif self.game_phase == "turn":
            self.game_phase = "river"
            self.deal_community_cards(1)
        elif self.game_phase == "river":
            self.game_phase = "showdown"
            self.showdown()
            return

        # Reset betting for new phase
        self.current_bet = 0
        for player in self.players:
            player.bet = 0
            
        # Find first active player after dealer
        active_players = self.get_active_players()
        if not active_players:
            self.showdown()
            return
            
        # Set current player to first active player after dealer
        self.current_player = (self.dealer + 1) % len(self.players)
        while self.players[self.current_player].folded:
            self.current_player = (self.current_player + 1) % len(self.players)

    def deal_community_cards(self, num_cards: int):
        cards, self.deck = GameLogic.deal_community_cards(self.deck, num_cards)
        for card in cards:
            card.face_up = True
        self.community_cards.extend(cards)

    def showdown(self):
        # Find winner(s)
        active_players = self.get_active_players()
        if len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.pot
        else:
            # Evaluate hands and determine winner(s)
            player_hands = []
            for player in active_players:
                hand_rank, kickers = PokerHand.evaluate_hand(player.hand, self.community_cards)
                player_hands.append((player, hand_rank, kickers))
            
            # Sort by hand rank and kickers
            player_hands.sort(key=lambda x: (x[1], x[2]), reverse=True)
            
            # Split pot among winners
            best_hand_rank = player_hands[0][1]
            best_kickers = player_hands[0][2]
            winners = [p for p, rank, kickers in player_hands 
                      if rank == best_hand_rank and kickers == best_kickers]
            
            split_amount = self.pot // len(winners)
            for winner in winners:
                winner.chips += split_amount

        # Start new hand
        self.dealer = (self.dealer + 1) % len(self.players)
        self.start_new_hand()

    def draw(self):
        self.screen.fill(GREEN)
        
        # Draw community cards at the top
        self.ui.draw_community_cards(self.community_cards, WINDOW_WIDTH // 2, 100)
        
        # Draw pot in upper right corner
        self.ui.draw_pot(self.pot, WINDOW_WIDTH - 150, 50)
        
        # Draw players
        for i, player in enumerate(self.players):
            is_dealer = i == self.dealer
            is_small_blind = i == (self.dealer + 1) % len(self.players)
            is_big_blind = i == (self.dealer + 2) % len(self.players)
            self.ui.draw_player(
                player, 
                i == self.current_player,
                is_dealer,
                is_small_blind,
                is_big_blind
            )
        
        # Draw UI elements
        self.ui.draw_buttons()
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = PokerGame()
    game.run()
    pygame.quit()
    sys.exit()