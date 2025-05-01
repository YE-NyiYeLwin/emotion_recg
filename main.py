import pygame
import os
import cv2
from fer import FER
import numpy as np
import time
import openai
import requests
import json
import textwrap
import pygame_gui

openai.api_key = "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"

# Initialize Pygame
pygame.init()

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize emotion detector
emotion_detector = FER(mtcnn=True)

# List to store captured images
captured_images = []

# List to store detected emotions
detected_emotions = []

# Set up the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Mario-like Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
SKY_BLUE = (135, 206, 235)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
DARK_YELLOW = (204, 172, 0)

# Define game constants
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_SPEED = -12
BLOCK_WIDTH = 45
BLOCK_HEIGHT = 45
FLOOR_HEIGHT = 50
ANIMATION_DELAY = 200  # Milliseconds between animation frames
show_powerup_text = False
powerup_text_timer = 0
first_choice_made = False
last_powerup_choice = None
rounds_since_last_powerup = 0
game_over_state = False
image_captured = False
capture_timer = 0

# Load game assets
game_dir = os.path.dirname(__file__)
player_sprite_sheet = pygame.image.load(os.path.join(game_dir, "assets/player.png"))
block_image = pygame.image.load(os.path.join(game_dir, "assets/block.png"))
flag_image = pygame.image.load("flag.png")
flag_image = pygame.transform.scale(flag_image, (30, 60))
sky_image = pygame.image.load(os.path.join(game_dir, "assets/sky.png"))
ground_image = pygame.image.load(os.path.join(game_dir, "assets/ground.png"))
cat_image = pygame.image.load(os.path.join(game_dir, "assets/cat.png"))
cat_image = pygame.transform.scale(cat_image, (50, 50))

sky_image = pygame.transform.scale(
    sky_image, (WINDOW_WIDTH, WINDOW_HEIGHT - FLOOR_HEIGHT)
)
ground_image = pygame.transform.scale(ground_image, (WINDOW_WIDTH, FLOOR_HEIGHT))


# Define game objects
red_powerup = pygame.Rect(700, WINDOW_HEIGHT - FLOOR_HEIGHT - 400, 30, 30)
big_coin = pygame.Rect(1200, WINDOW_HEIGHT - FLOOR_HEIGHT - 350, 30, 30)
powerups = [red_powerup, big_coin]
flag = pygame.Rect(2300, WINDOW_HEIGHT - 100, 30, 60)

cat = pygame.Rect(2150, WINDOW_HEIGHT - 100, 30, 60)  # Position it before the flag
cat_speed = 2  # Speed of the cat
cat_direction = 1  # 1 for right, -1 for left

player_rect = pygame.Rect(
    50, WINDOW_HEIGHT - PLAYER_HEIGHT - FLOOR_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT
)
easy_blocks = [
    pygame.Rect(
        200, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT
    ),
    pygame.Rect(
        600,
        WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 200,
        BLOCK_WIDTH,
        BLOCK_HEIGHT,
    ),
    pygame.Rect(
        900,
        WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 100,
        BLOCK_WIDTH,
        BLOCK_HEIGHT,
    ),
    pygame.Rect(
        850,
        WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 300,
        BLOCK_WIDTH,
        BLOCK_HEIGHT,
    ),
    pygame.Rect(
        980,
        WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 200,
        BLOCK_WIDTH,
        BLOCK_HEIGHT,
    ),
]
hard_blocks = [
    pygame.Rect(
        200, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT, BLOCK_WIDTH, BLOCK_HEIGHT
    ),
    pygame.Rect(
        600,
        WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 200,
        BLOCK_WIDTH,
        BLOCK_HEIGHT,
    ),
    pygame.Rect(
        900,
        WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 100,
        BLOCK_WIDTH,
        BLOCK_HEIGHT,
    ),
    pygame.Rect(
        850,
        WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 300,
        BLOCK_WIDTH,
        BLOCK_HEIGHT,
    ),
    pygame.Rect(
        980,
        WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 200,
        BLOCK_WIDTH,
        BLOCK_HEIGHT,
    ),
]

# Untouchable blocks
untouchable_blocks = [
    pygame.Rect(
        500, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 50, BLOCK_WIDTH, BLOCK_HEIGHT
    )
]

