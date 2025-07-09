import pygame
import os
from PIL import Image  # Make sure Pillow is installed: pip install Pillow

# --- Pygame Initialization ---
pygame.init()

# --- Screen Dimensions (Adjust as needed, 1280x720 is a common desktop resolution) ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Blackjack")

# --- Asset Paths ---
# Make sure your images are in a folder named 'assets' next to your Python script
ASSET_PATH = 'assets'

# --- Colors (Primarily for dynamic text) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_LIGHT = (100, 255, 100)  # Not used in this version

# --- Fonts ---
font_large = pygame.font.Font(None, 80)
font_medium = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 30)
font_money = pygame.font.Font(None, 36)  # Slightly smaller for money display

# --- Load Assets ---
assets = {}


def load_image(filename, alpha=True, scale=None):
    """Helper function to load and optionally scale images."""
    path = os.path.join(ASSET_PATH, filename)
    try:
        img = pygame.image.load(path)
        if alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        if scale:
            img = pygame.transform.smoothscale(img, scale)
        return img
    except pygame.error as e:
        print(f"Error loading image {filename}: {e}")
        placeholder = pygame.Surface(scale or (50, 50))
        placeholder.fill((255, 0, 255))  # Magenta for missing image
        # Draw text for placeholder
        ph_font = pygame.font.Font(None, 20)
        ph_text = ph_font.render(filename.split('.')[0], True, BLACK)
        ph_text_rect = ph_text.get_rect(center=placeholder.get_rect().center)
        placeholder.blit(ph_text, ph_text_rect)
        return placeholder


# Background & Table Elements
assets['felt_background'] = load_image(
    'felt_background.png', alpha=False, scale=(SCREEN_WIDTH, SCREEN_HEIGHT))

try:
    rail_original_width, rail_original_height = Image.open(
        os.path.join(ASSET_PATH, 'wooden_rail.png')).size
    rail_aspect_ratio = rail_original_width / rail_original_height
    RAIL_TARGET_WIDTH = SCREEN_WIDTH
    RAIL_TARGET_HEIGHT = int(RAIL_TARGET_WIDTH / rail_aspect_ratio)
except Exception as e:
    print(
        f"Could not get dimensions of wooden_rail.png using PIL: {e}. Using fallback scale.")
    RAIL_TARGET_WIDTH = SCREEN_WIDTH
    RAIL_TARGET_HEIGHT = int(SCREEN_HEIGHT * 0.5)

assets['wooden_rail'] = load_image(
    'wooden_rail.png', scale=(RAIL_TARGET_WIDTH, RAIL_TARGET_HEIGHT))

# Card Elements
CARD_WIDTH = 100
CARD_HEIGHT = 145
assets['card_back'] = load_image(
    'card_back.png', scale=(CARD_WIDTH, CARD_HEIGHT))
assets['card_AH'] = load_image('card_AH.png', scale=(CARD_WIDTH, CARD_HEIGHT))
assets['card_4C'] = load_image('card_4C.png', scale=(CARD_WIDTH, CARD_HEIGHT))
assets['card_10D'] = load_image(
    'card_10D.png', scale=(CARD_WIDTH, CARD_HEIGHT))
# ... (add other 49 card faces here if you have them for a full deck)

# Chip Elements (No longer actively drawn in the main area, but keep loaded if used for game logic)
CHIP_SIZE = 60
assets['chip_green_100'] = load_image(
    'chip_green_100.png', scale=(CHIP_SIZE, CHIP_SIZE))
assets['chip_black_500'] = load_image(
    'chip_black_500.png', scale=(CHIP_SIZE, CHIP_SIZE))
assets['chip_black_25'] = load_image(
    'chip_black_25.png', scale=(CHIP_SIZE, CHIP_SIZE))
assets['chip_blue_5'] = load_image(
    'chip_blue_5.png', scale=(CHIP_SIZE, CHIP_SIZE))

