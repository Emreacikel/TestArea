import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Endless Runner"

# Player constants
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 60
PLAYER_START_X = 200
PLAYER_START_Y = 100
PLAYER_JUMP_SPEED = 15
PLAYER_MOVE_SPEED = 5
GRAVITY = 0.8

# Obstacle constants
OBSTACLE_WIDTH = 30
OBSTACLE_SPEED = 5
MIN_OBSTACLE_SPACING = 300
TALL_OBSTACLE_HEIGHT = 80
SHORT_OBSTACLE_HEIGHT = 31
HEAD_OBSTACLE_HEIGHT = 31  # Height for the head-height obstacle

# Colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
SKY_BLUE = (135, 206, 235)

# Add to the top with other constants
RAINDROP_COUNT = 100
SUNNY_PARTICLE_COUNT = 50

class Obstacle:
    def __init__(self, x, obstacle_type):
        # obstacle_type can be: "tall", "short", or "head"
        if obstacle_type == "tall":
            self.height = TALL_OBSTACLE_HEIGHT
            self.y = SCREEN_HEIGHT - 60 - self.height  # On ground
        elif obstacle_type == "short":
            self.height = SHORT_OBSTACLE_HEIGHT
            self.y = SCREEN_HEIGHT - 160  # Flying obstacle
        else:  # head height
            self.height = SCREEN_HEIGHT - 100  # Screen height minus 100
            self.y = 0  # Start from top of screen
            
        self.width = OBSTACLE_WIDTH
        self.passed = False
        self.type = obstacle_type  # Store the obstacle type
        self.rect = pygame.Rect(x, self.y, self.width, self.height)

