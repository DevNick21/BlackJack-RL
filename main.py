# Import necessary libraries
import random
import time
import os
import pygame
import numpy as np
from collections import defaultdict

# Tracking Variables
INTERVAL_SIZE = 1000  # Track win rate every 1000 episodes
win_rates = []  # Store win rates for plotting
interval_wins = 0
interval_games = 0

# Pygame Initialization
pygame.init()

# Screen Dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack RL Agent")

# Asset Paths
ASSET_PATH = 'assets'

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_TABLE = (53, 101, 77)

# Fonts
font_large = pygame.font.Font(None, 80)
font_medium = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 30)
font_money = pygame.font.Font(None, 36)
font_info = pygame.font.Font(None, 24)

# Global Game State Variables for UI
dealer_hand_display = []
player_hand_display = []

# Initial money for display
current_player_total_money = 1000.00
current_player_stake = 0.0

game_result_message = ""
agent_last_action = ""
current_episode_num = 0
current_epsilon = 0.0
total_wins = 0
total_losses = 0
total_pushes = 0
winning_rate = 0.0

# Speed of simulation in seconds (0.001 for fast, 1 for slow)
simulation_speed = 0.001

# Helper function for loading assets
assets = {}
CARD_WIDTH = 100
CARD_HEIGHT = 145
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 60
ICON_SIZE = 40


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
        print(f"Error loading image {filename}: {e}. Creating placeholder.")
        placeholder = pygame.Surface(scale or (50, 50))
        placeholder.fill((255, 0, 255))  # Magenta for missing image
        # Draw text for placeholder
        ph_font = pygame.font.Font(None, 20)
        ph_text = ph_font.render(filename.split('.')[0], True, BLACK)
        ph_text_rect = ph_text.get_rect(center=placeholder.get_rect().center)
        placeholder.blit(ph_text, ph_text_rect)
        return placeholder


def load_all_assets():
    print("Loading assets...")
    assets['felt_background'] = load_image(
        'felt_background.png', alpha=False, scale=(SCREEN_WIDTH, SCREEN_HEIGHT))

    RAIL_TARGET_WIDTH = SCREEN_WIDTH
    RAIL_TARGET_HEIGHT = int(SCREEN_HEIGHT * 0.25)  # Fixed ratio
    assets['wooden_rail'] = load_image(
        'wooden_rail.png', scale=(RAIL_TARGET_WIDTH, RAIL_TARGET_HEIGHT))

    assets['card_back'] = load_image(
        'card_back.png', scale=(CARD_WIDTH, CARD_HEIGHT))

    # Load all 52 card faces
    suits = ['H', 'D', 'C', 'S']  # Hearts, Diamonds, Clubs, Spades
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    for suit in suits:
        for rank in ranks:
            card_code = f'card_{rank}{suit}'
            assets[card_code] = load_image(
                f'{card_code}.png', scale=(CARD_WIDTH, CARD_HEIGHT))

    # UI Elements
    assets['title_blackjack'] = load_image(
        'title_blackjack.png', scale=(300, 70))
    assets['money_display_box'] = load_image(
        'money_display_box.png', scale=(250, 60))
    assets['icon_dollar_sign'] = load_image(
        'icon_dollar_sign.png', scale=(30, 30))

    # Buttons
    assets['button_base_normal'] = load_image(
        'button_base_normal.png', scale=(BUTTON_WIDTH, BUTTON_HEIGHT))
    assets['button_base_hover'] = load_image(
        'button_base_hover.png', scale=(BUTTON_WIDTH, BUTTON_HEIGHT))

    # Top Right Icons
    assets['icon_settings'] = load_image(
        'icon_settings.png', scale=(ICON_SIZE, ICON_SIZE))
    assets['icon_help'] = load_image(
        'icon_help.png', scale=(ICON_SIZE, ICON_SIZE))
    print("Assets loaded.")


load_all_assets()


# Game Core Logic

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = self._get_value()
        self.display_code = f"card_{rank}{suit}"  # i.e. 'card_AH', 'card_10D'

    def _get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 1  # Base value, Hand class manages 11 vs 1
        else:
            return int(self.rank)

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return self.__str__()