# UI Elements
assets['title_blackjack'] = load_image('title_blackjack.png', scale=(300, 70))
assets['money_display_box'] = load_image(
    'money_display_box.png', scale=(250, 60))
assets['icon_dollar_sign'] = load_image('icon_dollar_sign.png', scale=(30, 30))

# Buttons (Button base images, text will be rendered dynamically)
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 60
assets['button_base_normal'] = load_image(
    'button_base_normal.png', scale=(BUTTON_WIDTH, BUTTON_HEIGHT))
assets['button_base_hover'] = load_image(
    'button_base_hover.png', scale=(BUTTON_WIDTH, BUTTON_HEIGHT))

# Top Right Icons
ICON_SIZE = 40
assets['icon_settings'] = load_image(
    'icon_settings.png', scale=(ICON_SIZE, ICON_SIZE))
assets['icon_help'] = load_image('icon_help.png', scale=(ICON_SIZE, ICON_SIZE))

# --- Game Data ---
dealer_hand_display = ['back', '4C']
player_hands_display = [
    {'cards': [], 'chips_stack': []},
    {'cards': ['AH', '4C', '10D'], 'chips_stack': [
        'chip_green_100', 'chip_black_500', 'chip_black_25', 'chip_blue_5']},
    {'cards': [], 'chips_stack': []}
]

current_player_total_money = 2000.00
current_player_stake = 50.00

# --- Button Class ---


class Button:
    def __init__(self, x, y, text, action, size=(BUTTON_WIDTH, BUTTON_HEIGHT)):
        self.action = action
        self.normal_image = assets['button_base_normal']
        self.hover_image = assets.get(
            'button_base_hover', assets['button_base_normal'])

        if self.normal_image.get_size() != size:
            self.normal_image = pygame.transform.smoothscale(
                self.normal_image, size)
            self.hover_image = pygame.transform.smoothscale(
                self.hover_image, size)

        self.rect = self.normal_image.get_rect(topleft=(x, y))
        self.text_surf = font_medium.render(text, True, WHITE)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

        self.current_image = self.normal_image

    def draw(self, surface):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.current_image = self.hover_image
        else:
            self.current_image = self.normal_image

        surface.blit(self.current_image, self.rect)
        surface.blit(self.text_surf, self.text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# Create Buttons
# *** Buttons moved to the center-bottom of the screen ***
buttons = [
    # Adjust X positions to center them in the lower middle area
    Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH - 20,
           SCREEN_HEIGHT - 100, "STAY", "stay_action"),
    Button(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 100, "HIT", "hit_action")
]


