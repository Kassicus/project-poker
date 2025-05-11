import pygame
import os
from typing import List, Tuple, Optional
from models import Card, Player

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

class UI:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.card_images = {}
        self.load_card_images()
        
        # Create buttons
        button_width = 150  # Increased button width
        button_height = 50  # Increased button height
        button_y = self.screen_height - 80  # Moved buttons down
        button_spacing = 30  # Increased spacing between buttons
        total_buttons_width = (button_width * 4) + (button_spacing * 3)
        start_x = (self.screen_width - total_buttons_width) // 2  # Center buttons
        
        self.fold_button = Button(start_x, button_y, button_width, button_height, "Fold", (255, 100, 100))
        self.check_button = Button(start_x + button_width + button_spacing, button_y, button_width, button_height, "Check", (100, 255, 100))
        self.call_button = Button(start_x + (button_width + button_spacing) * 2, button_y, button_width, button_height, "Call", (100, 100, 255))
        self.raise_button = Button(start_x + (button_width + button_spacing) * 3, button_y, button_width, button_height, "Raise", (255, 255, 100))
        
        # Betting slider
        slider_x = start_x + (button_width + button_spacing) * 4 + 30
        self.slider_rect = pygame.Rect(slider_x, button_y + 15, 250, 20)  # Increased slider width
        self.slider_pos = 0.5  # 0 to 1
        self.slider_dragging = False
        
    def load_card_images(self):
        """Load card images from a cards directory"""
        # Create cards directory if it doesn't exist
        if not os.path.exists('cards'):
            os.makedirs('cards')
            # TODO: Add code to generate card images if they don't exist
            
        # Load card images
        for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
            for value in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                image_path = f'cards/{value.lower()}_{suit.lower()}.png'
                if os.path.exists(image_path):
                    self.card_images[f"{value}_{suit}"] = pygame.image.load(image_path)
                else:
                    # Create a placeholder card with suit-specific colors
                    surf = pygame.Surface((100, 140))
                    surf.fill((255, 255, 255))
                    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
                    
                    # Set color based on suit
                    if suit == 'Hearts':
                        color = (255, 0, 0)  # Red
                    elif suit == 'Diamonds':
                        color = (255, 165, 0)  # Orange
                    elif suit == 'Clubs':
                        color = (0, 0, 255)  # Blue
                    else:  # Spades
                        color = (0, 0, 0)  # Black
                    
                    # Draw the card value
                    font = pygame.font.Font(None, 72)  # Larger font for better visibility
                    text = font.render(value, True, color)
                    text_rect = text.get_rect(center=surf.get_rect().center)
                    surf.blit(text, text_rect)
                    
                    self.card_images[f"{value}_{suit}"] = surf
    
    def draw_card(self, card: Card, pos: Tuple[int, int], face_up: bool = True):
        """Draw a card at the specified position"""
        if face_up and card.face_up:
            image = self.card_images.get(f"{card.value}_{card.suit}")
            if image:
                self.screen.blit(image, pos)
        else:
            # Draw card back
            pygame.draw.rect(self.screen, (0, 0, 100), pygame.Rect(pos[0], pos[1], 100, 140))
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(pos[0], pos[1], 100, 140), 2)
    
    def draw_blind_label(self, x: int, y: int, text: str, color: Tuple[int, int, int]):
        """Draw a label for blind positions inside a circle"""
        # Draw circle background
        circle_radius = 15
        pygame.draw.circle(self.screen, (50, 50, 50), (x, y), circle_radius)  # Dark gray background
        pygame.draw.circle(self.screen, color, (x, y), circle_radius - 2)  # Colored border
        
        # Draw text
        font = pygame.font.Font(None, 24)
        text_surface = font.render(text, True, (255, 255, 255))  # White text
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_player(self, player: Player, is_current_player: bool = False, is_dealer: bool = False, is_small_blind: bool = False, is_big_blind: bool = False):
        """Draw a player's information and cards"""
        # Draw cards with proper spacing
        card_spacing = 120  # Reduced spacing between cards
        total_cards_width = (len(player.hand) - 1) * card_spacing + 100  # 100 is card width
        start_x = player.position[0] - total_cards_width // 2
        
        # Draw cards first
        for i, card in enumerate(player.hand):
            card_pos = (start_x + (i * card_spacing), player.position[1] - 50)  # Moved cards up
            self.draw_card(card, card_pos)
            
        # Draw player name and chips below cards
        font = pygame.font.Font(None, 36)
        text_color = (255, 255, 0) if is_current_player else (255, 255, 255)
        text = font.render(f"{player.name} - Chips: {player.chips}", True, text_color)
        text_rect = text.get_rect(center=(player.position[0], player.position[1] + 150))  # Moved text further down
        self.screen.blit(text, text_rect)
            
        # Draw position indicators above cards
        if is_dealer:
            self.draw_blind_label(player.position[0], player.position[1] - 120, "D", (255, 255, 0))
        if is_small_blind:
            self.draw_blind_label(player.position[0], player.position[1] - 120, "SB", (0, 255, 0))
        if is_big_blind:
            self.draw_blind_label(player.position[0], player.position[1] - 120, "BB", (255, 0, 0))
    
    def draw_community_cards(self, cards: List[Card], x: int, y: int):
        """Draw community cards at the top of the screen"""
        for i, card in enumerate(cards):
            card_x = x - (len(cards) * 100 // 2) + (i * 100)
            self.draw_card(card, (card_x, y))
    
    def draw_pot(self, amount: int, x: int, y: int):
        """Draw pot amount below community cards"""
        font = pygame.font.Font(None, 48)
        text = font.render(f"Pot: ${amount}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(x, y))
        self.screen.blit(text, text_rect)
    
    def draw_buttons(self):
        """Draw the action buttons"""
        self.fold_button.draw(self.screen)
        self.check_button.draw(self.screen)
        self.call_button.draw(self.screen)
        self.raise_button.draw(self.screen)
        
        # Draw betting slider
        pygame.draw.rect(self.screen, (200, 200, 200), self.slider_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.slider_rect, 2)
        
        slider_handle_pos = (
            self.slider_rect.x + int(self.slider_rect.width * self.slider_pos),
            self.slider_rect.y + self.slider_rect.height // 2
        )
        pygame.draw.circle(self.screen, (0, 0, 0), slider_handle_pos, 10)
        
        # Draw current bet amount above slider
        font = pygame.font.Font(None, 36)
        current_bet = self.get_bet_amount(0, 1000)  # Example max bet of 1000
        bet_text = font.render(f"Bet: ${current_bet}", True, (255, 255, 255))
        bet_rect = bet_text.get_rect(center=(self.slider_rect.centerx, self.slider_rect.y - 20))
        self.screen.blit(bet_text, bet_rect)
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Handle mouse clicks and return the action taken"""
        if self.fold_button.is_clicked(pos):
            return "fold"
        elif self.check_button.is_clicked(pos):
            return "check"
        elif self.call_button.is_clicked(pos):
            return "call"
        elif self.raise_button.is_clicked(pos):
            return "raise"
        elif self.slider_rect.collidepoint(pos):
            self.slider_dragging = True
            self.slider_pos = (pos[0] - self.slider_rect.x) / self.slider_rect.width
            self.slider_pos = max(0, min(1, self.slider_pos))
        return None
    
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """Handle mouse motion for the betting slider"""
        if self.slider_dragging:
            # Calculate raw slider position
            raw_pos = (pos[0] - self.slider_rect.x) / self.slider_rect.width
            raw_pos = max(0, min(1, raw_pos))
            
            # Get current min and max bet values
            min_bet = 0  # This will be updated by the game logic
            max_bet = 1000  # This will be updated by the game logic
            
            # Calculate raw bet amount
            raw_bet = min_bet + int((max_bet - min_bet) * raw_pos)
            
            # Snap to nearest $10
            snapped_bet = round(raw_bet / 10) * 10
            
            # Update slider position to match the snapped value
            if max_bet > min_bet:
                self.slider_pos = (snapped_bet - min_bet) / (max_bet - min_bet)
    
    def handle_mouse_up(self):
        """Handle mouse button release"""
        self.slider_dragging = False
    
    def get_bet_amount(self, min_bet: int, max_bet: int) -> int:
        """Get the current bet amount from the slider, snapped to nearest $10"""
        # Calculate the raw bet amount
        raw_bet = min_bet + int((max_bet - min_bet) * self.slider_pos)
        
        # Snap to nearest $10
        snapped_bet = round(raw_bet / 10) * 10
        
        # Ensure we don't exceed max_bet
        snapped_bet = min(snapped_bet, max_bet)
        
        # Update slider position to match the snapped value
        if max_bet > min_bet:
            self.slider_pos = (snapped_bet - min_bet) / (max_bet - min_bet)
        
        return snapped_bet 