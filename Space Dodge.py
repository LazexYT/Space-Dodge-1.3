import pygame
import time
import random
import os
import sys
pygame.font.init()

# Window size
WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge") 

# Load background images
BG = pygame.transform.scale(pygame.image.load("bg.jpeg"), (WIDTH, HEIGHT))  # Game background
MAIN_MENU_BG = pygame.transform.scale(pygame.image.load("main menu.png"), (WIDTH, HEIGHT))  # Main menu background

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)  # This color was missing in the previous code

# Player properties
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_VEL = 5

# Star properties
STAR_WIDTH = 40
STAR_HEIGHT = 40
STAR_VEL = 3

# Fonts
FONT = pygame.font.SysFont("comicsans", 30)
FONT1 = pygame.font.SysFont("comicsans", 60)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)  # Yellow color for leaderboard button

# Button properties
button_rect_play = pygame.Rect(375, 340, 275, 100)
button_rect_login = pygame.Rect(WIDTH - 300, 50, 275, 80)  # Moved to top right corner
button_rect_retry = pygame.Rect(375, 360, 250, 100)
button_rect_menu = pygame.Rect(375, 500, 250, 100)
button_rect_settings = pygame.Rect(375, 640, 275, 100)  # Moved up
button_rect_quit = pygame.Rect(50, 50, 150, 80)  # Quit button in the left corner
button_rect_back = pygame.Rect(50, 50, 150, 80)  # Back button for difficulty screen
button_rect_leaderboard = pygame.Rect(700, 300, 280, 80)  # New leaderboard button between Icons and Settings
button_rect_icon_custom = pygame.Rect(375, 520, 275, 100)  # Moved up

button_rect_easy = pygame.Rect(375, 300, 250, 100)
button_rect_medium = pygame.Rect(375, 450, 250, 100)
button_rect_hard = pygame.Rect(375, 600, 250, 100)

# Login/Register input boxes
username_input = pygame.Rect(350, 250, 300, 50)
password_input = pygame.Rect(350, 350, 300, 50)
login_button = pygame.Rect(300, 450, 150, 50)
register_button = pygame.Rect(550, 450, 150, 50)

# Leaderboard difficulty selection buttons
leaderboard_easy_button = pygame.Rect(150, 200, 200, 80)
leaderboard_medium_button = pygame.Rect(400, 200, 200, 80)
leaderboard_hard_button = pygame.Rect(650, 200, 200, 80)

# Global variables for user authentication
current_user = None
users = {}  # Dictionary to store username:password pairs
user_scores = {}  # Dictionary to store username:{difficulty:score} pairs
user_rocket_settings = {}  # Dictionary to store username:{style, primary_color, secondary_color}
USER_DATA_FILE = "user_data.txt"

current_rocket_style = 0  # Default rocket style (Simple)
primary_color = RED  # Default primary color 

def load_user_data():
    global users, user_scores
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        username = parts[0]
                        password = parts[1]
                        users[username] = password
                        
                        # Initialize scores dictionary for each difficulty
                        if username not in user_scores:
                            user_scores[username] = {"easy": 0, "medium": 0, "hard": 0}
                        
                        # Parse scores for each difficulty
                        if len(parts) >= 5:  # Username, password, easy, medium, hard
                            try:
                                user_scores[username]["easy"] = int(parts[2])
                                user_scores[username]["medium"] = int(parts[3])
                                user_scores[username]["hard"] = int(parts[4])
                            except (ValueError, IndexError):
                                # If there's an error, keep default values
                                pass
                        
                        # Parse rocket settings if available
                        if len(parts) >= 8:  # Username, password, scores, rocket style, primary color R,G,B, secondary color R,G,B
                            try:
                                rocket_style = int(parts[5])
                                
                                # Parse primary color RGB values
                                primary_r = int(parts[6].split(':')[0])
                                primary_g = int(parts[6].split(':')[1])
                                primary_b = int(parts[6].split(':')[2])
                                
                                # Parse secondary color RGB values
                                secondary_r = int(parts[7].split(':')[0])
                                secondary_g = int(parts[7].split(':')[1])
                                secondary_b = int(parts[7].split(':')[2])
                                
                                # Initialize rocket settings
                                user_rocket_settings[username] = {
                                    "style": rocket_style,
                                    "primary_color": (primary_r, primary_g, primary_b),
                                    "secondary_color": (secondary_r, secondary_g, secondary_b),
                                    "volume": 100  # Default volume
                                }
                                
                                # Parse volume if available (9th value)
                                if len(parts) >= 9:
                                    try:
                                        volume = int(parts[8])
                                        user_rocket_settings[username]["volume"] = volume
                                    except (ValueError, IndexError):
                                        # Keep default volume if parsing fails
                                        pass
                                        
                            except (ValueError, IndexError):
                                # If there's an error, use default rocket settings
                                user_rocket_settings[username] = {
                                    "style": 0,  # Simple rocket
                                    "primary_color": RED,
                                    "secondary_color": BLUE,
                                    "volume": 100  # Default volume
                                }

# Updated save_user_data function to save volume settings
def save_user_data():
    with open(USER_DATA_FILE, 'w') as f:
        for username, password in users.items():
            # Get scores for each difficulty
            easy_score = user_scores.get(username, {}).get("easy", 0)
            medium_score = user_scores.get(username, {}).get("medium", 0)
            hard_score = user_scores.get(username, {}).get("hard", 0)
            
            # Get rocket settings
            settings = user_rocket_settings.get(username, {})
            style = settings.get("style", 0)
            primary = settings.get("primary_color", RED)
            secondary = settings.get("secondary_color", BLUE)
            volume = settings.get("volume", 100)
            
            # Format colors as strings
            primary_str = f"{primary[0]}:{primary[1]}:{primary[2]}"
            secondary_str = f"{secondary[0]}:{secondary[1]}:{secondary[2]}"
            
            # Write to file including volume
            f.write(f"{username},{password},{easy_score},{medium_score},{hard_score},{style},{primary_str},{secondary_str},{volume}\n")

def draw(player, elapsed_time, stars, difficulty):
    global current_user
    
    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
    WIN.blit(time_text, (10, 10))
    
    # Display current difficulty
    diff_text = FONT.render(f"Difficulty: {difficulty.capitalize()}", 1, "white")
    WIN.blit(diff_text, (10, 50))

    if current_user:
        user_text = FONT.render(f"User: {current_user}", 1, "white")
        WIN.blit(user_text, (WIDTH - user_text.get_width() - 10, 10))
        
        # Display best score for current difficulty
        if current_user in user_scores:
            best_score = user_scores[current_user].get(difficulty, 0)
            score_text = FONT.render(f"Best: {best_score}s", 1, "white")
            WIN.blit(score_text, (WIDTH - score_text.get_width() - 10, 50))

    pygame.draw.rect(WIN, primary_color, player)

    for star in stars:
        pygame.draw.rect(WIN, "yellow", star)

    pygame.display.update()