# Untouchable coins
untouchable_coins = [
    pygame.Rect(1850, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 15, 20, 20),
]

# Coins
coins = [
    pygame.Rect(250, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 25, 20, 20),
    pygame.Rect(450, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 125, 20, 20),
    pygame.Rect(650, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 225, 20, 20),
    pygame.Rect(1750, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 15, 20, 20),
    pygame.Rect(1950, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 15, 20, 20),
    pygame.Rect(2050, WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 15, 20, 20),
]

# Coin counter
coin_count = 0

# Ground Blocks
floor_rects = [
    pygame.Rect(0, WINDOW_HEIGHT - FLOOR_HEIGHT, 200, FLOOR_HEIGHT),
    pygame.Rect(300, WINDOW_HEIGHT - FLOOR_HEIGHT, 200, FLOOR_HEIGHT),
    pygame.Rect(600, WINDOW_HEIGHT - FLOOR_HEIGHT, 200, FLOOR_HEIGHT),
    pygame.Rect(900, WINDOW_HEIGHT - FLOOR_HEIGHT, 500, FLOOR_HEIGHT),
    pygame.Rect(1600, WINDOW_HEIGHT - FLOOR_HEIGHT, 900, FLOOR_HEIGHT),
]

# Player animation
player_animation_frames = []
num_frames = 12  # Assuming 4 frames in the sprite sheet
frame_width = player_sprite_sheet.get_width() // num_frames
for i in range(num_frames):
    x = i * frame_width
    player_animation_frames.append(
        player_sprite_sheet.subsurface(
            pygame.Rect(x, 0, frame_width, player_sprite_sheet.get_height())
        )
    )
current_frame = 0
last_update = pygame.time.get_ticks()

# Variables to track player choices
player_choices = []
game_started = False
game_over = False
difficulty = None
blocks = []

# Camera position
camera_x = 0

# Track the number of replays
replay_count = 0

# Game loop
running = True
player_x_velocity = 0
player_y_velocity = 0
on_ground = False
game_finished = False


# Process emotions of captured images
def process_emotions():
    global detected_emotions
    for image in captured_images:
        result = emotion_detector.detect_emotions(image)
        if result:
            dominant_emotion = max(result[0]["emotions"], key=result[0]["emotions"].get)
            detected_emotions.append(dominant_emotion)

    # Clear captured images after processing
    captured_images.clear()


# Report generation using AI21 API
def generate_personality_report(player_choices, detected_emotions):
    url = "https://api.ai21.com/studio/v1/j2-ultra/chat"

    if "Kills cute cat NPC" not in player_choices:
        player_choices.append("Does not kill cute cat NPC. ")

    if not any(
        choice.startswith("Tried out a different powerup") for choice in player_choices
    ):
        player_choices.append(
            "Did not explore all powerups: the fly boost and the 10 coins"
        )

    # Construct the prompt
    prompt = "I have played a game where I made the following choices and experienced the following emotions:\n"

    for choice in player_choices:
        prompt += f"Choice: {choice}.\n"

    prompt += "These are the emotions detected on the user when they died:\n"
    for emotion in detected_emotions:
        prompt += f"Emotion: {emotion}.\n"

    total_coins = 6
    prompt += f"I collected {coin_count}/{total_coins} coins.\n"
    prompt += f"I finished the game after dying {replay_count} times.\n"

    # Final sentence of the prompt
    prompt += "Based on these choices and emotions, can you generate a personality report that describes my key personality traits? Write it as an essay report, rather than bullet points. Just describe my personality."

    # Output the prompt for debugging/verification
    print(prompt)

    payload = {
        "numResults": 1,
        "temperature": 0.7,
        "messages": [
            {
                "text": prompt,
                "role": "user",
            }
        ],
        "system": "You are an AI assistant for generating personality assessment reports. Your responses should be informative and concise.",
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer DDRPPVJWLRaDm9U3pXP6crGjivmIOVly",
    }

    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)
    return result["outputs"][0]["text"]
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = json.loads(response.text)
        return result["outputs"][0]["text"]
    except requests.exceptions.RequestException as e:
        print(f"Error generating report: {e}")
        return "Unable to generate personality report due to an error."
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing API response: {e}")
        return (
            "Unable to generate personality report due to an error in the API response."
        )


