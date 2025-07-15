import pygame as pg
import sys
import random
import math
import os
from enum import Enum

# Initialize pygame
pg.init()
pg.mixer.init()

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
BASE_SPEED = 5

# Colors
BLACK = (10, 10, 10)
WHITE = (240, 240, 240)
GRAY = (100, 100, 100)
RED = (230, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 120, 220)
YELLOW = (240, 220, 50)
CYAN = (50, 220, 220)
BUTTON_COLOR = (50, 180, 80)
ROAD_COLOR = (40, 40, 45)
SHOULDER_COLOR = (70, 70, 75)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Game states
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

# Enhanced particle system for effects
class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        return self.lifetime > 0
        
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color, alpha)
        temp_surf = pg.Surface((self.size * 2, self.size * 2), pg.SRCALPHA)
        pg.draw.circle(temp_surf, color, (self.size, self.size), self.size)
        screen.blit(temp_surf, (self.x - self.size, self.y - self.size))

# Enhanced particle system manager
class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_explosion(self, x, y, color, count=10):
        for _ in range(count):
            velocity = (random.randint(-3, 3), random.randint(-3, 3))
            lifetime = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, velocity, lifetime))
            
    def add_smoke(self, x, y, count=5):
        for _ in range(count):
            velocity = (random.randint(-1, 1), random.randint(-2, 0))
            lifetime = random.randint(30, 60)
            color = (random.randint(50, 100), random.randint(50, 100), random.randint(50, 100))
            self.particles.append(Particle(x, y, color, velocity, lifetime))
            
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