def main(star_count=3, difficulty = "easy"):
    global current_user
    
    player = pygame.Rect(475, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    star_add_increment = 700
    star_count_tracker = 0
    
    # Set the decrement rate based on difficulty
    if difficulty == "easy":
        decrement_rate = 0
        star_add_increment = 1150 - decrement_rate
        star_count = 4
        STAR_VEL = 3

    elif difficulty == "medium":
        decrement_rate = 0
        star_count = 6
        STAR_VEL = 5

    else:  # hard
        decrement_rate = 0
        star_count = 8
        STAR_VEL = 7

    stars = []
    hit = False

    run = True
    while run:
        star_count_tracker += clock.tick(60)
        elapsed_time = time.time() - start_time

        if star_count_tracker > star_add_increment:
            for _ in range(star_count):
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                stars.append(star)

            star_add_increment = max(200, star_add_increment - decrement_rate)
            star_count_tracker = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # Add escape key handling for pause
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Pause the game when Escape is pressed
                    pause_time_start = time.time()
                    pause_game(difficulty)
                    # Adjust the start time to account for pause duration
                    pause_time_end = time.time()
                    start_time += (pause_time_end - pause_time_start)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_d] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
        if keys[pygame.K_s] and player.y + PLAYER_VEL + player.height <= HEIGHT:
            player.y += PLAYER_VEL
        if keys[pygame.K_w] and player.y - PLAYER_VEL - player.height >= HEIGHT/2:
            player.y -= PLAYER_VEL
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL
        if keys[pygame.K_DOWN] and player.y + PLAYER_VEL + player.height <= HEIGHT:
            player.y += PLAYER_VEL
        if keys[pygame.K_UP] and player.y - PLAYER_VEL - player.height >= HEIGHT/2:
            player.y -= PLAYER_VEL

        for star in stars[:]:
            star.y += STAR_VEL
            if star.y > HEIGHT:
                stars.remove(star)
            elif star.y + star.height >= player.y and star.colliderect(player):
                stars.remove(star)
                hit = True
                break

        if hit:
            # Save score if logged in and it's a new high score for this difficulty
            if current_user:
                if current_user not in user_scores:
                    user_scores[current_user] = {"easy": 0, "medium": 0, "hard": 0}
                
                if round(elapsed_time) > user_scores[current_user].get(difficulty, 0):
                    user_scores[current_user][difficulty] = round(elapsed_time)
                    save_user_data()
            
            game_over(elapsed_time, difficulty)

        draw(player, elapsed_time, stars, difficulty)

    pygame.quit()

def game_over(score=0, difficulty = "easy"):
    global current_user
    
    font = pygame.font.SysFont("comicsans", 40)
    running = True
    while running:
        WIN.blit(BG, (0, 0))  # Display the game over screen background (bg.jpeg)

        # Display "You Lost!"
        lost_text = FONT1.render("You Lost!", 1, "white")
        WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2-75 - lost_text.get_height()/2 - 50))
        
        # Display score and difficulty
        score_text = font.render(f"Score: {round(score)}s on {difficulty.capitalize()} difficulty", 1, "white")
        WIN.blit(score_text, (WIDTH/2 - score_text.get_width()/2, HEIGHT/2+220 - score_text.get_height()/2 + 20))

        # Display personal best for this difficulty if logged in
        if current_user and current_user in user_scores:
            best_score = user_scores[current_user].get(difficulty, 0)
            best_text = font.render(f"Your Best: {best_score}s", 1, "white")
            WIN.blit(best_text, (WIDTH/2 - best_text.get_width()/2, HEIGHT/2+250 - best_text.get_height()/2 + 70))

        # Buttons for Retry and Main Menu
        pygame.draw.rect(WIN, BLACK, button_rect_retry)
        pygame.draw.rect(WIN, BLACK, button_rect_menu)

        text_retry = font.render("Try Again", True, WHITE)
        text_menu = font.render("Main Menu", True, WHITE)

        WIN.blit(text_retry, (button_rect_retry.centerx - text_retry.get_width() / 2, button_rect_retry.centery - text_retry.get_height() / 2))
        WIN.blit(text_menu, (button_rect_menu.centerx - text_menu.get_width() / 2, button_rect_menu.centery - text_menu.get_height() / 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_retry.collidepoint(event.pos):
                    main(difficulty=difficulty)
                if button_rect_menu.collidepoint(event.pos):
                    main_menu()

        pygame.display.update()

def login_screen():
    global current_user, current_rocket_style, primary_color, secondary_color
    
    username = ""
    password = ""
    message = ""
    active_input = None
    
    back_font = pygame.font.SysFont("comicsans", 40)
    font = pygame.font.SysFont("comicsans", 40)
    small_font = pygame.font.SysFont("comicsans", 30)
    
    running = True
    while running:
        WIN.blit(BG, (0, 0))
        
        # Title
        title_text = FONT1.render("Login / Register", 1, "white")
        WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 100))
        
        # Username field
        pygame.draw.rect(WIN, WHITE, username_input)
        username_text = small_font.render(username, True, BLACK)
        username_label = small_font.render("Username:", True, WHITE)
        WIN.blit(username_label, (username_input.x, username_input.y - 40))
        WIN.blit(username_text, (username_input.x + 10, username_input.y + 15))
        
        # Password field
        pygame.draw.rect(WIN, WHITE, password_input)
        password_display = '*' * len(password)
        password_text = small_font.render(password_display, True, BLACK)
        password_label = small_font.render("Password:", True, WHITE)
        WIN.blit(password_label, (password_input.x, password_input.y - 40))
        WIN.blit(password_text, (password_input.x + 10, password_input.y + 15))
        
        # Login and Register buttons
        pygame.draw.rect(WIN, GREEN, login_button)
        pygame.draw.rect(WIN, BLUE, register_button)
        login_text = small_font.render("Login", True, WHITE)
        register_text = small_font.render("Register", True, WHITE)
        WIN.blit(login_text, (login_button.centerx - login_text.get_width()/2, login_button.centery - login_text.get_height()/2))
        WIN.blit(register_text, (register_button.centerx - register_text.get_width()/2, register_button.centery - register_text.get_height()/2))
        
        # Back button
        pygame.draw.rect(WIN, RED, button_rect_back)
        back_text = back_font.render("BACK", True, WHITE)
        WIN.blit(back_text, (button_rect_back.centerx - back_text.get_width()/2, button_rect_back.centery - back_text.get_height()/2))
        
        # Display any messages
        if message:
            msg_text = small_font.render(message, True, WHITE)
            WIN.blit(msg_text, (WIDTH/2 - msg_text.get_width()/2, 550))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_input.collidepoint(event.pos):
                    active_input = "username"
                elif password_input.collidepoint(event.pos):
                    active_input = "password"
                elif login_button.collidepoint(event.pos):
                    if username in users and users[username] == password:
                        current_user = username
                        
                        # Load user's rocket settings if available
                        if username in user_rocket_settings:
                            current_rocket_style = user_rocket_settings[username]["style"]
                            primary_color = user_rocket_settings[username]["primary_color"]
                            secondary_color = user_rocket_settings[username]["secondary_color"]
                        
                        message = f"Login successful! Welcome {username}!"
                        # Return to main menu after successful login
                        time.sleep(1)
                        return True
                    else:
                        message = "Invalid username or password"
                elif register_button.collidepoint(event.pos):
                    if not username or not password:
                        message = "Username and password cannot be empty"
                    elif username in users:
                        message = "Username already exists"
                    else:
                        users[username] = password
                        # Initialize scores for all difficulties
                        user_scores[username] = {"easy": 0, "medium": 0, "hard": 0}
                        # Initialize rocket settings with defaults
                        user_rocket_settings[username] = {
                            "style": current_rocket_style,
                            "primary_color": primary_color,
                            "secondary_color": secondary_color
                        }
                        save_user_data()
                        current_user = username
                        message = "Registration successful!"
                        # Return to main menu after successful registration
                        time.sleep(1)
                        return True
                elif button_rect_back.collidepoint(event.pos):
                    return False
                else:
                    active_input = None
                    
            if event.type == pygame.KEYDOWN:
                if active_input == "username":
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.key == pygame.K_RETURN:
                        active_input = "password"
                    elif len(username) < 20:  # Limit username length
                        username += event.unicode
                elif active_input == "password":
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    elif event.key == pygame.K_RETURN:
                        # Try to login when Enter is pressed
                        if username in users and users[username] == password:
                            current_user = username
                            
                            # Load user's rocket settings if available
                            if username in user_rocket_settings:
                                current_rocket_style = user_rocket_settings[username]["style"]
                                primary_color = user_rocket_settings[username]["primary_color"]
                                secondary_color = user_rocket_settings[username]["secondary_color"]
                            
                            message = f"Login successful! Welcome {username}!"
                            time.sleep(1)
                            return True
                        else:
                            message = "Invalid username or password"
                    elif len(password) < 20:  # Limit password length
                        password += event.unicode
                        
        pygame.display.update()