class Deck:
    def __init__(self, num_decks=1, seed=None):
        self.num_decks = num_decks
        self.cards = []
        self.rng = random.Random(seed)  # Pseudo-random for reproducibility
        self._initialize_deck()
        self.shuffle()

    def _initialize_deck(self):
        suits = ['H', 'D', 'C', 'S']
        ranks = ['A', '2', '3', '4', '5', '6',
                 '7', '8', '9', '10', 'J', 'Q', 'K']
        for _ in range(self.num_decks):
            for suit in suits:
                for rank in ranks:
                    self.cards.append(Card(rank, suit))

    def shuffle(self):
        self.rng.shuffle(self.cards)

    def deal_card(self):
        if not self.cards:
            print("Deck is empty, reshuffling...")
            self._initialize_deck()  # Re-initialize if runs out
            self.shuffle()
        return self.cards.pop()


class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0  # Number of aces being counted as 11

    def add_card(self, card):
        self.cards.append(card)
        if card.rank == 'A':
            self.aces += 1
            self.value += 11  # Start with 11
        else:
            self.value += card.value
        self._adjust_for_ace()

    def _adjust_for_ace(self):
        # Convert aces from 11 to 1 while over 21
        while self.value > 21 and self.aces > 0:
            self.value -= 10  # Convert 11 to 1
            self.aces -= 1

    def is_blackjack(self):
        return len(self.cards) == 2 and self.value == 21

    def is_bust(self):
        return self.value > 21

    def get_display_codes(self, hide_first_card=False):
        if hide_first_card and self.cards:
            # Assumes the first card in dealer_hand.cards is the hole card
            return ['card_back'] + [card.display_code for card in self.cards[1:]]
        return [card.display_code for card in self.cards]

    def has_usable_ace(self):
        # Has at least one ace being counted as 11
        return self.aces > 0


class BlackjackGame:
    def __init__(self, seed=None):
        self.deck = Deck(num_decks=1, seed=seed)
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.game_over = False
        self.result = ""  # "Win", "Loss", "Push"

    def start_hand(self):
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.game_over = False
        self.result = ""

        # Standard blackjack dealing: Player, Dealer (upcard), Player, Dealer (hole card)
        self.player_hand.add_card(self.deck.deal_card())
        # Dealer's upcard (visible)
        self.dealer_hand.add_card(self.deck.deal_card())
        self.player_hand.add_card(self.deck.deal_card())
        # Dealer's hole card (hidden)
        self.dealer_hand.add_card(self.deck.deal_card())

        # Check for immediate Blackjacks
        if self.player_hand.is_blackjack():
            if self.dealer_hand.is_blackjack():
                self.game_over = True
                self.result = "Push"
            else:
                self.game_over = True
                self.result = "Win"  # Player Blackjack wins (pays 3:2)
            return "game_over"

        elif self.dealer_hand.is_blackjack():
            self.game_over = True
            self.result = "Loss"  # Dealer Blackjack beats player non-Blackjack
            return "game_over"

        return "player_turn"

    def player_hit(self):
        self.player_hand.add_card(self.deck.deal_card())
        if self.player_hand.is_bust():
            self.game_over = True
            self.result = "Loss"
            return "player_bust"  # Signal for UI
        return "player_turn"  # Signal for UI, can hit again

    def player_stand(self):
        return self.dealer_turn()  # Proceed to dealer's turn

    def dealer_turn(self):
        # Dealer must hit on 16 or less, stand on 17 or more (standard rule)
        while self.dealer_hand.value < 17:
            self.dealer_hand.add_card(self.deck.deal_card())
            if self.dealer_hand.is_bust():
                self.game_over = True
                self.result = "Win"
                return "dealer_bust"  # Signal for UI

        # Determine winner if no busts
        if self.player_hand.value > self.dealer_hand.value:
            self.result = "Win"
        elif self.dealer_hand.value > self.player_hand.value:
            self.result = "Loss"
        else:
            self.result = "Push"  # Tie

        self.game_over = True
        return "game_over"  # Signal for UI

# --- RL Agent Logic ---

