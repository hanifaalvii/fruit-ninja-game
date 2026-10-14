import pygame
import random
import sys
import math
import array

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)

WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((800, 600), pygame.SCALED)
pygame.display.set_caption("Fruit Ninja - Jazz Edition")
clock = pygame.time.Clock()

# Wooden Tabletop Theme Colors
WOOD_DARK = (70, 42, 24)
WOOD_LIGHT = (95, 59, 34)
WOOD_PLANK = (82, 50, 28)
WOOD_LINE = (50, 30, 16)

PINK_POP = (255, 60, 150)
YELLOW_POP = (255, 200, 50)
CYAN_POP = (0, 200, 220)
PURPLE_POP = (100, 45, 140)
GREEN_POP = (50, 205, 50)
RED_POP = (255, 60, 60)
WHITE = (255, 255, 255)
BLACK = (15, 15, 20)
DARK_GRAY = (50, 50, 50)

# Fonts
font_huge = pygame.font.SysFont("Impact", 64)
font_title = pygame.font.SysFont("Impact", 36)
font_btn = pygame.font.SysFont("Arial", 24, bold=True)
font_ui = pygame.font.SysFont("Arial", 22, bold=True)

# Procedural Sound Generators
def create_beep_sound(frequency, duration, volume=0.3):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    buffer = array.array('h', [
        int(volume * 32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        for i in range(num_samples)
    ])
    return pygame.mixer.Sound(buffer=buffer)

def create_slide_sound(start_freq, end_freq, duration, volume=0.3):
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    buffer = array.array('h', [])
    for i in range(num_samples):
        progress = i / num_samples
        freq = start_freq + (end_freq - start_freq) * progress
        val = int(volume * 32767 * math.sin(2 * math.pi * freq * i / sample_rate))
        buffer.append(val)
    return pygame.mixer.Sound(buffer=buffer)

def create_heartbreak_sound():
    sample_rate = 22050
    duration = 0.35
    num_samples = int(sample_rate * duration)
    buffer = array.array('h', [])
    for i in range(num_samples):
        t = i / sample_rate
        freq = 300 - (t * 600)
        if freq < 60: freq = 60
        val = int(0.4 * 32767 * math.sin(2 * math.pi * freq * t))
        buffer.append(val)
    return pygame.mixer.Sound(buffer=buffer)

# Sound Effects
click_sound = create_beep_sound(800, 0.05, 0.2)
slice_sound = create_slide_sound(500, 900, 0.08, 0.25)
bomb_sound = create_slide_sound(180, 50, 0.3, 0.4)
heartbreak_sound = create_heartbreak_sound()

# Smooth Jazz Walking Bass Loop
def generate_jazz_bgm():
    sample_rate = 22050
    notes = [130.81, 196.00, 233.08, 196.00, 116.54, 174.61, 207.65, 174.61]
    note_duration = 0.3
    samples_per_note = int(sample_rate * note_duration)
    buffer = array.array('h', [])
    
    for note in notes:
        for i in range(samples_per_note):
            t = i / sample_rate
            env = math.sin(math.pi * (i / samples_per_note))
            val = int(0.2 * 32767 * env * (math.sin(2 * math.pi * note * t) + 0.3 * math.sin(2 * math.pi * (note*2) * t)))
            buffer.append(val)
    return pygame.mixer.Sound(buffer=buffer)

bgm_sound = generate_jazz_bgm()
bgm_channel = pygame.mixer.Channel(1)

# Game State & Settings
current_state = "WELCOME"
game_mode = "ENDLESS"
current_level = 1
music_enabled = True
sfx_enabled = True

# Fruit Types Setup
FRUIT_TYPES = {
    "watermelon": {"color": GREEN_POP, "radius": 40, "points": 10},
    "orange": {"color": YELLOW_POP, "radius": 30, "points": 15},
    "apple": {"color": RED_POP, "radius": 28, "points": 12},
    "bomb": {"color": DARK_GRAY, "radius": 25, "points": 0}
}

class GameObject:
    def __init__(self, is_level_mode=False, level=1):
        if is_level_mode and level == 1:
            self.type = "orange"
        else:
            self.type = random.choice(["watermelon", "orange", "apple", "bomb"] if random.random() < 0.2 else ["watermelon", "orange", "apple"])
        
        data = FRUIT_TYPES[self.type]
        self.color = data["color"]
        self.radius = data["radius"]
        self.points = data["points"]
        
        self.x = random.randint(120, WIDTH - 120)
        self.y = HEIGHT + 40
        self.dy = -random.uniform(13, 17)
        self.dx = random.uniform(-3, 3)
        self.gravity = 0.38
        self.sliced = False

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity

    def draw(self, surface):
        if not self.sliced:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            if self.type == "bomb":
                pygame.draw.circle(surface, YELLOW_POP, (int(self.x), int(self.y - self.radius)), 4)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(3, 7)
        self.dx = random.uniform(-6, 6)
        self.dy = random.uniform(-6, 6)
        self.lifetime = 25

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Button:
    def __init__(self, text, x, y, w, h, bg_color):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.bg_color = bg_color

    def draw(self, surface, active_pos):
        is_hovered = self.rect.collidepoint(active_pos)
        shadow_rect = self.rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(surface, BLACK, shadow_rect, border_radius=12)

        draw_color = YELLOW_POP if is_hovered else self.bg_color
        pygame.draw.rect(surface, draw_color, self.rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 3, border_radius=12)

        txt_surface = font_btn.render(self.text, True, BLACK if is_hovered else WHITE)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        surface.blit(txt_surface, txt_rect)

    def is_triggered(self, pos):
        return self.rect.collidepoint(pos)

# UI Buttons Setup
btn_endless = Button("ENDLESS MODE", WIDTH // 2 - 140, 240, 280, 55, PINK_POP)
btn_levels = Button("LEVEL SELECT", WIDTH // 2 - 140, 315, 280, 55, CYAN_POP)
btn_settings = Button("SETTINGS", WIDTH // 2 - 140, 390, 280, 55, PURPLE_POP)
btn_back = Button("BACK", 30, 20, 110, 40, PINK_POP)
btn_level_1 = Button("STAGE 1: ORANGES", 200, 220, 260, 60, YELLOW_POP)
btn_level_2 = Button("STAGE 2: MIXED", 485, 220, 260, 60, CYAN_POP)

btn_music_toggle = Button("", WIDTH // 2 - 140, 220, 280, 55, CYAN_POP)
btn_sfx_toggle = Button("", WIDTH // 2 - 140, 305, 280, 55, PINK_POP)

def reset_game():
    return 0, 3, [], [], []

score, lives, items, particles, blade_trail = reset_game()
spawn_timer = 0
game_over = False

running = True
input_pos = (0, 0)

while running:
    clock.tick(60)
    
    # Render Clean Wooden Plank Background
    screen.fill(WOOD_DARK)
    plank_width = 110
    for x_pos in range(0, WIDTH + plank_width, plank_width):
        pygame.draw.rect(screen, WOOD_PLANK, (x_pos, 0, plank_width - 4, HEIGHT))
        pygame.draw.line(screen, WOOD_LINE, (x_pos + plank_width - 4, 0), (x_pos + plank_width - 4, HEIGHT), 3)

    if music_enabled:
        if not bgm_channel.get_busy():
            bgm_channel.play(bgm_sound)
    else:
        bgm_channel.stop()

    mouse_pos = pygame.mouse.get_pos()
    input_pos = mouse_pos

    blade_trail.append(input_pos)
    if len(blade_trail) > 10:
        blade_trail.pop(0)

    action_triggered_pos = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action_triggered_pos = event.pos
            if sfx_enabled: click_sound.play()
        elif event.type == pygame.FINGERDOWN:
            touch_x = event.x * WIDTH
            touch_y = event.y * HEIGHT
            input_pos = (touch_x, touch_y)
            action_triggered_pos = input_pos
            if sfx_enabled: click_sound.play()
        elif event.type == pygame.FINGERMOTION:
            input_pos = (event.x * WIDTH, event.y * HEIGHT)

        if event.type == pygame.KEYDOWN and current_state == "WELCOME":
            if event.key == pygame.K_RETURN:
                current_state = "MENU"
                if sfx_enabled: click_sound.play()

    # Screen Logic
    if current_state == "WELCOME":
        title = font_huge.render("FRUIT NINJA", True, YELLOW_POP)
        sub = font_btn.render("Press [ ENTER ] or Tap to Start", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 3 + 100))
        if action_triggered_pos:
            current_state = "MENU"

    elif current_state == "MENU":
        title = font_huge.render("MAIN MENU", True, CYAN_POP)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        btn_endless.draw(screen, input_pos)
        btn_levels.draw(screen, input_pos)
        btn_settings.draw(screen, input_pos)

        if action_triggered_pos:
            if btn_endless.is_triggered(action_triggered_pos):
                game_mode = "ENDLESS"
                score, lives, items, particles, blade_trail = reset_game()
                game_over = False
                current_state = "GAMEPLAY"
            elif btn_levels.is_triggered(action_triggered_pos):
                current_state = "LEVEL_SELECT"
            elif btn_settings.is_triggered(action_triggered_pos):
                current_state = "SETTINGS"

    elif current_state == "LEVEL_SELECT":
        title = font_huge.render("SELECT LEVEL", True, YELLOW_POP)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        btn_back.draw(screen, input_pos)
        btn_level_1.draw(screen, input_pos)
        btn_level_2.draw(screen, input_pos)

        if action_triggered_pos:
            if btn_back.is_triggered(action_triggered_pos):
                current_state = "MENU"
            elif btn_level_1.is_triggered(action_triggered_pos):
                current_level = 1
                game_mode = "LEVELS"
                score, lives, items, particles, blade_trail = reset_game()
                game_over = False
                current_state = "GAMEPLAY"
            elif btn_level_2.is_triggered(action_triggered_pos):
                current_level = 2
                game_mode = "LEVELS"
                score, lives, items, particles, blade_trail = reset_game()
                game_over = False
                current_state = "GAMEPLAY"

    elif current_state == "SETTINGS":
        title = font_huge.render("SETTINGS", True, PURPLE_POP)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        btn_back.draw(screen, input_pos)

        btn_music_toggle.text = f"MUSIC: {'ON' if music_enabled else 'OFF'}"
        btn_sfx_toggle.text = f"SOUND FX: {'ON' if sfx_enabled else 'OFF'}"

        btn_music_toggle.draw(screen, input_pos)
        btn_sfx_toggle.draw(screen, input_pos)

        if action_triggered_pos:
            if btn_back.is_triggered(action_triggered_pos):
                current_state = "MENU"
            elif btn_music_toggle.is_triggered(action_triggered_pos):
                music_enabled = not music_enabled
            elif btn_sfx_toggle.is_triggered(action_triggered_pos):
                sfx_enabled = not sfx_enabled

    elif current_state == "GAMEPLAY":
        btn_back.draw(screen, input_pos)
        if action_triggered_pos and btn_back.is_triggered(action_triggered_pos):
            current_state = "MENU"

        if not game_over:
            spawn_timer += 1
            if spawn_timer > 45:
                items.append(GameObject(is_level_mode=(game_mode=="LEVELS"), level=current_level))
                spawn_timer = 0

            for particle in particles[:]:
                particle.update()
                particle.draw(screen)
                if particle.lifetime <= 0:
                    particles.remove(particle)

            for item in items[:]:
                item.update()
                item.draw(screen)

                if not item.sliced:
                    dist = math.hypot(input_pos[0] - item.x, input_pos[1] - item.y)
                    if dist < item.radius + 25 and len(blade_trail) > 1:
                        item.sliced = True
                        if item.type == "bomb":
                            if sfx_enabled: bomb_sound.play()
                            game_over = True
                        else:
                            if sfx_enabled: slice_sound.play()
                            score += item.points
                            for _ in range(12):
                                particles.append(Particle(item.x, item.y, item.color))
                        items.remove(item)

                if item.y > HEIGHT + 60:
                    if not item.sliced and item.type != "bomb":
                        lives -= 1
                        if sfx_enabled: heartbreak_sound.play()
                        if lives <= 0:
                            game_over = True
                    items.remove(item)

        score_text = font_ui.render(f"Score: {score}", True, WHITE)
        lives_text = font_ui.render(f"Lives: {'[X] ' * max(0, lives)}", True, RED_POP)
        screen.blit(score_text, (160, 25))
        screen.blit(lives_text, (WIDTH - 240, 25))

        if game_over:
            over_text = font_title.render("GAME OVER", True, RED_POP)
            restart_text = font_btn.render("Press 'R' to Restart or Back", True, WHITE)
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 3))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 3 + 60))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                score, lives, items, particles, blade_trail = reset_game()
                game_over = False

    if len(blade_trail) > 1:
        pygame.draw.lines(screen, CYAN_POP, False, blade_trail, 5)

    pygame.display.flip()

pygame.quit()
sys.exit()