# New function to display leaderboards
def leaderboard_screen():
    global user_scores
    
    back_font = pygame.font.SysFont("comicsans", 40)
    font = pygame.font.SysFont("comicsans", 60)
    small_font = pygame.font.SysFont("comicsans", 30)
    large_font = pygame.font.SysFont("comicsans", 40)
    
    # Track which difficulty leaderboard is being viewed
    current_difficulty = "easy"
    
    running = True
    while running:
        WIN.blit(BG, (0, 0))
        
        # Title
        title_text = font.render("LEADERBOARDS", True, WHITE)
        WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 80))
        
        # Back button
        pygame.draw.rect(WIN, RED, button_rect_back)
        back_text = back_font.render("BACK", True, WHITE)
        WIN.blit(back_text, (button_rect_back.centerx - back_text.get_width()/2, button_rect_back.centery - back_text.get_height()/2))
        
        # Difficulty selection buttons
        pygame.draw.rect(WIN, BLUE if current_difficulty == "easy" else BLACK, leaderboard_easy_button)
        pygame.draw.rect(WIN, BLUE if current_difficulty == "medium" else BLACK, leaderboard_medium_button)
        pygame.draw.rect(WIN, BLUE if current_difficulty == "hard" else BLACK, leaderboard_hard_button)
        
        easy_text = large_font.render("EASY", True, WHITE)
        medium_text = large_font.render("MEDIUM", True, WHITE)
        hard_text = large_font.render("HARD", True, WHITE)
        
        WIN.blit(easy_text, (leaderboard_easy_button.centerx - easy_text.get_width()/2, leaderboard_easy_button.centery - easy_text.get_height()/2))
        WIN.blit(medium_text, (leaderboard_medium_button.centerx - medium_text.get_width()/2, leaderboard_medium_button.centery - medium_text.get_height()/2))
        WIN.blit(hard_text, (leaderboard_hard_button.centerx - hard_text.get_width()/2, leaderboard_hard_button.centery - hard_text.get_height()/2))
        
        # Get scores for the selected difficulty and sort them
        difficulty_scores = []
        for username, scores in user_scores.items():
            # Filter out admin and Developer accounts
            if username.lower() not in ["admin", "developer"]:
                score = scores.get(current_difficulty, 0)
                difficulty_scores.append((username, score))
        
        # Sort by score (descending)
        difficulty_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Display current difficulty title
        diff_title = large_font.render(f"{current_difficulty.upper()} LEADERBOARD", True, YELLOW)
        WIN.blit(diff_title, (WIDTH/2 - diff_title.get_width()/2, 300))
        
        # Display top players
        start_y = 350
        rank = 1
        
        # Display table headers
        header_font = pygame.font.SysFont("comicsans", 35)
        rank_header = header_font.render("RANK", True, WHITE)
        name_header = header_font.render("PLAYER", True, WHITE)
        score_header = header_font.render("SCORE", True, WHITE)
        
        WIN.blit(rank_header, (250, start_y))
        WIN.blit(name_header, (400, start_y))
        WIN.blit(score_header, (650, start_y))
        
        # Draw a line under headers
        pygame.draw.line(WIN, WHITE, (200, start_y + 40), (800, start_y + 40), 2)
        
        start_y += 60
        
        # Display scores
        if difficulty_scores:
            for i, (username, score) in enumerate(difficulty_scores[:10]):  # Show top 10
                rank_text = small_font.render(f"{rank}", True, WHITE)
                name_text = small_font.render(username, True, WHITE)
                
                if score > 0:
                    score_text = small_font.render(f"{score}s", True, GREEN)
                else:
                    score_text = small_font.render("No score", True, GRAY)
                
                WIN.blit(rank_text, (250, start_y + i * 40))
                WIN.blit(name_text, (400, start_y + i * 40))
                WIN.blit(score_text, (650, start_y + i * 40))
                
                rank += 1
        else:
            no_scores = large_font.render("No scores yet!", True, RED)
            WIN.blit(no_scores, (WIDTH/2 - no_scores.get_width()/2, start_y + 100))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_back.collidepoint(event.pos):
                    return
                elif leaderboard_easy_button.collidepoint(event.pos):
                    current_difficulty = "easy"
                elif leaderboard_medium_button.collidepoint(event.pos):
                    current_difficulty = "medium"
                elif leaderboard_hard_button.collidepoint(event.pos):
                    current_difficulty = "hard"
        
        pygame.display.update()