# State definition: (player_sum, dealer_upcard_value, usable_ace)
# Player sum: 4-21 (min starting hand is 2, max after hits can be 21)
# Dealer upcard: 2-11 (11 for Ace)
# Usable ace: 0 (False), 1 (True)
# Actions: 0 (Stand), 1 (Hit)


def get_state(player_hand, dealer_hand):
    # Use dealer's first card (upcard) for state representation
    dealer_upcard = dealer_hand.cards[0] if dealer_hand.cards else None
    if dealer_upcard is None:
        dealer_upcard_value = 0
    elif dealer_upcard.rank == 'A':
        dealer_upcard_value = 11  # Ace upcard is always 11 for state
    else:
        dealer_upcard_value = dealer_upcard.value

    player_sum = player_hand.value
    usable_ace = 1 if player_hand.has_usable_ace() else 0

    # Handle edge cases for Q-learning
    if player_sum < 12:  # Always hit below 12 in basic strategy
        player_sum = max(player_sum, 4)  # Minimum possible starting hand
    elif player_sum > 21:  # Bust states shouldn't reach here, but safety check
        player_sum = 21

    return (player_sum, dealer_upcard_value, usable_ace)


def get_reward(game_result, is_blackjack=False):
    if game_result == "Win":
        return 1.5 if is_blackjack else 1.0  # Blackjack pays 3:2
    elif game_result == "Loss":
        return -1.0
    elif game_result == "Push":
        return 0.0
    else:
        return 0.0


# Using defaultdict for Q-table allows new state-action pairs to be initialized to 0
# without pre-defining the entire table explicitly.
q_table = defaultdict(lambda: np.zeros(2))  # 2 actions: 0=Stand, 1=Hit

# Q-learning parameters
LEARNING_RATE = 0.05
DISCOUNT_FACTOR = 0.95
EPSILON_START = 1.0
EPSILON_DECAY = 0.99995  # Faster decay for 50k episodes
EPSILON_MIN = 0.01
EPISODES = 50000  # More episodes needed for Blackjack due to more states and stochasticity

# Pseudo-random number generators for reproducibility
game_rng_seed = 42
epsilon_rng_seed = 123
# For epsilon-greedy action choice
q_learning_rng = random.Random(epsilon_rng_seed)

# --- UI Button Class ---


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


# Simulation control buttons
control_buttons = [
    Button(SCREEN_WIDTH - BUTTON_WIDTH - 20, SCREEN_HEIGHT -
           200, "Start Sim", "start_sim", size=(180, 60)),
    Button(SCREEN_WIDTH - BUTTON_WIDTH - 20, SCREEN_HEIGHT -
           130, "Pause Sim", "pause_sim", size=(180, 60)),
    Button(SCREEN_WIDTH - BUTTON_WIDTH - 20, SCREEN_HEIGHT -
           60, "Reset Q", "reset_q", size=(180, 60)),
]

# --- Main Drawing Function ---