# --- Main Drawing Function ---
def draw_game_elements():
    # 1. Background Felt
    screen.blit(assets['felt_background'], (0, 0))

    # 2. Wooden Rail
    rail_rect = assets['wooden_rail'].get_rect(
        midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))
    screen.blit(assets['wooden_rail'], rail_rect)

    # 3. Fixed Table Text Elements
    screen.blit(assets['title_blackjack'], assets['title_blackjack'].get_rect(
        center=(SCREEN_WIDTH // 2, 50)))

    # 4. Player Betting Circle Positions (Conceptual - no longer drawing actual chips here)
    player_betting_area_y = SCREEN_HEIGHT - 160
    player_circle_offset_x = 250
    player_chip_positions = [
        (SCREEN_WIDTH // 2 - player_circle_offset_x, player_betting_area_y),
        (SCREEN_WIDTH // 2, player_betting_area_y),
        (SCREEN_WIDTH // 2 + player_circle_offset_x, player_betting_area_y)
    ]

    # 5. Dealer Cards
    dealer_card_start_x = SCREEN_WIDTH // 2 - CARD_WIDTH - 10
    dealer_card_y = 100
    for i, card_code in enumerate(dealer_hand_display):
        card_image = None
        if card_code == 'back':
            card_image = assets['card_back']
        else:
            card_image = assets.get(f'card_{card_code}', None)

        if card_image:
            screen.blit(card_image, (dealer_card_start_x +
                        (i * (CARD_WIDTH // 2)), dealer_card_y))

    # 6. Player Hands (Chips removed from this display area)
    center_player_idx = 1
    center_player_data = player_hands_display[center_player_idx]

    # --- Removed Chip Drawing ---
    # The code that drew the chip stack has been removed from here.
    # --- End Removed Chip Drawing ---

    # Cards for center player
    player_card_start_x = player_chip_positions[center_player_idx][0] - \
        CARD_WIDTH // 2 - 20
    # Centered vertically on betting area Y
    player_card_y = player_chip_positions[center_player_idx][1] - \
        CARD_HEIGHT // 2
    card_overlap_offset = 30
    for i, card_code in enumerate(center_player_data['cards']):
        card_image = assets.get(f'card_{card_code}')
        if card_image:
            screen.blit(card_image, (player_card_start_x +
                        i * card_overlap_offset, player_card_y))

    # 7. Money Displays (Total and Stake)
    money_box_width = assets['money_display_box'].get_width()
    money_box_height = assets['money_display_box'].get_height()

    # Position on the right side
    right_side_x = SCREEN_WIDTH - money_box_width - 30  # 30px padding from right edge

    # Stacked vertically on the right
    total_money_box_y = SCREEN_HEIGHT - 100 - \
        money_box_height - 10  # 10px gap between boxes
    stake_money_box_y = SCREEN_HEIGHT - 100  # This is the lower box

    # Draw Total Money Box
    total_money_rect = assets['money_display_box'].get_rect(
        topleft=(right_side_x, total_money_box_y))
    screen.blit(assets['money_display_box'], total_money_rect)
    screen.blit(assets['icon_dollar_sign'], (total_money_rect.x + 10,
                total_money_rect.centery - assets['icon_dollar_sign'].get_height() // 2))
    total_money_label_surf = font_small.render("TOTAL", True, WHITE)
    total_money_text_surf = font_money.render(
        f"{current_player_total_money:.2f}", True, WHITE)
    screen.blit(total_money_label_surf,
                (total_money_rect.x + 50, total_money_rect.y + 5))
    screen.blit(total_money_text_surf, (total_money_rect.x + 50,
                total_money_rect.centery - total_money_text_surf.get_height() // 2 + 10))

    # Draw Stake Money Box
    stake_money_rect = assets['money_display_box'].get_rect(
        topleft=(right_side_x, stake_money_box_y))
    screen.blit(assets['money_display_box'], stake_money_rect)
    screen.blit(assets['icon_dollar_sign'], (stake_money_rect.x + 10,
                stake_money_rect.centery - assets['icon_dollar_sign'].get_height() // 2))
    stake_money_label_surf = font_small.render("STAKE", True, WHITE)
    stake_money_text_surf = font_money.render(
        f"{current_player_stake:.2f}", True, WHITE)
    screen.blit(stake_money_label_surf,
                (stake_money_rect.x + 50, stake_money_rect.y + 5))
    screen.blit(stake_money_text_surf, (stake_money_rect.x + 50,
                stake_money_rect.centery - stake_money_text_surf.get_height() // 2 + 10))

    # 8. Buttons (HIT and STAY)
    for button in buttons:
        button.draw(screen)

    # 9. Top Right Icons
    screen.blit(assets['icon_settings'], (SCREEN_WIDTH - ICON_SIZE - 20, 20))
    screen.blit(assets['icon_help'], (SCREEN_WIDTH - ICON_SIZE * 2 - 30, 20))


# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.is_clicked(event.pos):
                    print(f"Button clicked! Action: {button.action}")
                    if button.action == "hit_action":
                        print("Player chose to HIT!")
                        # Add your game logic for HIT here
                    elif button.action == "stay_action":
                        print("Player chose to STAY!")
                        # Add your game logic for STAY here

    # Drawing everything
    draw_game_elements()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