def pause_game(difficulty):
    global current_user
    
    font = pygame.font.SysFont("comicsans", 60)
    button_font = pygame.font.SysFont("comicsans", 40)
    
    # Create button rectangles for the pause menu
    button_rect_unpause = pygame.Rect(375, 300, 250, 80)
    button_rect_retry = pygame.Rect(375, 400, 250, 80)
    button_rect_menu = pygame.Rect(375, 500, 250, 80)
    
    # Take a screenshot of the current game state
    background = WIN.copy()
    
    paused = True
    while paused:
        # Start with a clean copy of the background
        WIN.blit(background, (0, 0))
        
        # Create a semi-transparent overlay for the whole screen
        s = pygame.Surface((WIDTH, HEIGHT))  # Create a surface the same size as the window
        s.set_alpha(128)  # Set alpha to around 70% (adjust as needed for desired transparency)
        s.fill((0, 0, 0))  # Fill with black
        WIN.blit(s, (0, 0))  # Apply the overlay
        
        # Title with solid background to ensure visibility
        pause_text = font.render("GAME PAUSED", True, WHITE)
        title_bg = pygame.Rect(WIDTH/2 - pause_text.get_width()/2 - 10, 145, 
                              pause_text.get_width() + 20, pause_text.get_height() + 10)
        pygame.draw.rect(WIN, (0, 0, 0), title_bg)
        WIN.blit(pause_text, (WIDTH/2 - pause_text.get_width()/2, 150))
        
        # Draw buttons (these remain solid)
        pygame.draw.rect(WIN, BLACK, button_rect_unpause)
        pygame.draw.rect(WIN, BLACK, button_rect_retry)
        pygame.draw.rect(WIN, BLACK, button_rect_menu)
        
        # Button text
        text_unpause = button_font.render("RESUME", True, WHITE)
        text_retry = button_font.render("RETRY", True, WHITE)
        text_menu = button_font.render("MAIN MENU", True, WHITE)
        
        WIN.blit(text_unpause, (button_rect_unpause.centerx - text_unpause.get_width()/2, 
                             button_rect_unpause.centery - text_unpause.get_height()/2))
        WIN.blit(text_retry, (button_rect_retry.centerx - text_retry.get_width()/2, 
                           button_rect_retry.centery - text_retry.get_height()/2))
        WIN.blit(text_menu, (button_rect_menu.centerx - text_menu.get_width()/2, 
                          button_rect_menu.centery - text_menu.get_height()/2))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Press Escape again to unpause
                    paused = False
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_unpause.collidepoint(event.pos):
                    paused = False
                if button_rect_retry.collidepoint(event.pos):
                    main(difficulty=difficulty)
                if button_rect_menu.collidepoint(event.pos):
                    main_menu()