def show_text_modal(report):
    manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Set up modal dimensions and position
    modal_width = 600
    modal_height = 400
    modal_x = (WINDOW_WIDTH - modal_width) // 2
    modal_y = (WINDOW_HEIGHT - modal_height) // 2

    # Create a background panel for the modal
    panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(modal_x, modal_y, modal_width, modal_height),
        manager=manager,
    )

    # Create a text box with a scrollbar
    text_box = pygame_gui.elements.UITextBox(
        html_text=report,
        relative_rect=pygame.Rect(10, 10, modal_width - 20, modal_height - 60),
        manager=manager,
        container=panel,
    )

    # Create a close button
    close_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(modal_width - 110, modal_height - 40, 100, 30),
        text="Close",
        manager=manager,
        container=panel,
    )

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == close_button:
                        is_running = False

            manager.process_events(event)

        manager.update(time_delta)

        window.fill(SKY_BLUE)
        manager.draw_ui(window)
        pygame.display.update()

    # Clean up
    pygame.quit()


clock = pygame.time.Clock()
while running:
    # Handle events

    if game_finished:
        process_emotions()
        print("Detected emotions:", detected_emotions)
        font = pygame.font.Font(None, 74)
        text = font.render("Thanks for playing", True, (255, 0, 0))  # Red color
        window.blit(
            text,
            (
                WINDOW_WIDTH // 2 - text.get_width() // 2,
                WINDOW_HEIGHT // 2 - text.get_height() // 2,
            ),
        )

        personality_report = generate_personality_report(
            player_choices, detected_emotions
        )
        show_text_modal(personality_report)
        break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    # Reset the game
                    image_captured = False
                    player_rect.x = 50
                    player_rect.y = WINDOW_HEIGHT - PLAYER_HEIGHT - FLOOR_HEIGHT
                    player_x_velocity = 0
                    player_y_velocity = 0
                    game_over = False
                    replay_count += 1  # Increment replay count
                    rounds_since_last_powerup += (
                        1  # Increment rounds since last powerup
                    )
                    cat = pygame.Rect(
                        2200, WINDOW_HEIGHT - FLOOR_HEIGHT - 50, 50, 50
                    )  # Reset cat position
                    cat_direction = 1  # Reset cat direction
                    coin_count = 0  # Reset coin count
                    coins = [
                        pygame.Rect(
                            250,
                            WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 25,
                            20,
                            20,
                        ),
                        pygame.Rect(
                            450,
                            WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 125,
                            20,
                            20,
                        ),
                        pygame.Rect(
                            650,
                            WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 225,
                            20,
                            20,
                        ),
                        pygame.Rect(
                            1750,
                            WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 15,
                            20,
                            20,
                        ),
                        pygame.Rect(
                            1950,
                            WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 15,
                            20,
                            20,
                        ),
                        pygame.Rect(
                            2050,
                            WINDOW_HEIGHT - BLOCK_HEIGHT - FLOOR_HEIGHT - 15,
                            20,
                            20,
                        ),
                    ]
            elif not game_started:
                if event.key == pygame.K_1:
                    difficulty = "easy"
                    player_choices.append("Chose easy mode")
                    blocks = easy_blocks
                    game_started = True
                elif event.key == pygame.K_2:
                    difficulty = "hard"
                    player_choices.append("Chose hard mode")
                    blocks = hard_blocks
                    game_started = True
            else:
                if event.key == pygame.K_LEFT:
                    player_x_velocity = -PLAYER_SPEED
                elif event.key == pygame.K_RIGHT:
                    player_x_velocity = PLAYER_SPEED
                elif event.key == pygame.K_SPACE and on_ground:
                    player_y_velocity = JUMP_SPEED
        elif event.type == pygame.KEYUP:
            if game_started and (
                event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT
            ):
                player_x_velocity = 0

    if game_started and not game_over:
        if cat:  # Only update if cat exists
            # Update cat position
            cat.x += cat_speed * cat_direction

            # Reverse direction if the cat reaches the edge of its movement range
            if cat.x <= 2100 or cat.x >= 2300:  # Adjust these values as needed
                cat_direction *= -1

        # Update player position
        player_rect.x += player_x_velocity
        player_y_velocity += GRAVITY
        player_rect.y += player_y_velocity

        # Check for collisions with coins
        for coin in coins[:]:
            if player_rect.colliderect(coin):
                coins.remove(coin)
                coin_count += 1

        if cat:  # Only update if cat exists
            # Check for collisions with the cat
            if player_rect.colliderect(cat):
                if (
                    player_rect.bottom <= cat.top + 10 and player_y_velocity > 0
                ):  # Player is on top of the cat
                    cat = None  # Remove the cat
                    player_choices.append("Kills cute cat NPC")
                    player_y_velocity = (
                        JUMP_SPEED  # Make the player jump after killing the cat
                    )
                else:  # Player touched the sides of the cat
                    game_over = True

        # Check for collisions with powerups
        for powerup in powerups:
            if player_rect.colliderect(powerup):
                if not first_choice_made:
                    if powerup == red_powerup:
                        player_choices.append(
                            "Chose a Fly Boost powerup instead of 10 coins."
                        )
                    elif powerup == big_coin:
                        player_choices.append(
                            "Chose 10 coins instead of a Fly boost powerup."
                        )
                    first_choice_made = True

                # Record the powerup choice
                current_powerup_choice = (
                    "red powerup" if powerup == red_powerup else "big coin"
                )
                if (
                    last_powerup_choice is not None
                    and current_powerup_choice != last_powerup_choice
                ):
                    curious_count = rounds_since_last_powerup
                    player_choices.append(
                        f"Tried out a different powerup, {curious_count} rounds after first choice. How curious."
                    )

                last_powerup_choice = current_powerup_choice
                rounds_since_last_powerup = 0

                show_powerup_text = True
                powerup_text_timer = 180
                capture_timer = 60  # 60 frames (1 second at 60 FPS)
                powerups = []  # Remove all power-ups once one is collected
                break

        if show_powerup_text:
            powerup_text_timer -= 1
            if powerup_text_timer <= 0:
                show_powerup_text = False

        if capture_timer > 0:
            capture_timer -= 1
            if capture_timer == 0:
                # Capture image
                ret, frame = cap.read()
                if ret:
                    captured_images.append(frame)
                    print("Captured after powerup")

        # Check for collisions with blocks
        for block in blocks:
            if player_rect.colliderect(block):
                if player_y_velocity > 0:
                    player_rect.bottom = block.top
                    player_y_velocity = 0
                    on_ground = True  # Set on_ground to True when landing on a block
                elif player_y_velocity < 0:
                    player_rect.top = block.bottom
                    player_y_velocity = 0

        # Check for collisions with floor
        for floor_rect in blocks + floor_rects:
            if player_rect.colliderect(floor_rect):
                if player_y_velocity > 0:
                    player_rect.bottom = (
                        floor_rect.top
                    )  # Align player's bottom with floor's top
                    player_y_velocity = 0
                    on_ground = True
                elif player_y_velocity < 0:
                    player_y_velocity = 0

        # Check for collisions with untouchable blocks
        for block in untouchable_blocks:
            if player_rect.colliderect(block):
                game_over = True

        # Check for collisions with untouchable coin
        for coin in untouchable_coins:
            if player_rect.colliderect(coin):
                game_over = True
                break

        # Check if the player has touched the flag
        if player_rect.colliderect(flag):
            game_finished = True

        # Reset on_ground if player is not on any surface
        if player_y_velocity > 0:
            on_ground = False

        # Check if player has fallen into a gap
        if player_rect.y > WINDOW_HEIGHT:
            game_over = True

        # Update player animation
        current_time = pygame.time.get_ticks()
        if current_time - last_update > ANIMATION_DELAY:
            last_update = current_time
            current_frame = (current_frame + 1) % num_frames
            if player_x_velocity == 0:
                current_frame = 0  # Reset to the first frame when not moving

        # Update camera position
        camera_x = max(0, player_rect.x - WINDOW_WIDTH // 2)

    # Clear the window
    window.fill(SKY_BLUE)

    if not game_started:
        # Display the choice modal
        font = pygame.font.Font(None, 36)
        text1 = font.render("Choose your difficulty level:", True, WHITE)
        text2 = font.render("Press 1 for Easy Mode", True, WHITE)
        text3 = font.render("Press 2 for Hard Mode", True, WHITE)
        window.blit(
            text1, (WINDOW_WIDTH // 2 - text1.get_width() // 2, WINDOW_HEIGHT // 2 - 50)
        )
        window.blit(
            text2, (WINDOW_WIDTH // 2 - text2.get_width() // 2, WINDOW_HEIGHT // 2)
        )
        window.blit(
            text3, (WINDOW_WIDTH // 2 - text3.get_width() // 2, WINDOW_HEIGHT // 2 + 50)
        )
    elif game_over:
        # Display the game over screen
        # Capture image when player dies
        game_over_state = True

        if not image_captured:
            # Capture image when player dies
            ret, frame = cap.read()
            if ret:
                captured_images.append(frame)
                image_captured = True
                print("Captured")
        red_powerup = pygame.Rect(700, WINDOW_HEIGHT - FLOOR_HEIGHT - 400, 30, 30)
        big_coin = pygame.Rect(1200, WINDOW_HEIGHT - FLOOR_HEIGHT - 350, 30, 30)
        powerups = [red_powerup, big_coin]
        font = pygame.font.Font(None, 36)
        text1 = font.render("Game Over!", True, RED)
        text2 = font.render("Press R to Replay", True, WHITE)
        text3 = font.render(f"Replays: {replay_count}", True, WHITE)
        window.blit(
            text1, (WINDOW_WIDTH // 2 - text1.get_width() // 2, WINDOW_HEIGHT // 2 - 50)
        )
        window.blit(
            text2, (WINDOW_WIDTH // 2 - text2.get_width() // 2, WINDOW_HEIGHT // 2)
        )
        window.blit(
            text3, (WINDOW_WIDTH // 2 - text3.get_width() // 2, WINDOW_HEIGHT // 2 + 50)
        )
    else:
        # Draw sky
        sky_offset = (
            camera_x * 0.2
        ) % sky_image.get_width()  # Adjust the multiplier for desired parallax effect
        for i in range(0, WINDOW_WIDTH * 2, sky_image.get_width()):
            window.blit(sky_image, (-sky_offset + i, 0))

        # Draw player
        player_image = player_animation_frames[current_frame]
        window.blit(player_image, (player_rect.x - camera_x, player_rect.y))

        # Draw powerups
        pick_text = font.render("Pick 1 only", True, WHITE)
        text_x = (
            (red_powerup.x + big_coin.x) // 2 - pick_text.get_width() // 2 - camera_x
        )
        text_y = (red_powerup.y + big_coin.y) // 2 - 50
        window.blit(pick_text, (text_x, text_y))
        for powerup in powerups:
            if powerup == red_powerup:
                pygame.draw.rect(
                    window,
                    RED,
                    pygame.Rect(
                        powerup.x - camera_x, powerup.y, powerup.width, powerup.height
                    ),
                )
                text = font.render("Fly Boost", True, WHITE)
                window.blit(text, (red_powerup.x - camera_x, red_powerup.y - 30))
            elif powerup == big_coin:
                text = font.render("This is worth 10 coins", True, WHITE)
                window.blit(text, (big_coin.x - camera_x, big_coin.y - 30))
                # Outer circle (main coin body)
                pygame.draw.circle(
                    window, GOLD, (powerup.x - camera_x + 15, powerup.y + 15), 15
                )

                # Inner circle (for 3D effect)
                pygame.draw.circle(
                    window, YELLOW, (powerup.x - camera_x + 16, powerup.y + 14), 12
                )

                # Coin shine (top-left highlight)
                pygame.draw.arc(
                    window,
                    WHITE,
                    (powerup.x - camera_x + 5, powerup.y + 5, 20, 20),
                    0.9,
                    2.5,
                    2,
                )

                font = pygame.font.Font(None, 24)
                symbol = font.render("$", True, DARK_YELLOW)
                window.blit(symbol, (powerup.x - camera_x + 10, powerup.y + 7))

                # Coin outline
                pygame.draw.circle(
                    window,
                    DARK_YELLOW,
                    (powerup.x - camera_x + 15, powerup.y + 15),
                    15,
                    1,
                )

        if show_powerup_text:
            font = pygame.font.Font(None, 36)
            text = font.render("Haha, You fell for it, Nice Try", True, WHITE)
            text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
            text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
            window.blit(text, (text_x, text_y))
            game_over_state = True

        # Draw cat
        if cat:
            window.blit(cat_image, (cat.x - camera_x, cat.y))

            # Draw instructions
            instruction_font = pygame.font.Font(None, 40)
            instruction_text = instruction_font.render(
                "Jump on the cat to kill it!", True, RED
            )
            instruction_x = 2000 - camera_x
            window.blit(instruction_text, (instruction_x, 100))

        # Draw coins
        for coin in coins:
            # Outer circle (main coin body)
            pygame.draw.circle(window, GOLD, (coin.x - camera_x + 10, coin.y + 10), 10)

            # Inner circle (for 3D effect)
            pygame.draw.circle(window, YELLOW, (coin.x - camera_x + 11, coin.y + 9), 8)

            # Coin shine (top-left highlight)
            pygame.draw.arc(
                window, WHITE, (coin.x - camera_x + 3, coin.y + 3, 14, 14), 0.9, 2.5, 2
            )

            pygame.draw.line(
                window,
                DARK_YELLOW,
                (coin.x - camera_x + 9, coin.y + 6),
                (coin.x - camera_x + 9, coin.y + 11),
                2,
            )
            pygame.draw.circle(
                window, DARK_YELLOW, (coin.x - camera_x + 9, coin.y + 14), 1
            )

            # Coin outline
            pygame.draw.circle(
                window, DARK_YELLOW, (coin.x - camera_x + 10, coin.y + 10), 10, 1
            )

        # Display coin counter
        font = pygame.font.Font(None, 36)
        coin_text = font.render(f"Coins: {coin_count}", True, WHITE)
        window.blit(coin_text, (10, 10))

        # untouchable coins
        for coin in untouchable_coins:
            # Outer circle (main coin body)
            pygame.draw.circle(window, GOLD, (coin.x - camera_x + 10, coin.y + 10), 10)

            # Inner circle (for 3D effect)
            pygame.draw.circle(window, YELLOW, (coin.x - camera_x + 11, coin.y + 9), 8)

            # Coin shine (top-left highlight)
            pygame.draw.arc(
                window, WHITE, (coin.x - camera_x + 3, coin.y + 3, 14, 14), 0.9, 2.5, 2
            )

            pygame.draw.line(
                window,
                DARK_YELLOW,
                (coin.x - camera_x + 9, coin.y + 6),
                (coin.x - camera_x + 9, coin.y + 11),
                2,
            )
            pygame.draw.circle(
                window, DARK_YELLOW, (coin.x - camera_x + 9, coin.y + 14), 1
            )

            # Coin outline
            pygame.draw.circle(
                window, DARK_YELLOW, (coin.x - camera_x + 10, coin.y + 10), 10, 1
            )

        # Draw flag
        flag_draw_pos = (flag.x - camera_x, flag.y)
        window.blit(flag_image, flag_draw_pos)

        # Draw blocks
        for block in blocks:
            window.blit(
                pygame.transform.scale(block_image, (BLOCK_WIDTH, BLOCK_HEIGHT)),
                (block.x - camera_x, block.y),
            )

        # Draw untouchable blocks
        for block in untouchable_blocks:
            pygame.draw.rect(
                window,
                BLUE,
                pygame.Rect(block.x - camera_x, block.y, block.width, block.height),
            )

        # Draw floor
        for floor_rect in floor_rects:
            pygame.draw.rect(
                window,
                GREEN,
                pygame.Rect(
                    floor_rect.x - camera_x,
                    floor_rect.y,
                    floor_rect.width,
                    floor_rect.height,
                ),
            )

    # Update the display
    pygame.display.update()

    # Limit the frame rate
    clock.tick(60)

# Print player choices and replay count
print("Player choices:", player_choices)
print("Total replays:", replay_count)

# At the end of your game loop or in a cleanup function
cap.release()

# Quit Pygame
pygame.quit()