class EndlessRunner:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_over = False
        self.game_started = False
        self.score = 0
        self.void_position = 0
        
        # Keep track of past scores
        if not hasattr(self, 'past_scores'):
            self.past_scores = []
        
        # Player properties
        self.player_rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.player_velocity_y = 0
        self.player_velocity_x = 0
        self.is_jumping = False
        
        # Ground
        self.ground_rect = pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60)
        
        # Obstacles
        self.obstacles = []
        self.spawn_initial_obstacles()
        
        # Add weather particles
        self.raindrops = []
        self.sun_particles = []
        self.init_weather()
        
        # Add ghosts list (maximum 2 ghosts)
        self.ghosts = [
            {'x': 0, 'y': SCREEN_HEIGHT // 3, 'speed': 1},
            {'x': 0, 'y': 2 * SCREEN_HEIGHT // 3, 'speed': 1}
        ]

    def spawn_initial_obstacles(self):
        # Start with 3 obstacles
        x = SCREEN_WIDTH + 200  # Start beyond the screen
        for _ in range(3):
            obstacle_type = random.choice(["tall", "short", "head"])
            self.obstacles.append(Obstacle(x, obstacle_type))
            x += MIN_OBSTACLE_SPACING

    def spawn_new_obstacle(self):
        # Spawn a new obstacle if the last one is far enough
        if not self.obstacles or self.obstacles[-1].rect.x < SCREEN_WIDTH - MIN_OBSTACLE_SPACING:
            obstacle_type = random.choice(["tall", "short", "head"])  # Now includes head height
            x = SCREEN_WIDTH + 100
            self.obstacles.append(Obstacle(x, obstacle_type))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.game_started = True
                    elif self.game_over:
                        # Save current score before resetting
                        self.past_scores.append(self.score)
                        # Reset game state
                        self.__init__()
                        self.game_started = True
                elif event.key == pygame.K_UP and not self.is_jumping:
                    self.player_velocity_y = -PLAYER_JUMP_SPEED
                    self.is_jumping = True
                elif event.key == pygame.K_DOWN:
                    self.player_rect.height = 30
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.player_rect.height = PLAYER_HEIGHT
        
        keys = pygame.key.get_pressed()
        self.player_velocity_x = 0
        if keys[pygame.K_LEFT]:
            self.player_velocity_x = -PLAYER_MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            self.player_velocity_x = PLAYER_MOVE_SPEED
        
        return True

    def init_weather(self):
        # Initialize raindrops
        self.raindrops = []
        for _ in range(RAINDROP_COUNT):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.randint(5, 15)
            self.raindrops.append({'x': x, 'y': y, 'speed': speed})
            
        # Initialize sunny particles
        self.sun_particles = []
        for _ in range(SUNNY_PARTICLE_COUNT):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 4)
            self.sun_particles.append({'x': x, 'y': y, 'size': size})

    def update_weather(self):
        # Determine weather based on score ranges (changes every 25 points)
        is_rainy = (self.score // 25) % 2 == 1  # Rainy when score is 25-49, 75-99, etc.
        
        if is_rainy:
            # Update rain
            for drop in self.raindrops:
                drop['y'] += drop['speed']
                drop['x'] -= drop['speed'] // 2  # Diagonal rain
                if drop['y'] > SCREEN_HEIGHT:
                    drop['y'] = 0
                    drop['x'] = random.randint(0, SCREEN_WIDTH)
        else:
            # Update sunny particles
            for particle in self.sun_particles:
                particle['x'] += random.randint(-1, 1)
                particle['y'] += random.randint(-1, 1)
                
                # Keep particles within screen bounds
                particle['x'] = max(0, min(SCREEN_WIDTH, particle['x']))
                particle['y'] = max(0, min(SCREEN_HEIGHT, particle['y']))

    def draw_weather(self):
        # Determine weather based on score ranges
        is_rainy = (self.score // 25) % 2 == 1  # Rainy when score is 25-49, 75-99, etc.
        
        if is_rainy:
            # Draw rain
            for drop in self.raindrops:
                pygame.draw.line(self.screen, (150, 150, 255), 
                               (drop['x'], drop['y']), 
                               (drop['x'] + 5, drop['y'] + 5), 2)
        else:
            # Draw sunny particles
            for particle in self.sun_particles:
                pygame.draw.circle(self.screen, (255, 255, 100), 
                                 (int(particle['x']), int(particle['y'])), 
                                 particle['size'])
            
            # Draw sun in top right corner
            sun_x = SCREEN_WIDTH - 60
            sun_y = 60
            # Draw sun circle
            pygame.draw.circle(self.screen, (255, 255, 0), (sun_x, sun_y), 30)
            # Draw sun rays
            for i in range(8):  # 8 rays
                angle = i * (360 / 8)  # Evenly space rays
                rad_angle = angle * math.pi / 180  # Convert to radians
                start_x = sun_x + 25 * math.cos(rad_angle)
                start_y = sun_y + 25 * math.sin(rad_angle)
                end_x = sun_x + 40 * math.cos(rad_angle)
                end_y = sun_y + 40 * math.sin(rad_angle)
                pygame.draw.line(self.screen, (255, 255, 0), 
                               (int(start_x), int(start_y)), 
                               (int(end_x), int(end_y)), 3)

    def update(self):
        if self.game_over or not self.game_started:
            return
            
        # Update weather
        self.update_weather()
        
        # Update ghosts during rainy weather
        is_rainy = (self.score // 25) % 2 == 1
        if is_rainy:
            for ghost in self.ghosts:
                # Move ghost toward player
                dx = self.player_rect.centerx - ghost['x']
                dy = self.player_rect.centery - ghost['y']
                
                # Calculate distance
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance > 0:
                    # Normalize and apply speed
                    ghost['x'] += (dx / distance) * ghost['speed']
                    ghost['y'] += (dy / distance) * ghost['speed']
                
                # Check for collision with ghost
                ghost_rect = pygame.Rect(ghost['x'] - 15, ghost['y'] - 15, 30, 30)
                if ghost_rect.colliderect(self.player_rect):
                    self.game_over = True
        
        # Apply gravity
        self.player_velocity_y += GRAVITY
        self.player_rect.y += self.player_velocity_y
        
        # Apply horizontal movement
        self.player_rect.x += self.player_velocity_x
        
        # Check if player has moved near the right edge
        if self.player_rect.x > SCREEN_WIDTH * 0.7:  # When player reaches 70% of screen width
            # Move everything left to create illusion of continuous movement
            offset = PLAYER_MOVE_SPEED * 2
            
            # Move player back
            self.player_rect.x -= offset
            
            # Move obstacles left
            for obstacle in self.obstacles:
                obstacle.rect.x -= offset
            
            # Move void left
            self.void_position -= offset
        
        # Keep player within left bound only
        if self.player_rect.left < 0:
            self.player_rect.left = 0
        
        # Ground collision
        if self.player_rect.bottom > self.ground_rect.top:
            self.player_rect.bottom = self.ground_rect.top
            self.player_velocity_y = 0
            self.is_jumping = False
            
        # Move the void
        self.void_position += 1
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.rect.x -= OBSTACLE_SPEED
            # Check if player has passed the obstacle
            if not obstacle.passed and obstacle.rect.right < self.player_rect.left:
                obstacle.passed = True
                # Award points based on obstacle type
                if obstacle.type == "tall":
                    self.score += 2  # 2 points for tall obstacles
                elif obstacle.type == "short":
                    self.score += 1  # 1 point for short obstacles
                else:  # head height
                    self.score += 2  # 2 points for head-height obstacles
            # Remove obstacles that are off screen
            if obstacle.rect.right < 0:
                self.obstacles.remove(obstacle)
        
        # Spawn new obstacles
        self.spawn_new_obstacle()
        
        # Check collision with obstacles
        for obstacle in self.obstacles:
            if self.player_rect.colliderect(obstacle.rect):
                self.game_over = True
                break
        
        # Check for game over (void catches up)
        if self.void_position + 50 > self.player_rect.left:
            self.game_over = True

    def draw(self):
        # Clear screen with weather-appropriate background
        is_rainy = (self.score // 25) % 2 == 1
        if is_rainy:
            self.screen.fill((100, 100, 150))  # Darker sky for rain
        else:
            self.screen.fill((135, 206, 235))  # Bright sky blue
            
        # Draw weather effects
        self.draw_weather()
        
        # Draw ghosts during rainy weather
        if is_rainy:
            for ghost in self.ghosts:
                # Draw ghost body (white semi-transparent circle)
                ghost_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(ghost_surface, (255, 255, 255, 180), (15, 15), 15)
                self.screen.blit(ghost_surface, (ghost['x'] - 15, ghost['y'] - 15))
                
                # Draw ghost eyes (black dots)
                pygame.draw.circle(self.screen, BLACK, (int(ghost['x'] - 5), int(ghost['y'] - 5)), 3)
                pygame.draw.circle(self.screen, BLACK, (int(ghost['x'] + 5), int(ghost['y'] - 5)), 3)
        
        # Draw the area covered by void (everything left of the void position)
        pygame.draw.rect(self.screen, RED, (0, 0, self.void_position, SCREEN_HEIGHT))
        
        # Draw the void's right edge
        pygame.draw.rect(self.screen, RED, (self.void_position - 50, 0, 100, SCREEN_HEIGHT))
        
        # Draw obstacles with different colors based on type and position
        for obstacle in self.obstacles:
            # If obstacle is in the void area, make it red
            if obstacle.rect.right < self.void_position:
                color = RED
            else:
                if obstacle.type == "tall":
                    color = (255, 255, 0)  # Yellow
                elif obstacle.type == "short":
                    color = PURPLE  # Purple
                else:  # head height
                    color = GREEN
            pygame.draw.rect(self.screen, color, obstacle.rect)
        
        # Draw player
        pygame.draw.rect(self.screen, BLUE, self.player_rect)
        
        # Draw ground
        pygame.draw.rect(self.screen, GREEN, self.ground_rect)
        
        # Draw current score in top left
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Current Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Draw past scores in top right
        if self.past_scores:
            past_scores_font = pygame.font.Font(None, 36)
            last_three_scores = self.past_scores[-3:]  # Get only the last 3 scores
            past_scores_text = past_scores_font.render(f"Last Attempts: {', '.join(map(str, last_three_scores))}", True, BLACK)
            past_scores_rect = past_scores_text.get_rect()
            past_scores_rect.topright = (SCREEN_WIDTH - 10, 10)  # Position in top right with 10px padding
            self.screen.blit(past_scores_text, past_scores_rect)
        
        # Draw start message if game hasn't started
        if not self.game_started:
            start_font = pygame.font.Font(None, 48)
            start_text = start_font.render("Press SPACE to start", True, BLACK)
            text_rect = start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(start_text, text_rect)
        
        # Draw game over message if game is over
        if self.game_over:
            game_over_font = pygame.font.Font(None, 72)
            if self.score > 25:
                game_over_text = game_over_font.render("You Win!", True, GREEN)
            else:
                game_over_text = game_over_font.render("You Lose!", True, BLACK)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(game_over_text, text_rect)
            
            # Draw final score
            final_score_font = pygame.font.Font(None, 48)
            final_score_text = final_score_font.render(f"Final Score: {self.score}", True, BLACK)
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60))
            self.screen.blit(final_score_text, score_rect)
            
            # Draw restart message
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press SPACE to restart", True, BLACK)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 120))
            self.screen.blit(restart_text, restart_rect)
        
        # Update display
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

def main():
    game = EndlessRunner()
    game.run()

if __name__ == "__main__":
    main()