def main_menu():

    font = pygame.font.SysFont("comicsans", 70)
    med_font = pygame.font.SysFont("comicsans", 50)
    leaderboard_font = pygame.font.SysFont("comicsans", 45)  # New font for leaderboard
    small_font = pygame.font.SysFont("comicsans", 30)
    quit_font = pygame.font.SysFont("comicsans", 40)

    global current_user, users, user_scores
    
    load_user_data()  # Load user data at startup
    
    # Add admin account with password nimdA2012
    if "admin" not in users:
        users["admin"] = "nimdA2012"
        if "admin" not in user_scores:
            user_scores["admin"] = {"easy": 0, "medium": 0, "hard": 0}
        save_user_data()
        print("Admin account created successfully")

    if "PlayTester" not in users:
        users["PlayTester"] = "PlayGameTester2012"
        if "PlayTester" not in user_scores:
             user_scores["PlayTester"] = {"easy": 0, "medium": 0, "hard": 0}
        save_user_data()
        print("PlayTester account created successfully")

    if "Developer" not in users:
        users["Developer"] = "dEvEloPeR.0603"
        if "Developer" not in user_scores:
             user_scores["Developer"] = {"easy": 0, "medium": 0, "hard": 0}
        save_user_data()
        print("Developer account created successfully")
    
    running = True
    while running:
        WIN.blit(MAIN_MENU_BG, (0, 0))

        pygame.draw.rect(WIN, BLACK, button_rect_play)
        pygame.draw.rect(WIN, BLACK, button_rect_icon_custom)
        pygame.draw.rect(WIN, YELLOW, button_rect_leaderboard)  # Leaderboard button in yellow
        pygame.draw.rect(WIN, BLACK, button_rect_settings)
        pygame.draw.rect(WIN, RED, button_rect_quit)  # Quit button in red
        
        # Login/Register button in the top right
        pygame.draw.rect(WIN, BLUE, button_rect_login)
        
        text_play = font.render("PLAY", True, WHITE)
        text_icon_custom = font.render("Icons", True, WHITE)
        # Create a smaller font for the leaderboard button
        leaderboard_font = pygame.font.SysFont("comicsans", 45)  # Reduced from 70 to 45
        text_leaderboard = leaderboard_font.render("Leaderboard", True, BLACK)
        text_settings = font.render("Settings", True, WHITE)
        text_quit = quit_font.render("QUIT", True, WHITE)
        
        # Login/Register text
        if current_user:
            text_login = small_font.render("LOGOUT", True, WHITE)
        else:
            text_login = small_font.render("LOGIN/REGISTER", True, WHITE)

        # Display current user if logged in
        if current_user:
            user_text = small_font.render(f"User: {current_user}", True, RED)
            WIN.blit(user_text, (WIDTH - user_text.get_width() - 30, 130))  # Below login button
            
            # Show high scores for all difficulties if available
            if current_user in user_scores:
                easy_score = user_scores[current_user].get("easy", 0)
                medium_score = user_scores[current_user].get("medium", 0)
                hard_score = user_scores[current_user].get("hard", 0)
                
                easy_text = small_font.render(f"Easy Best: {easy_score}s", True, BLUE)
                medium_text = small_font.render(f"Medium Best: {medium_score}s", True, BLUE)
                hard_text = small_font.render(f"Hard Best: {hard_score}s", True, BLUE)
                
                WIN.blit(easy_text, (WIDTH - easy_text.get_width() - 30, 170))
                WIN.blit(medium_text, (WIDTH - medium_text.get_width() - 30, 200))
                WIN.blit(hard_text, (WIDTH - hard_text.get_width() - 30, 230))

        # Center the text on the buttons
        WIN.blit(text_play, (button_rect_play.centerx - text_play.get_width() / 2, 
                           button_rect_play.centery - text_play.get_height() / 2))
        WIN.blit(text_login, (button_rect_login.centerx - text_login.get_width() / 2, 
                            button_rect_login.centery - text_login.get_height() / 2))
        WIN.blit(text_icon_custom, (button_rect_icon_custom.centerx - text_icon_custom.get_width() / 2, 
                                  button_rect_icon_custom.centery - text_icon_custom.get_height() / 2))
        WIN.blit(text_leaderboard, (button_rect_leaderboard.centerx - text_leaderboard.get_width() / 2, 
                                 button_rect_leaderboard.centery - text_leaderboard.get_height() / 2))
        WIN.blit(text_settings, (button_rect_settings.centerx - text_settings.get_width() / 2, 
                               button_rect_settings.centery - text_settings.get_height() / 2))
        WIN.blit(text_quit, (button_rect_quit.centerx - text_quit.get_width() / 2, 
                           button_rect_quit.centery - text_quit.get_height() / 2)) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Make sure we properly exit when the window close button is clicked
                running = False
                pygame.quit()
                import sys
                sys.exit()

            # Fix: Combine all MOUSEBUTTONDOWN checks into a single if statement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_settings.collidepoint(event.pos):
                    settings_menu()  # Call the settings menu function
                elif button_rect_icon_custom.collidepoint(event.pos):
                    # Check if icons_menu function exists and print debug info
                    print("Icons button clicked!")
                    try:
                        icons_menu()
                        print("icons_menu function executed")
                    except NameError:
                        print("icons_menu function is not defined!")
                        # Temporary placeholder for icons_menu if it doesn't exist
                        temp_message = FONT.render("Icons feature coming soon!", True, WHITE)
                        WIN.blit(temp_message, (WIDTH/2 - temp_message.get_width()/2, 400))
                        pygame.display.update()
                        pygame.time.delay(2000)  # Show message for 2 seconds
                elif button_rect_play.collidepoint(event.pos):
                    difficulty_screen()
                elif button_rect_login.collidepoint(event.pos):
                    if current_user:
                        # Logout functionality
                        current_user = None
                    else:
                        login_screen()
                elif button_rect_leaderboard.collidepoint(event.pos):
                    leaderboard_screen()
                elif button_rect_quit.collidepoint(event.pos):
                    # Make sure we properly exit when quit button is clicked
                    running = False
                    pygame.quit()
                    import sys
                    sys.exit()

        pygame.display.update()

def difficulty_screen():
    global current_user
    
    font = pygame.font.SysFont("comicsans", 60)
    back_font = pygame.font.SysFont("comicsans", 40)
    score_font = pygame.font.SysFont("comicsans", 30)
    
    running = True
    while running:
        WIN.blit(BG, (0, 0))

        # Title
        title_text = font.render("SELECT DIFFICULTY", True, WHITE)
        WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 150))

        pygame.draw.rect(WIN, BLACK, button_rect_easy)
        pygame.draw.rect(WIN, BLACK, button_rect_medium)
        pygame.draw.rect(WIN, BLACK, button_rect_hard)
        pygame.draw.rect(WIN, RED, button_rect_back)  # Back button in blue

        text_easy = font.render("EASY", True, WHITE)
        text_medium = font.render("MEDIUM", True, WHITE)
        text_hard = font.render("HARD", True, WHITE)
        text_back = back_font.render("BACK", True, WHITE)

        WIN.blit(text_easy, (button_rect_easy.centerx - text_easy.get_width() / 2, 
                           button_rect_easy.centery - text_easy.get_height() / 2))
        WIN.blit(text_medium, (button_rect_medium.centerx - text_medium.get_width() / 2, 
                             button_rect_medium.centery - text_medium.get_height() / 2))
        WIN.blit(text_hard, (button_rect_hard.centerx - text_hard.get_width() / 2, 
                           button_rect_hard.centery - text_hard.get_height() / 2))
        WIN.blit(text_back, (button_rect_back.centerx - text_back.get_width() / 2, 
                           button_rect_back.centery - text_back.get_height() / 2))

        # Display high scores for each difficulty if logged in
        if current_user and current_user in user_scores:
            easy_score = user_scores[current_user].get("easy", 0)
            medium_score = user_scores[current_user].get("medium", 0)
            hard_score = user_scores[current_user].get("hard", 0)
            
            easy_score_text = score_font.render(f"Your Best: {easy_score}s.", True, BLUE)
            medium_score_text = score_font.render(f"Your Best: {medium_score}s.", True, BLUE)
            hard_score_text = score_font.render(f"Your Best: {hard_score}s.", True, BLUE)
            
            WIN.blit(easy_score_text, (button_rect_easy.centerx - easy_score_text.get_width() / 2, 
                                     button_rect_easy.bottom))
            WIN.blit(medium_score_text, (button_rect_medium.centerx - medium_score_text.get_width() / 2, 
                                       button_rect_medium.bottom))
            WIN.blit(hard_score_text, (button_rect_hard.centerx - hard_score_text.get_width() / 2, 
                                     button_rect_hard.bottom))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_easy.collidepoint(event.pos):
                    main(star_count=4, difficulty="easy")
                if button_rect_medium.collidepoint(event.pos):
                    main(star_count=6, difficulty="medium")
                if button_rect_hard.collidepoint(event.pos):
                    main(star_count=8, difficulty="hard")
                if button_rect_back.collidepoint(event.pos):
                    main_menu()

        pygame.display.update()