# Enhanced sound system
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        # Create sound effects programmatically if files don't exist
        try:
            # Engine sound (white noise)
            self.sounds['engine'] = pg.mixer.Sound(pg.mixer.get_init()[0] // 4)
            # Crash sound
            self.sounds['crash'] = pg.mixer.Sound(pg.mixer.get_init()[0] // 8)
            # Score sound
            self.sounds['score'] = pg.mixer.Sound(pg.mixer.get_init()[0] // 16)
        except:
            self.sounds = {}
            
    def play(self, sound_name, volume=0.5):
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()

# Music setup with better error handling
def load_music():
    music_folder = "music"
    try:
        if not os.path.exists(music_folder):
            os.makedirs(music_folder)
            print(f"Created '{music_folder}' folder. Please add your music files there.")
            return None
        
        music_files = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav', '.ogg'))]
        
        if not music_files:
            print(f"No music files found in '{music_folder}' folder.")
            return None
            
        selected_music = os.path.join(music_folder, random.choice(music_files))
        pg.mixer.music.load(selected_music)
        pg.mixer.music.set_volume(0.3)
        return selected_music
    except Exception as e:
        print(f"Error loading music: {e}")
        return None

# Enhanced car class with animations and better physics
class Car:
    def __init__(self, x, y, color, player=False):
        self.width = 45
        self.height = 80 if player else random.choice([75, 80, 85])
        self.x = x
        self.y = y
        self.speed = BASE_SPEED if player else random.randint(2, 4)
        self.original_speed = self.speed
        self.color = color
        self.player = player
        self.window_color = CYAN if player else WHITE
        self.type = "player" if player else random.choice(["sedan", "truck", "suv"])
        
        # Enhanced physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.3
        self.friction = 0.85
        self.max_speed = 8
        
        # Visual effects
        self.tilt = 0
        self.target_tilt = 0
        self.brake_lights = False
        self.headlights = True
        
        # Better road boundaries
        self.road_left = 175
        self.road_right = WIDTH - 225
        self.lane_width = (self.road_right - self.road_left) // 3
        
        # Animation frame for wheels
        self.wheel_rotation = 0
        
    def get_rect(self):
        return pg.Rect(self.x, self.y, self.width, self.height)
        
    def get_lane(self):
        center_x = self.x + self.width // 2
        relative_pos = center_x - self.road_left
        return max(0, min(2, int(relative_pos // self.lane_width)))
        
    def update_physics(self):
        # Apply friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Update tilt animation
        self.tilt += (self.target_tilt - self.tilt) * 0.1
        
        # Update wheel rotation
        self.wheel_rotation += abs(self.velocity_x) + abs(self.velocity_y)
        
    def draw(self, screen):
        # Calculate tilted position
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Create surface for the car
        car_surface = pg.Surface((self.width + 20, self.height + 20), pg.SRCALPHA)
        
        # Draw car body with enhanced details
        car_rect = pg.Rect(10, 10, self.width, self.height)
        
        # Main body
        pg.draw.rect(car_surface, self.color, car_rect, border_radius=5)
        
        # Highlight
        highlight_color = (min(self.color[0] + 30, 255), min(self.color[1] + 30, 255), min(self.color[2] + 30, 255))
        pg.draw.rect(car_surface, highlight_color, (car_rect.x + 2, car_rect.y + 2, car_rect.width - 4, 8), border_radius=3)
        
        # Windows based on car type
        if self.type == "sedan":
            pg.draw.rect(car_surface, self.window_color, (car_rect.x + 4, car_rect.y + 8, self.width - 8, 20), border_radius=2)
            pg.draw.rect(car_surface, self.window_color, (car_rect.x + 4, car_rect.y + 32, self.width - 8, 20), border_radius=2)
        elif self.type == "truck":
            pg.draw.rect(car_surface, self.window_color, (car_rect.x + 8, car_rect.y + 8, 25, 18), border_radius=2)
        else:  # SUV
            pg.draw.rect(car_surface, self.window_color, (car_rect.x + 4, car_rect.y + 8, self.width - 8, 35), border_radius=2)
            
        # Enhanced wheels with rotation
        wheel_color = (20, 20, 20)
        rim_color = (80, 80, 80)
        wheel_positions = [(4, 5), (self.width - 16, 5), (4, self.height - 17), (self.width - 16, self.height - 17)]
        
        for i, wheel_pos in enumerate(wheel_positions):
            wheel_x = car_rect.x + wheel_pos[0]
            wheel_y = car_rect.y + wheel_pos[1]
            
            # Wheel shadow
            pg.draw.ellipse(car_surface, (0, 0, 0, 100), (wheel_x + 1, wheel_y + 1, 12, 12))
            # Wheel
            pg.draw.ellipse(car_surface, wheel_color, (wheel_x, wheel_y, 12, 12))
            pg.draw.ellipse(car_surface, rim_color, (wheel_x + 2, wheel_y + 2, 8, 8))
            
            # Animated spokes
            spoke_angle = self.wheel_rotation + i * 90
            spoke_x = wheel_x + 6 + math.cos(math.radians(spoke_angle)) * 2
            spoke_y = wheel_y + 6 + math.sin(math.radians(spoke_angle)) * 2
            pg.draw.circle(car_surface, WHITE, (int(spoke_x), int(spoke_y)), 1)
        
        # Headlights
        if self.headlights:
            pg.draw.ellipse(car_surface, YELLOW, (car_rect.x + 3, car_rect.y + 2, 8, 6))
            pg.draw.ellipse(car_surface, YELLOW, (car_rect.x + self.width - 11, car_rect.y + 2, 8, 6))
        
        # Brake lights
        if self.brake_lights:
            pg.draw.ellipse(car_surface, RED, (car_rect.x + 3, car_rect.y + self.height - 8, 8, 6))
            pg.draw.ellipse(car_surface, RED, (car_rect.x + self.width - 11, car_rect.y + self.height - 8, 8, 6))
        
        # Rotate surface if tilted
        if abs(self.tilt) > 0.1:
            rotated_surface = pg.transform.rotate(car_surface, self.tilt)
            rotated_rect = rotated_surface.get_rect(center=(center_x, center_y))
            screen.blit(rotated_surface, rotated_rect)
        else:
            screen.blit(car_surface, (self.x - 10, self.y - 10))
        
    def move(self, direction=None, obstacles=None, player_car=None):
        if self.player:
            if direction == "left":
                self.velocity_x = max(-self.max_speed, self.velocity_x - self.acceleration)
                self.target_tilt = -5
                new_x = max(self.road_left, self.x + self.velocity_x)
                if new_x != self.x:
                    self.x = new_x
            elif direction == "right":
                self.velocity_x = min(self.max_speed, self.velocity_x + self.acceleration)
                self.target_tilt = 5
                new_x = min(self.road_right - self.width, self.x + self.velocity_x)
                if new_x != self.x:
                    self.x = new_x
            else:
                self.target_tilt = 0
                
            self.update_physics()
        else:
            # Enhanced AI for enemy cars
            original_y = self.y
            
            # Simple lane changing logic
            if random.random() < 0.001:  # 0.1% chance per frame
                current_lane = self.get_lane()
                if current_lane > 0 and random.random() < 0.5:
                    self.velocity_x = -1
                elif current_lane < 2 and random.random() < 0.5:
                    self.velocity_x = 1
                    
            # Keep in bounds
            self.x = max(self.road_left, min(self.road_right - self.width, self.x + self.velocity_x))
            
            new_y = self.y + self.speed
            temp_rect = pg.Rect(self.x, new_y, self.width, self.height)
            can_move = True
            
            # Collision avoidance
            if obstacles:
                for other_car in obstacles:
                    if other_car != self:
                        other_rect = other_car.get_rect()
                        if temp_rect.colliderect(other_rect):
                            safe_distance = self.height + 20
                            if new_y + self.height > other_car.y:
                                self.y = max(original_y, other_car.y - safe_distance)
                                self.speed = max(1, min(self.speed, other_car.speed - 0.5))
                                self.brake_lights = True
                                can_move = False
                            break
            
            if player_car and can_move:
                player_rect = player_car.get_rect()
                if temp_rect.colliderect(player_rect):
                    can_move = False
                    self.brake_lights = True
            
            if can_move:
                self.y = new_y
                self.brake_lights = False
                if self.speed < self.original_speed:
                    self.speed = min(self.original_speed, self.speed + 0.1)
                    
            self.update_physics()
            return self.y > HEIGHT + 50

# Enhanced Road class with better visuals
class Road:
    def __init__(self):
        self.road_width = 450
        self.road_x = (WIDTH - self.road_width) // 2
        self.stripes = []
        self.scenery_objects = []
        
        # Initialize road stripes
        for i in range(15):
            self.stripes.append({
                'y': i * 80 - 200,
                'width': 50,
                'height': 30,
                'speed': BASE_SPEED + 1
            })
            
        # Add scenery objects
        self.generate_scenery()
        
    def generate_scenery(self):
        # Trees and buildings on the sides
        for i in range(20):
            side = random.choice(['left', 'right'])
            x = random.randint(10, 150) if side == 'left' else random.randint(WIDTH - 150, WIDTH - 10)
            y = i * 100 - 500
            obj_type = random.choice(['tree', 'building', 'sign'])
            self.scenery_objects.append({
                'x': x,
                'y': y,
                'type': obj_type,
                'color': random.choice([GREEN, GRAY, YELLOW, ORANGE])
            })
            
    def draw(self, screen):
        # Draw gradient shoulders
        for i in range(self.road_x):
            shade = 70 + int(15 * (i / self.road_x))
            pg.draw.line(screen, (shade, shade, shade + 5), (i, 0), (i, HEIGHT))
            
        for i in range(self.road_x, WIDTH):
            shade = 70 + int(15 * ((WIDTH - i) / (WIDTH - self.road_x)))
            pg.draw.line(screen, (shade, shade, shade + 5), (i, 0), (i, HEIGHT))
        
        # Road surface with texture
        pg.draw.rect(screen, ROAD_COLOR, (self.road_x, 0, self.road_width, HEIGHT))
        
        # Add road texture
        for i in range(0, HEIGHT, 20):
            noise_color = (ROAD_COLOR[0] + random.randint(-5, 5), 
                          ROAD_COLOR[1] + random.randint(-5, 5), 
                          ROAD_COLOR[2] + random.randint(-5, 5))
            pg.draw.line(screen, noise_color, (self.road_x, i), (self.road_x + self.road_width, i))
        
        # Draw scenery
        for obj in self.scenery_objects:
            if obj['y'] > -50 and obj['y'] < HEIGHT + 50:
                if obj['type'] == 'tree':
                    pg.draw.circle(screen, obj['color'], (int(obj['x']), int(obj['y'])), 15)
                    pg.draw.rect(screen, (101, 67, 33), (obj['x'] - 3, obj['y'], 6, 20))
                elif obj['type'] == 'building':
                    pg.draw.rect(screen, obj['color'], (obj['x'] - 20, obj['y'] - 30, 40, 50))
                    # Windows
                    for row in range(3):
                        for col in range(2):
                            pg.draw.rect(screen, YELLOW, (obj['x'] - 15 + col * 15, obj['y'] - 25 + row * 15, 8, 8))
                elif obj['type'] == 'sign':
                    pg.draw.rect(screen, obj['color'], (obj['x'] - 15, obj['y'] - 10, 30, 20))
                    pg.draw.rect(screen, BLACK, (obj['x'] - 2, obj['y'], 4, 15))
        
        # Enhanced lane dividers
        lane_width = self.road_width // 3
        for lane in range(1, 3):
            lane_x = self.road_x + lane * lane_width
            for stripe in self.stripes:
                if stripe['y'] > -50 and stripe['y'] < HEIGHT:
                    # Main stripe
                    pg.draw.rect(screen, WHITE, (lane_x - 25, stripe['y'], 50, stripe['height']))
                    # Glow effect
                    pg.draw.rect(screen, (255, 255, 255, 100), (lane_x - 27, stripe['y'] - 2, 54, stripe['height'] + 4))
        
        # Road edges with reflectors
        pg.draw.line(screen, WHITE, (self.road_x, 0), (self.road_x, HEIGHT), 4)
        pg.draw.line(screen, WHITE, (self.road_x + self.road_width, 0), (self.road_x + self.road_width, HEIGHT), 4)
        
        # Reflectors
        for i in range(0, HEIGHT, 40):
            pg.draw.circle(screen, YELLOW, (self.road_x - 5, i), 3)
            pg.draw.circle(screen, YELLOW, (self.road_x + self.road_width + 5, i), 3)
            
    def update(self):
        # Update road stripes
        for stripe in self.stripes:
            stripe['y'] += stripe['speed']
            if stripe['y'] > HEIGHT:
                stripe['y'] = -stripe['height'] - 50
                
        # Update scenery
        for obj in self.scenery_objects:
            obj['y'] += BASE_SPEED
            if obj['y'] > HEIGHT + 100:
                obj['y'] = -100
                obj['x'] = random.randint(10, 150) if obj['x'] < WIDTH // 2 else random.randint(WIDTH - 150, WIDTH - 10)

# Enhanced Game class with state management
class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Ultimate Street Racer")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 42)
        self.small_font = pg.font.Font(None, 28)
        self.large_font = pg.font.Font(None, 64)
        
        # Game state
        self.state = GameState.MENU
        self.player = Car(WIDTH // 2 - 22, HEIGHT - 120, BLUE, True)
        self.obstacles = []
        self.road = Road()
        self.particle_system = ParticleSystem()
        self.sound_manager = SoundManager()
        
        # Game variables
        self.score = 0
        self.level = 1
        self.lives = 3
        self.power_ups = []
        self.last_obstacle_time = 0
        self.obstacle_frequency = 2000
        self.min_obstacle_distance = 120
        self.speed_boost = 1.0
        self.speed_boost_timer = 0
        
        # UI elements
        self.play_button = Button(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60, "START RACE")
        self.pause_button = Button(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60, "RESUME")
        self.restart_button = Button(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 60, "RESTART")
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_timer = 0
        self.show_fps = False
        
        # Load and play music
        self.current_music = load_music()
        if self.current_music:
            pg.mixer.music.play(-1)
            
    def can_spawn_obstacle(self, new_x, new_y):
        new_rect = pg.Rect(new_x, new_y, 45, 80)
        
        for obstacle in self.obstacles:
            obstacle_rect = obstacle.get_rect()
            if abs(new_y - obstacle.y) < self.min_obstacle_distance:
                new_lane = self.get_lane_from_x(new_x)
                obstacle_lane = obstacle.get_lane()
                if abs(new_lane - obstacle_lane) <= 1:
                    return False
                    
            if new_rect.colliderect(obstacle_rect):
                return False
        
        return True
    
    def get_lane_from_x(self, x):
        road_left = 175
        road_right = WIDTH - 225
        lane_width = (road_right - road_left) // 3
        center_x = x + 22
        relative_pos = center_x - road_left
        return max(0, min(2, int(relative_pos // lane_width)))
    
    def get_safe_spawn_position(self):
        road_left = 175
        road_right = WIDTH - 225
        lane_width = (road_right - road_left) // 3
        
        lanes = [0, 1, 2]
        random.shuffle(lanes)
        
        for lane in lanes:
            lane_center = road_left + lane * lane_width + lane_width // 2
            spawn_x = lane_center - 22
            spawn_y = -100
            
            if self.can_spawn_obstacle(spawn_x, spawn_y):
                return spawn_x, spawn_y
        
        return None, None
    
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.current_music:
                    pg.mixer.music.stop()
                pg.quit()
                sys.exit()
                
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                elif event.key == pg.K_r and self.state == GameState.GAME_OVER:
                    self.reset_game()
                elif event.key == pg.K_F1:
                    self.show_fps = not self.show_fps
                    
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == GameState.MENU and self.play_button.is_clicked(event.pos):
                    self.state = GameState.PLAYING
                elif self.state == GameState.PAUSED and self.pause_button.is_clicked(event.pos):
                    self.state = GameState.PLAYING
                elif self.state == GameState.GAME_OVER and self.restart_button.is_clicked(event.pos):
                    self.reset_game()
    
    def update(self):
        if self.state != GameState.PLAYING:
            return
            
        # Update speed boost
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer == 0:
                self.speed_boost = 1.0
                
        # Handle player input
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.player.move("left")
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.player.move("right")
        
        # Spawn obstacles
        current_time = pg.time.get_ticks()
        if current_time - self.last_obstacle_time > self.obstacle_frequency:
            spawn_x, spawn_y = self.get_safe_spawn_position()
            
            if spawn_x is not None:
                colors = [(220, 60, 60), (60, 180, 60), (220, 140, 60), (180, 60, 180), (60, 60, 220)]
                color = random.choice(colors)
                
                new_obstacle = Car(spawn_x, spawn_y, color)
                new_obstacle.speed = random.randint(2, 5) * self.speed_boost
                new_obstacle.original_speed = new_obstacle.speed
                self.obstacles.append(new_obstacle)
                self.last_obstacle_time = current_time
                
                # Increase difficulty
                if self.score > 0 and self.score % 10 == 0:
                    self.obstacle_frequency = max(600, self.obstacle_frequency - 100)
                    self.level = (self.score // 10) + 1
                    self.min_obstacle_distance = max(80, self.min_obstacle_distance - 10)
                    if self.score % 50 == 0:
                        self.speed_boost = min(2.0, self.speed_boost + 0.2)
                        self.speed_boost_timer = 300  # 5 seconds at 60 FPS
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            if obstacle.move(obstacles=self.obstacles, player_car=self.player):
                self.obstacles.remove(obstacle)
                self.score += 1
                
                # Add score particles
                self.particle_system.add_explosion(
                    obstacle.x + obstacle.width // 2,
                    HEIGHT + 20,
                    GREEN,
                    5
                )
                
            # Enhanced collision detection
            player_rect = self.player.get_rect()
            obstacle_rect = obstacle.get_rect()
            
            buffer = 5
            collision_rect = pg.Rect(
                player_rect.x + buffer,
                player_rect.y + buffer,
                player_rect.width - 2 * buffer,
                player_rect.height - 2 * buffer
            )
            
            if collision_rect.colliderect(obstacle_rect):
                # Add crash effects
                self.particle_system.add_explosion(
                    player_rect.centerx,
                    player_rect.centery,
                    RED,
                    15
                )
                self.particle_system.add_smoke(
                    player_rect.centerx,
                    player_rect.centery,
                    10
                )
                
                self.sound_manager.play('crash', 0.7)
                
                self.lives -= 1
                if self.lives <= 0:
                    self.state = GameState.GAME_OVER
                    if self.current_music:
                        pg.mixer.music.fadeout(2000)
                else:
                    # Remove the obstacle and give brief invincibility
                    self.obstacles.remove(obstacle)
                    # Reset player position
                    self.player.x = WIDTH // 2 - 22
                    self.player.velocity_x = 0
                    break
        
        # Update systems
        self.road.update()
        self.particle_system.update()
        
        # Update FPS counter
        self.fps_timer += 1
        if self.fps_timer >= 60:
            self.fps_counter = int(self.clock.get_fps())
            self.fps_timer = 0
    
    def draw(self):
        # Enhanced background gradient
        for y in range(HEIGHT):
            night_factor = 0.8 + 0.2 * math.sin(y * 0.01)
            shade = int(15 * night_factor)
            color = (shade, shade, int(shade * 1.2))
            pg.draw.line(self.screen, color, (0, y), (WIDTH, y))
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        
        # Draw FPS counter if enabled
        if self.show_fps:
            fps_text = self.small_font.render(f"FPS: {self.fps_counter}", True, WHITE)
            self.screen.blit(fps_text, (10, HEIGHT - 30))
            
        pg.display.flip()
    
    def draw_menu(self):
        # Animated title
        title_y = 100 + math.sin(pg.time.get_ticks() * 0.003) * 5
        title = self.large_font.render("ULTIMATE STREET RACER", True, (255, 215, 0))
        shadow = self.large_font.render("ULTIMATE STREET RACER", True, (100, 80, 0))
        self.screen.blit(shadow, (WIDTH//2 - title.get_width()//2 + 3, title_y + 3))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, title_y))
        
        # Subtitle
        subtitle = self.font.render("Enhanced Edition", True, CYAN)
        self.screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, title_y + 80))
        
        # Instructions with icons
        instructions = [
            "🏎️ Use ARROW KEYS or WASD to steer",
            "🚗 Avoid other vehicles on the road",
            "💨 Speed boosts every 50 points",
            "❤️ You have 3 lives",
            "⏸️ Press ESC to pause",
            f"🏆 High Score: {self.get_high_score()}"
        ]
        
        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, 220 + i*35))
        
        # Animated road preview
        preview_y = 350
        pg.draw.rect(self.screen, ROAD_COLOR, (WIDTH//2 - 100, preview_y, 200, 100))
        
        # Moving stripes
        stripe_offset = (pg.time.get_ticks() // 50) % 60
        for i in range(4):
            stripe_y = preview_y + i * 30 - stripe_offset
            if stripe_y > preview_y - 30 and stripe_y < preview_y + 130:
                pg.draw.rect(self.screen, WHITE, (WIDTH//2 - 15, stripe_y, 30, 20))
        
        # Mini car
        mini_car_x = WIDTH//2 - 15 + math.sin(pg.time.get_ticks() * 0.005) * 20
        pg.draw.rect(self.screen, BLUE, (mini_car_x, preview_y + 60, 30, 20))
        
        self.play_button.draw(self.screen, self.font)
        
        # Version info
        version_text = self.small_font.render("v2.0 - Enhanced Edition", True, GRAY)
        self.screen.blit(version_text, (10, HEIGHT - 25))
    
    def draw_game(self):
        self.road.draw(self.screen)
        
        # Draw all cars
        all_cars = [self.player] + self.obstacles
        for car in all_cars:
            car.draw(self.screen)
        
        # Draw particle effects
        self.particle_system.draw(self.screen)
        
        # Enhanced HUD
        hud_bg = pg.Surface((300, 140), pg.SRCALPHA)
        hud_bg.fill((0, 0, 0, 180))
        pg.draw.rect(hud_bg, (255, 255, 255, 50), (0, 0, 300, 140), 2, border_radius=10)
        self.screen.blit(hud_bg, (10, 10))
        
        # HUD content
        hud_texts = [
            f"Score: {self.score}",
            f"Level: {self.level}",
            f"Lives: {'❤️' * self.lives}",
            f"Cars: {len(self.obstacles)}"
        ]
        
        for i, text in enumerate(hud_texts):
            rendered = self.small_font.render(text, True, WHITE)
            self.screen.blit(rendered, (20, 20 + i*30))
        
        # Speed boost indicator
        if self.speed_boost > 1.0:
            boost_text = self.small_font.render(f"SPEED BOOST! {self.speed_boost:.1f}x", True, YELLOW)
            boost_bg = pg.Surface((boost_text.get_width() + 20, 30), pg.SRCALPHA)
            boost_bg.fill((255, 255, 0, 100))
            self.screen.blit(boost_bg, (WIDTH//2 - boost_text.get_width()//2 - 10, 50))
            self.screen.blit(boost_text, (WIDTH//2 - boost_text.get_width()//2, 55))
        
        # Level up notification
        if self.score > 0 and self.score % 10 == 0 and pg.time.get_ticks() % 1000 < 500:
            level_text = self.font.render(f"LEVEL {self.level}!", True, GREEN)
            self.screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 - 50))
    
    def draw_pause_overlay(self):
        # Semi-transparent overlay
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Pause box
        box = pg.Surface((400, 300), pg.SRCALPHA)
        box.fill((0, 0, 0, 200))
        pg.draw.rect(box, (255, 255, 255, 100), (0, 0, 400, 300), 3, border_radius=15)
        self.screen.blit(box, (WIDTH//2 - 200, HEIGHT//2 - 150))
        
        # Pause text
        pause_title = self.large_font.render("PAUSED", True, YELLOW)
        self.screen.blit(pause_title, (WIDTH//2 - pause_title.get_width()//2, HEIGHT//2 - 100))
        
        # Instructions
        instructions = [
            "Press ESC to resume",
            "Press R to restart",
            "Click RESUME button"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 20 + i*30))
        
        self.pause_button.draw(self.screen, self.font)
    
    def draw_game_over(self):
        # Dark overlay with pulsing effect
        alpha = 180 + int(20 * math.sin(pg.time.get_ticks() * 0.01))
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))
        
        # Game over box
        box = pg.Surface((500, 400), pg.SRCALPHA)
        box.fill((20, 20, 20, 220))
        pg.draw.rect(box, (255, 50, 50, 150), (0, 0, 500, 400), 4, border_radius=20)
        self.screen.blit(box, (WIDTH//2 - 250, HEIGHT//2 - 200))
        
        # Game over text with glow effect
        game_over_text = self.large_font.render("GAME OVER", True, RED)
        glow_text = self.large_font.render("GAME OVER", True, (255, 100, 100))
        
        # Draw glow
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            self.screen.blit(glow_text, (WIDTH//2 - game_over_text.get_width()//2 + offset[0], 
                                       HEIGHT//2 - 150 + offset[1]))
        
        self.screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 150))
        
        # Stats
        stats = [
            f"Final Score: {self.score}",
            f"Level Reached: {self.level}",
            f"High Score: {self.get_high_score()}"
        ]
        
        for i, stat in enumerate(stats):
            text_color = YELLOW if "High Score" in stat else WHITE
            text = self.font.render(stat, True, text_color)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 80 + i*40))
        
        # Performance rating
        if self.score >= 100:
            rating = "LEGENDARY!"
            rating_color = (255, 215, 0)
        elif self.score >= 50:
            rating = "EXPERT!"
            rating_color = (255, 165, 0)
        elif self.score >= 25:
            rating = "SKILLED!"
            rating_color = GREEN
        else:
            rating = "ROOKIE"
            rating_color = WHITE
            
        rating_text = self.font.render(rating, True, rating_color)
        self.screen.blit(rating_text, (WIDTH//2 - rating_text.get_width()//2, HEIGHT//2 + 40))
        
        # Controls
        controls = [
            "Press R to restart",
            "or click RESTART button"
        ]
        
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, WHITE)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 100 + i*25))
        
        self.restart_button.draw(self.screen, self.font)
    
    def get_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        try:
            high_score = max(self.score, self.get_high_score())
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))
        except:
            pass
    
    def reset_game(self):
        self.save_high_score()
        
        # Reset game state
        self.state = GameState.PLAYING
        self.player = Car(WIDTH // 2 - 22, HEIGHT - 120, BLUE, True)
        self.obstacles = []
        self.particle_system = ParticleSystem()
        self.road = Road()
        
        # Reset game variables
        self.score = 0
        self.level = 1
        self.lives = 3
        self.last_obstacle_time = pg.time.get_ticks()
        self.obstacle_frequency = 2000
        self.min_obstacle_distance = 120
        self.speed_boost = 1.0
        self.speed_boost_timer = 0
        
        # Restart music
        if self.current_music:
            pg.mixer.music.play(-1)
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# Enhanced Button class with animations
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = (50, 180, 80)
        self.hover_color = (80, 220, 120)
        self.click_color = (30, 140, 60)
        self.shadow = pg.Surface((width, height), pg.SRCALPHA)
        self.shadow.fill((0, 0, 0, 80))
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.is_pressed = False
        
    def draw(self, screen, font):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        
        # Update hover state
        if self.rect.collidepoint(mouse_pos):
            self.target_scale = 1.05
            color = self.click_color if mouse_pressed else self.hover_color
            self.is_pressed = mouse_pressed
        else:
            self.target_scale = 1.0
            color = self.color
            self.is_pressed = False
        
        # Smooth scaling animation
        self.hover_scale += (self.target_scale - self.hover_scale) * 0.2
        
        # Calculate scaled dimensions
        scaled_width = int(self.rect.width * self.hover_scale)
        scaled_height = int(self.rect.height * self.hover_scale)
        scaled_rect = pg.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        
        # Draw shadow
        shadow_rect = pg.Rect(scaled_rect.x + 3, scaled_rect.y + 3, scaled_width, scaled_height)
        shadow_surface = pg.transform.scale(self.shadow, (scaled_width, scaled_height))
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw button with gradient effect
        button_surface = pg.Surface((scaled_width, scaled_height), pg.SRCALPHA)
        
        # Gradient background
        for i in range(scaled_height):
            gradient_color = (
                min(255, color[0] + int(20 * (i / scaled_height))),
                min(255, color[1] + int(20 * (i / scaled_height))),
                min(255, color[2] + int(20 * (i / scaled_height)))
            )
            pg.draw.line(button_surface, gradient_color, (0, i), (scaled_width, i))
        
        # Border
        pg.draw.rect(button_surface, (255, 255, 255, 120), (0, 0, scaled_width, scaled_height), 3, border_radius=10)
        
        screen.blit(button_surface, scaled_rect)
        
        # Button text with shadow
        text_surface = font.render(self.text, True, WHITE)
        text_shadow = font.render(self.text, True, (0, 0, 0, 150))
        
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        shadow_rect = pg.Rect(text_rect.x + 2, text_rect.y + 2, text_rect.width, text_rect.height)
        
        screen.blit(text_shadow, shadow_rect)
        screen.blit(text_surface, text_rect)
        
        # Glow effect when hovered
        if self.target_scale > 1.0:
            glow_surface = pg.Surface((scaled_width + 20, scaled_height + 20), pg.SRCALPHA)
            glow_rect = pg.Rect(0, 0, scaled_width + 20, scaled_height + 20)
            pg.draw.rect(glow_surface, (*color, 30), glow_rect, border_radius=15)
            screen.blit(glow_surface, (scaled_rect.x - 10, scaled_rect.y - 10))
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Run the game
if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        pg.quit()
        sys.exit()