def draw_game_elements():
    global dealer_hand_display, player_hand_display, current_player_total_money, current_player_stake, \
        game_result_message, agent_last_action, current_episode_num, current_epsilon, \
        total_wins, total_losses, total_pushes, winning_rate  # <--- ADDED: winning_rate

    # 1. Background Felt
    screen.blit(assets['felt_background'], (0, 0))

    # 2. Wooden Rail
    rail_rect = assets['wooden_rail'].get_rect(
        midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))
    screen.blit(assets['wooden_rail'], rail_rect)

    # 3. Title
    screen.blit(assets['title_blackjack'], assets['title_blackjack'].get_rect(
        center=(SCREEN_WIDTH // 2, 50)))

    # 4. Dealer Cards
    dealer_card_start_x = SCREEN_WIDTH // 2 - \
        (len(dealer_hand_display) * CARD_WIDTH // 4)
    dealer_card_y = 100
    for i, card_code in enumerate(dealer_hand_display):
        # Fallback to card_back if code not found (e.g., 'back')
        card_image = assets.get(card_code, assets['card_back'])
        screen.blit(card_image, (dealer_card_start_x +
                    (i * (CARD_WIDTH // 3)), dealer_card_y))

    # Dealer Score
    # Show true score when hand is over, or after initial checks
    if game.game_over or (len(game.dealer_hand.cards) > 1 and not game_result_message == ""):
        dealer_score_text = font_medium.render(
            f"Dealer: {game.dealer_hand.value}", True, WHITE)
    else:  # Otherwise, show score based on upcard (or 0 if no cards yet)
        dealer_upcard_value = game.dealer_hand.cards[0].value if game.dealer_hand.cards else 0
        dealer_score_text = font_medium.render(
            f"Dealer: {dealer_upcard_value} + ?", True, WHITE)
    screen.blit(dealer_score_text, (SCREEN_WIDTH // 2 -
                dealer_score_text.get_width() // 2, dealer_card_y + CARD_HEIGHT + 10))

    # 5. Player Cards
    player_card_start_x = SCREEN_WIDTH // 2 - \
        (len(player_hand_display) * CARD_WIDTH // 4)
    player_card_y = SCREEN_HEIGHT - CARD_HEIGHT - 250
    for i, card_code in enumerate(player_hand_display):
        # Fallback to card_back if code not found
        card_image = assets.get(card_code, assets['card_back'])
        screen.blit(card_image, (player_card_start_x +
                    (i * (CARD_WIDTH // 3)), player_card_y))

    # Player Score
    player_score_text = font_medium.render(
        f"Agent Hand: {game.player_hand.value}", True, WHITE)
    screen.blit(player_score_text, (SCREEN_WIDTH // 2 -
                player_score_text.get_width() // 2, player_card_y - 50))

    # 6. Money Displays (Total and Stake)
    money_box_width = assets['money_display_box'].get_width()
    money_box_height = assets['money_display_box'].get_height()

    right_side_x = SCREEN_WIDTH - money_box_width - 30
    total_money_box_y = SCREEN_HEIGHT - 100 - money_box_height - 10
    stake_money_box_y = SCREEN_HEIGHT - 100

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

    # 7. Simulation Control Buttons
    for button in control_buttons:
        button.draw(screen)

    # 8. Game Result Message
    if game_result_message:
        result_surf = font_large.render(game_result_message, True, WHITE)
        result_rect = result_surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(result_surf, result_rect)

    # 9. Agent Info Display (Top Left)
    info_text_y = 20
    info_x = 20

    episode_text = font_info.render(
        f"Episode: {current_episode_num}/{EPISODES}", True, WHITE)
    screen.blit(episode_text, (info_x, info_text_y))
    info_text_y += 30

    epsilon_text = font_info.render(
        f"Epsilon: {current_epsilon:.4f}", True, WHITE)
    screen.blit(epsilon_text, (info_x, info_text_y))
    info_text_y += 30

    action_text = font_info.render(
        f"Agent Action: {agent_last_action}", True, WHITE)
    screen.blit(action_text, (info_x, info_text_y))
    info_text_y += 30

    # Calculate and display winning rate
    total_hands = total_wins + total_losses + total_pushes
    if total_hands > 0:
        winning_rate = (total_wins / total_hands) * 100
    else:
        winning_rate = 0.0  # No hands played yet

    stats_text = font_info.render(
        f"Wins: {total_wins} | Losses: {total_losses} | Pushes: {total_pushes}", True, WHITE)
    screen.blit(stats_text, (info_x, info_text_y))
    info_text_y += 30

    winning_rate_text = font_info.render(
        f"Win Rate: {winning_rate:.2f}%", True, WHITE)  # <--- ADDED: Display winning rate
    screen.blit(winning_rate_text, (info_x, info_text_y))


# --- Main Game Loop for RL Training and Visualization ---
game = BlackjackGame(seed=game_rng_seed)
epsilon = EPSILON_START
simulation_active = False  # Flag to control simulation
last_game_state_change_time = 0

# Initial UI update
dealer_hand_display = game.dealer_hand.get_display_codes(hide_first_card=True)
player_hand_display = game.player_hand.get_display_codes()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in control_buttons:
                if button.is_clicked(event.pos):
                    if button.action == "start_sim":
                        simulation_active = True
                        print("Simulation Started!")
                    elif button.action == "pause_sim":
                        simulation_active = False
                        print("Simulation Paused!")
                    elif button.action == "reset_q":
                        q_table.clear()  # Reset Q-table
                        epsilon = EPSILON_START
                        current_episode_num = 0
                        total_wins, total_losses, total_pushes = 0, 0, 0
                        winning_rate = 0.0  # Reset winning rate
                        interval_wins = 0  # Reset interval tracking
                        interval_games = 0
                        win_rates.clear()  # Clear win rate history
                        game_result_message = "Q-Table Reset!"
                        simulation_active = False  # Pause after reset
                        print("Q-Table and Simulation Reset!")

    current_time = time.time()
    # Only step the simulation if active and enough time has passed
    if simulation_active and current_time - last_game_state_change_time > simulation_speed:
        if current_episode_num < EPISODES:
            current_episode_num += 1
            current_epsilon = epsilon
            game_result_message = ""  # Clear previous result

            # Start a new hand
            # Use a new seed for each episode to ensure different card sequences per episode,
            # but the overall sequence of episodes is reproducible due to game_rng_seed.
            game = BlackjackGame(seed=game_rng_seed + current_episode_num)
            game_status = game.start_hand()

            # Handle immediate game over from start_hand (e.g., Blackjack)
            if game.game_over:
                # Update UI for initial deal & reveal dealer's hole card if game over
                dealer_hand_display = game.dealer_hand.get_display_codes(
                    hide_first_card=False)
                player_hand_display = game.player_hand.get_display_codes()

                # Check if player won with blackjack for bonus reward
                is_player_blackjack = game.player_hand.is_blackjack() and game.result == "Win"
                reward = get_reward(game.result, is_player_blackjack)

                game_result_message = f"{game.result}" + \
                    (" (Blackjack!)" if is_player_blackjack else "")
                if game.result == "Win":
                    total_wins += 1
                elif game.result == "Loss":
                    total_losses += 1
                elif game.result == "Push":
                    total_pushes += 1

                # Epsilon decay happens at end of episode (hand)
                epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY)

                last_game_state_change_time = current_time
                continue

            # Initial state and action selection for player
            state = get_state(game.player_hand, game.dealer_hand)

            # --- Agent's Turn Loop ---
            while not game.game_over:
                # Epsilon-greedy action selection
                if q_learning_rng.uniform(0, 1) < epsilon:
                    action = q_learning_rng.choice([0, 1])  # 0=Stand, 1=Hit
                    agent_last_action = "Explore: " + \
                        ("STAND" if action == 0 else "HIT")
                else:
                    action = np.argmax(q_table[state])
                    agent_last_action = "Exploit: " + \
                        ("STAND" if action == 0 else "HIT")

                # Update UI to show current hand and agent's choice before action
                dealer_hand_display = game.dealer_hand.get_display_codes(
                    hide_first_card=True)
                player_hand_display = game.player_hand.get_display_codes()
                draw_game_elements()
                pygame.display.flip()
                time.sleep(simulation_speed)  # Pause for visual effect

                # Take action
                old_state = state  # Store old state before action
                if action == 1:  # HIT
                    game_status = game.player_hit()
                else:  # STAND
                    game_status = game.player_stand()

                # Get new state (if not game over yet)
                if not game.game_over:
                    new_state = get_state(game.player_hand, game.dealer_hand)
                    reward = 0  # Rewards are sparse, only at end of game
                else:  # Game over, new_state is terminal, reward applies
                    new_state = None  # Terminal state
                    # Check for blackjack bonus (only for initial blackjack, not after hitting)
                    is_player_blackjack = (game.player_hand.is_blackjack() and
                                           len(game.player_hand.cards) == 2 and
                                           game.result == "Win")
                    reward = get_reward(game.result, is_player_blackjack)

                    game_result_message = f"{game.result}" + \
                        (" (Blackjack!)" if is_player_blackjack else "")

                    # Update win/loss/push counts for display
                    if game.result == "Win":
                        total_wins += 1
                        interval_wins += 1  # Track wins for current interval
                    elif game.result == "Loss":
                        total_losses += 1
                    elif game.result == "Push":
                        total_pushes += 1

                    interval_games += 1

                    # Check if we've completed an interval
                    if interval_games >= INTERVAL_SIZE:
                        current_win_rate = (
                            interval_wins / interval_games) * 100
                        win_rates.append(current_win_rate)
                        print(
                            f"Episodes {current_episode_num - INTERVAL_SIZE + 1}-{current_episode_num}: Win Rate = {current_win_rate:.2f}%")
                        interval_wins = 0
                        interval_games = 0

                    # Epsilon decay happens at end of episode (hand)
                    epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY)

                # Q-table update
                old_q_value = q_table[old_state][action]
                if new_state is None:  # Terminal state
                    target_q_value = reward
                else:
                    target_q_value = reward + DISCOUNT_FACTOR * \
                        np.max(q_table[new_state])

                q_table[old_state][action] = old_q_value + \
                    LEARNING_RATE * (target_q_value - old_q_value)

                state = new_state  # Move to new state for next iteration

                if game.game_over:
                    # Final UI update for the hand's outcome
                    dealer_hand_display = game.dealer_hand.get_display_codes(
                        hide_first_card=False)  # Reveal dealer's hand
                    player_hand_display = game.player_hand.get_display_codes()

                    # Epsilon decay happens at end of episode (hand)
                    epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY)

                    draw_game_elements()
                    pygame.display.flip()
                    # Longer pause at game end
                    time.sleep(simulation_speed * 2)
                    break  # Break out of inner while loop (agent's turn)
        else:
            simulation_active = False  # Stop simulation when episodes complete
            game_result_message = "Training Complete!"

        last_game_state_change_time = current_time

    # Drawing everything
    draw_game_elements()

    # Update the display
    pygame.display.flip()


def export_results_to_json():
    """Exports all relevant training results to a JSON file."""
    print("\nExporting results to training_results.json...")

    # Convert Q-table keys (tuples) to strings for JSON compatibility
    q_table_exportable = {str(k): v.tolist() for k, v in q_table.items()}

    results = {
        "hyperparameters": {
            "learning_rate": LEARNING_RATE,
            "discount_factor": DISCOUNT_FACTOR,
            "episodes": EPISODES,
            "epsilon_start": EPSILON_START,
            "epsilon_decay": EPSILON_DECAY,
            "epsilon_min": EPSILON_MIN,
            "interval_size": INTERVAL_SIZE
        },
        "statistics": {
            "total_wins": total_wins,
            "total_losses": total_losses,
            "total_pushes": total_pushes,
            "final_win_rate_percent": winning_rate
        },
        "win_rate_history": win_rates,
        "q_table": q_table_exportable
    }

    try:
        import json
        with open('training_results.json', 'w') as f:
            json.dump(results, f, indent=4)
        print("Successfully exported results.")
    except Exception as e:
        print(f"Error exporting results: {e}")


export_results_to_json()


# Quit Pygame
pygame.quit()
print("Simulation finished. Q-table state examples:")
# Print some learned Q-values (e.g., for common states)
# Optimal basic strategy for these:
# (17, 7, 0) -> Stand (action 0)
# (12, 4, 0) -> Hit (action 1)
# Player 17, dealer 7, no usable ace, Stand
print(f"Q((17, 7, 0), Stand): {q_table[(17, 7, 0)][0]:.4f}")
# Player 17, dealer 7, no usable ace, Hit
print(f"Q((17, 7, 0), Hit): {q_table[(17, 7, 0)][1]:.4f}")

# Player 12, dealer 4, no usable ace, Stand
print(f"Q((12, 4, 0), Stand): {q_table[(12, 4, 0)][0]:.4f}")
# Player 12, dealer 4, no usable ace, Hit
print(f"Q((12, 4, 0), Hit): {q_table[(12, 4, 0)][1]:.4f}")

# Player 18, dealer 10, no usable ace, Stand
print(f"Q((18, 10, 0), Stand): {q_table[(18, 10, 0)][0]:.4f}")
# Player 18, dealer 10, no usable ace, Hit
print(f"Q((18, 10, 0), Hit): {q_table[(18, 10, 0)][1]:.4f}")

# Player 11, dealer 7, no usable ace, Stand
print(f"Q((11, 7, 0), Stand): {q_table[(11, 7, 0)][0]:.4f}")
# Player 11, dealer 7, no usable ace, Hit
print(f"Q((11, 7, 0), Hit): {q_table[(11, 7, 0)][1]:.4f}")