def settings_menu():
    global current_user, volume_level

    back_font = pygame.font.SysFont("comicsans", 40)
    font = pygame.font.SysFont("comicsans", 60)
    med_font = pygame.font.SysFont("comicsans", 40)
    small_font = pygame.font.SysFont("comicsans", 30)
    
    # Initialize volume based on user settings if logged in
    if current_user and current_user in user_rocket_settings:
        volume_level = user_rocket_settings[current_user].get("volume", 100)
    else:
        volume_level = 100  # Default for users not logged in
    
    # Create settings option buttons
    volume_button = pygame.Rect(375, 300, 250, 80)
    controls_button = pygame.Rect(375, 400, 250, 80)
    credits_button = pygame.Rect(375, 500, 250, 80)
    button_rect_back = pygame.Rect(50, 50, 150, 80)  # Back button
    
    # Track which section is active
    active_section = "main"  # main, volume, controls, credits
    
    # For volume controls
    volume_slider_rect = pygame.Rect(300, 350, 400, 30)
    volume_handle_rect = pygame.Rect(300 + int((volume_level / 100) * 400) - 10, 335, 20, 60)  # Position based on current volume
    
    running = True
    while running:
        WIN.blit(BG, (0, 0))
        
        # Draw the back button for all screens
        pygame.draw.rect(WIN, RED, button_rect_back)
        back_text = back_font.render("BACK", True, WHITE)
        WIN.blit(back_text, (button_rect_back.centerx - back_text.get_width()/2, 
                          button_rect_back.centery - back_text.get_height()/2))
        
        # Main settings screen
        if active_section == "main":
            # Title
            title_text = font.render("SETTINGS", True, WHITE)
            WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 150))
            
            # Draw option buttons
            pygame.draw.rect(WIN, BLACK, volume_button)
            pygame.draw.rect(WIN, BLACK, controls_button)
            pygame.draw.rect(WIN, BLACK, credits_button)
            
            # Button texts
            volume_text = med_font.render("Volume", True, WHITE)
            controls_text = med_font.render("Controls", True, WHITE)
            credits_text = med_font.render("Credits", True, WHITE)
            
            WIN.blit(volume_text, (volume_button.centerx - volume_text.get_width()/2, 
                                volume_button.centery - volume_text.get_height()/2))
            WIN.blit(controls_text, (controls_button.centerx - controls_text.get_width()/2, 
                                  controls_button.centery - controls_text.get_height()/2))
            WIN.blit(credits_text, (credits_button.centerx - credits_text.get_width()/2, 
                                 credits_button.centery - credits_text.get_height()/2))
            
        # Volume settings screen
        elif active_section == "volume":
            # Title
            title_text = font.render("VOLUME SETTINGS", True, WHITE)
            WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 150))
            
            # Volume level text
            volume_val_text = med_font.render(f"Volume: {volume_level}%", True, WHITE)
            WIN.blit(volume_val_text, (WIDTH/2 - volume_val_text.get_width()/2, 250))
            
            # Draw slider background
            pygame.draw.rect(WIN, GRAY, volume_slider_rect)
            
            # Draw filled portion based on volume
            filled_width = int((volume_level / 100) * volume_slider_rect.width)
            pygame.draw.rect(WIN, BLUE, pygame.Rect(volume_slider_rect.x, volume_slider_rect.y, 
                                                 filled_width, volume_slider_rect.height))
            
            # Draw slider handle
            handle_x = volume_slider_rect.x + filled_width - 10
            volume_handle_rect.x = handle_x
            pygame.draw.rect(WIN, WHITE, volume_handle_rect)
            
            # Volume buttons for precise control
            minus_button = pygame.Rect(240, 350, 40, 30)
            plus_button = pygame.Rect(720, 350, 40, 30)
            
            pygame.draw.rect(WIN, RED, minus_button)
            pygame.draw.rect(WIN, GREEN, plus_button)
            
            minus_text = med_font.render("-", True, WHITE)
            plus_text = med_font.render("+", True, WHITE)
            
            WIN.blit(minus_text, (minus_button.centerx - minus_text.get_width()/2, 
                               minus_button.centery - minus_text.get_height()/2))
            WIN.blit(plus_text, (plus_button.centerx - plus_text.get_width()/2, 
                              plus_button.centery - plus_text.get_height()/2))
            
            # Sound effect hint
            hint_text = small_font.render("Changes will affect sound effects when implemented", True, LIGHT_GRAY)
            WIN.blit(hint_text, (WIDTH/2 - hint_text.get_width()/2, 420))
            
            # Add save status text if logged in
            if current_user:
                save_text = small_font.render("Volume setting will be saved to your profile", True, GREEN)
                WIN.blit(save_text, (WIDTH/2 - save_text.get_width()/2, 460))
            else:
                login_text = small_font.render("Log in to save your volume setting", True, YELLOW)
                WIN.blit(login_text, (WIDTH/2 - login_text.get_width()/2, 460))
            
        # Controls screen
        elif active_section == "controls":
            # Title
            title_text = font.render("GAME CONTROLS", True, WHITE)
            WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 150))
            
            # Controls information
            control_texts = [
                "Movement Controls:",
                "WASD or Arrow Keys - Move the player",
                "",
                "Game Controls:",
                "Escape - Pause game",
                "",
                "Objective:",
                "Avoid the falling stars for as long as possible",
                "Your score is the time survived in seconds"
            ]
            
            y_offset = 250
            for text in control_texts:
                if text == "Movement Controls:" or text == "Game Controls:" or text == "Objective:":
                    rendered_text = med_font.render(text, True, YELLOW)
                else:
                    rendered_text = small_font.render(text, True, WHITE)
                WIN.blit(rendered_text, (WIDTH/2 - rendered_text.get_width()/2, y_offset))
                y_offset += 40
                
        # Credits screen
        elif active_section == "credits":
            # Title
            title_text = font.render("CREDITS", True, WHITE)
            WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 150))
            
            # Credits information
            credit_texts = [
                "Space Dodge Game",
                "Created by: LazexYT",
                "",
                "Assets:",
                "Background images from Google",
                "Fonts: Pygame default",
                "",
                "Version 1.2",
                "© 2025 Space Dodge Studios"
            ]
            
            y_offset = 250
            for i, text in enumerate(credit_texts):
                if i == 0:  # Game title
                    rendered_text = med_font.render(text, True, YELLOW)
                elif i == 1 or i == 3:  # Section headers
                    rendered_text = med_font.render(text, True, BLUE)
                else:
                    rendered_text = small_font.render(text, True, WHITE)
                WIN.blit(rendered_text, (WIDTH/2 - rendered_text.get_width()/2, y_offset))
                y_offset += 40
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle back button for all screens
                if button_rect_back.collidepoint(event.pos):
                    if active_section == "main":
                        # Save volume setting before returning to main menu
                        if current_user:
                            if current_user in user_rocket_settings:
                                user_rocket_settings[current_user]["volume"] = volume_level
                            else:
                                user_rocket_settings[current_user] = {
                                    "style": 0,  # Default
                                    "primary_color": RED,
                                    "secondary_color": BLUE,
                                    "volume": volume_level
                                }
                            save_user_data()  # Save changes to file
                        return
                    else:
                        # Return to main settings menu
                        active_section = "main"
                
                # Handle main menu button clicks
                if active_section == "main":
                    if volume_button.collidepoint(event.pos):
                        active_section = "volume"
                    elif controls_button.collidepoint(event.pos):
                        active_section = "controls"
                    elif credits_button.collidepoint(event.pos):
                        active_section = "credits"
                
                # Handle volume controls
                elif active_section == "volume":
                    if volume_slider_rect.collidepoint(event.pos):
                        # Calculate volume based on click position
                        click_x = event.pos[0]
                        relative_x = click_x - volume_slider_rect.x
                        volume_level = max(0, min(100, int((relative_x / volume_slider_rect.width) * 100)))
                    
                    # Handle plus and minus buttons
                    if pygame.Rect(240, 350, 40, 30).collidepoint(event.pos):  # Minus button
                        volume_level = max(0, volume_level - 5)
                    if pygame.Rect(720, 350, 40, 30).collidepoint(event.pos):  # Plus button
                        volume_level = min(100, volume_level + 5)
            
            # Handle dragging for volume slider
            if event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                if volume_handle_rect.collidepoint(event.pos) or volume_slider_rect.collidepoint(event.pos):
                    if active_section == "volume":
                        # Update volume based on drag position
                        mouse_x = event.pos[0]
                        relative_x = mouse_x - volume_slider_rect.x
                        volume_level = max(0, min(100, int((relative_x / volume_slider_rect.width) * 100)))
        
        pygame.display.update()
    
    # Save volume setting when exiting the settings menu
    if current_user:
        if current_user in user_rocket_settings:
            user_rocket_settings[current_user]["volume"] = volume_level
        else:
            user_rocket_settings[current_user] = {
                "style": 0,  # Default
                "primary_color": RED,
                "secondary_color": BLUE,
                "volume": volume_level
            }
        save_user_data()

    # Save volume setting when exiting the settings menu
    if current_user:
        if current_user in user_rocket_settings:
            user_rocket_settings[current_user]["volume"] = volume_level
        else:
            user_rocket_settings[current_user] = {
                "style": 0,  # Default
                "primary_color": RED,
                "secondary_color": BLUE,
                "volume": volume_level
            }
        save_user_data()

# Rocket styles
rocket_styles = ["Simple", "Classic", "Modern"]

# Default rocket appearance settings
current_rocket_style = 0  # Default to Simple style
primary_color = RED  # Default primary color
secondary_color = BLUE  # Default secondary color

# Function to draw rockets with fire effect
def draw_rocket(surface, x, y, width, height, style, color1, color2):
    # Base shape for all rocket styles
    if style == 0:  # Simple rocket
        # Rocket body
        pygame.draw.rect(surface, color1, (x - width//2, y, width, height//2))
        # Rocket tip - more pointed
        pygame.draw.polygon(surface, color2, [(x - width//2, y), (x, y - height//3), (x + width//2, y)])
        # Rocket fins - larger and more stylized
        pygame.draw.polygon(surface, color2, [(x - width//2, y + height//2), (x - width*0.8, y + height//2), (x - width//2, y + height//5)])
        pygame.draw.polygon(surface, color2, [(x + width//2, y + height//2), (x + width*0.8, y + height//2), (x + width//2, y + height//5)])
        # Rocket bottom
        pygame.draw.rect(surface, color2, (x - width//4, y + height//2, width//2, height//4))
        
        # Rocket windows
        window_color = (200, 200, 255)
        pygame.draw.circle(surface, window_color, (x, y + height//5), width//6)
        
        # Fire effect
        draw_rocket_fire(surface, x, y + height*0.75, width//2, height//3)
    
    elif style == 1:  # Classic rocket
        # Rocket body - smoother
        pygame.draw.rect(surface, color1, (x - width//3, y, 2*width//3, height//2))
        # Rounded top
        pygame.draw.ellipse(surface, color1, (x - width//3, y - height//6, 2*width//3, height//3))
        # Rocket tip
        pygame.draw.polygon(surface, color2, [(x - width//3, y - height//10), (x, y - height//2), (x + width//3, y - height//10)])
        # Rocket fins - more detailed
        pygame.draw.polygon(surface, color2, [(x - width//3, y + height//2), (x - width*0.6, y + height*0.6), (x - width//3, y + height//4)])
        pygame.draw.polygon(surface, color2, [(x + width//3, y + height//2), (x + width*0.6, y + height*0.6), (x + width//3, y + height//4)])
        # Rocket bottom
        pygame.draw.rect(surface, color2, (x - width//6, y + height//2, width//3, height//3))
        
        # Rocket details
        detail_color = (min(color1[0] + 40, 255), min(color1[1] + 40, 255), min(color1[2] + 40, 255))
        pygame.draw.line(surface, detail_color, (x - width//6, y + height//4), (x + width//6, y + height//4), 2)
        pygame.draw.line(surface, detail_color, (x - width//6, y + height//3), (x + width//6, y + height//3), 2)
        
        # Windows
        window_color = (200, 200, 255)
        pygame.draw.circle(surface, window_color, (x, y + height//5), width//8)
        pygame.draw.circle(surface, window_color, (x, y + height//3), width//10)
        
        # Fire effect - larger
        draw_rocket_fire(surface, x, y + height*0.8, width*0.6, height*0.4)
    
    elif style == 2:  # Modern rocket
        # Sleek rocket body
        pygame.draw.ellipse(surface, color1, (x - width*0.4, y, width*0.8, height*0.6))
        
        # Rocket tip - more aerodynamic
        pygame.draw.polygon(surface, color2, [(x - width*0.25, y), (x, y - height*0.4), (x + width*0.25, y)])
        
        # Rocket fins - curved and modern
        fin_color = (min(color2[0] + 30, 255), min(color2[1] + 30, 255), min(color2[2] + 30, 255))
        pygame.draw.arc(surface, fin_color, (x - width*0.8, y + height*0.3, width*0.8, height*0.4), 0, 3.14/2, 3)
        pygame.draw.arc(surface, fin_color, (x, y + height*0.3, width*0.8, height*0.4), 3.14/2, 3.14, 3)
        
        # Rocket bottom - more detailed
        pygame.draw.ellipse(surface, color2, (x - width//4, y + height*0.5, width//2, height//5))
        
        # Metallic details
        detail_color = (180, 180, 200)
        pygame.draw.line(surface, detail_color, (x - width*0.3, y + height*0.2), (x + width*0.3, y + height*0.2), 2)
        pygame.draw.line(surface, detail_color, (x - width*0.3, y + height*0.3), (x + width*0.3, y + height*0.3), 2)
        pygame.draw.line(surface, detail_color, (x - width*0.3, y + height*0.4), (x + width*0.3, y + height*0.4), 2)
        
        # Windows - modern style
        window_color = (150, 220, 255)
        pygame.draw.ellipse(surface, window_color, (x - width*0.15, y + height*0.1, width*0.3, height*0.15))
        pygame.draw.ellipse(surface, (220, 220, 255), (x - width*0.12, y + height*0.12, width*0.24, height*0.11))
        
        # Advanced fire effect
        draw_rocket_fire(surface, x, y + height*0.65, width*0.5, height*0.5)

# Function to draw rocket fire
def draw_rocket_fire(surface, x, y, width, height):
    # Create a dynamic fire effect with multiple colors
    fire_colors = [
        (255, 69, 0),    # Red-orange
        (255, 140, 0),   # Dark orange
        (255, 165, 0),   # Orange
        (255, 215, 0)    # Gold
    ]
    
    # Main fire cone
    for i in range(4):
        fire_width = width * (1 - i*0.2)
        fire_height = height * (1 - i*0.15)
        fire_y_offset = y + i * height * 0.1
        
        points = [
            (x - fire_width/2, fire_y_offset),
            (x, fire_y_offset + fire_height),
            (x + fire_width/2, fire_y_offset)
        ]
        pygame.draw.polygon(surface, fire_colors[i], points)
    
    # Add some sparks/embers for realism
    for _ in range(6):
        spark_x = x + random.randint(-int(width*0.6), int(width*0.6))
        spark_y = y + random.randint(int(height*0.5), int(height*1.2))
        spark_radius = random.randint(2, 5)
        spark_color = random.choice(fire_colors)
        pygame.draw.circle(surface, spark_color, (spark_x, spark_y), spark_radius)

def icons_menu():
    """Main function for the icons customization menu"""
    # Fonts
    back_font = pygame.font.SysFont("comicsans", 40)
    font = pygame.font.SysFont("comicsans", 60)
    med_font = pygame.font.SysFont("comicsans", 40)
    small_font = pygame.font.SysFont("comicsans", 30)
    
    global primary_color, current_user
    
    # Store initial settings to check for changes later
    initial_primary = primary_color
    
    # Back button
    button_rect_back = pygame.Rect(50, 50, 150, 80)

    # Available colors for selection
    color_options = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, WHITE, BLACK, GRAY]
    color_names = ["Red", "Green", "Blue", "Yellow", "Orange", "Purple", "White", "Black", "Gray"]
    
    # Color selection buttons
    color_buttons = []
    for i in range(len(color_options)):
        row = i // 3
        col = i % 3
        color_buttons.append(pygame.Rect(
            WIDTH/2 - 200 + col * 150,
            250 + row * 100,
            100,
            60
        ))
    
    # Display login status
    login_status = small_font.render(f"{'Logged in as: ' + current_user if current_user else 'Not logged in'}", True, WHITE)
    
    running = True
    while running:
        WIN.blit(BG, (0, 0))
        
        # Draw the back button
        pygame.draw.rect(WIN, RED, button_rect_back)
        back_text = back_font.render("BACK", True, WHITE)
        WIN.blit(back_text, (button_rect_back.centerx - back_text.get_width()/2, 
                          button_rect_back.centery - back_text.get_height()/2))
        
        # Draw login status
        WIN.blit(login_status, (WIDTH - login_status.get_width() - 20, 50))
        
        # Draw current rocket (simple rectangle)
        pygame.draw.rect(WIN, primary_color, (WIDTH - 150, 520, 80, 140))
        preview_text = small_font.render("Current Color:", True, WHITE)
        WIN.blit(preview_text, (WIDTH - 210, 450))
        
        # Title
        title_text = font.render("COLOR CUSTOMIZER", True, WHITE)
        WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 150))
        
        # Draw color options directly on main screen
        for i, button in enumerate(color_buttons):
            pygame.draw.rect(WIN, color_options[i], button)
            pygame.draw.rect(WIN, BLACK, button, 2)  # Border
            
            # Add color name
            color_name = small_font.render(color_names[i], True, BLACK if color_options[i] in [WHITE, YELLOW, LIGHT_BLUE] else WHITE)
            WIN.blit(color_name, (button.centerx - color_name.get_width()/2, 
                               button.centery - color_name.get_height()/2))
            
        # Highlight the selected color
        for i, color in enumerate(color_options):
            if color == primary_color:
                pygame.draw.rect(WIN, GREEN, color_buttons[i], 4)
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Save settings if logged in and changes were made
                if current_user and initial_primary != primary_color:
                    user_rocket_settings[current_user] = {
                        "primary_color": primary_color
                    }
                    save_user_data()
                
                running = False
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle back button
                if button_rect_back.collidepoint(event.pos):
                    # Save settings if logged in and changes were made
                    if current_user and initial_primary != primary_color:
                        user_rocket_settings[current_user] = {
                            "primary_color": primary_color
                        }
                        save_user_data()
                    
                    # Return to main menu
                    return
                
                # Handle color selection directly on main screen
                for i, button in enumerate(color_buttons):
                    if button.collidepoint(event.pos):
                        primary_color = color_options[i]
                        
                        # Save immediately if user is logged in
                        if current_user:
                            if current_user not in user_rocket_settings:
                                user_rocket_settings[current_user] = {
                                    "primary_color": primary_color
                                }
                            else:
                                user_rocket_settings[current_user]["primary_color"] = primary_color
                            save_user_data()
        
        pygame.display.update()

# Initialize user rocket settings when the game starts
def initialize_game():
    global current_rocket_style, primary_color, secondary_color
    
    # Load all user data
    load_user_data()
    
    # If user is already logged in, load their rocket settings
    if current_user and current_user in user_rocket_settings:
        current_rocket_style = user_rocket_settings[current_user]["style"]
        primary_color = user_rocket_settings[current_user]["primary_color"]
        secondary_color = user_rocket_settings[current_user]["secondary_color"]

# Also make sure to call initialize_game() at the start of your main_menu function
# or wherever the game first initializes

if __name__ == "__main__":
    main_menu()