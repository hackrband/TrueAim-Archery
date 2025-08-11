import math
import random
import time
import pygame

pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer with Bow and Arrow")

# Game constants
TARGET_INCREMENT = 400
TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 30
BG_COLOR = (0, 25, 40)
LIVES = 3
TOP_BAR_HEIGHT = 50
ARROW_SPEED = 20
LABEL_FONT = pygame.font.SysFont("comicsans", 24)

# Class for the target
class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2
    COLOR = "red"
    SECOND_COLOR = "white"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True

    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False
        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        dis = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return dis <= self.size

# Class for the arrows
class Arrow:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = ARROW_SPEED
        self.hit = False

    def update(self):
        if not self.hit:
            self.x += math.cos(self.angle) * self.speed
            self.y -= math.sin(self.angle) * self.speed

    def draw(self, win):
        if not self.hit:
            end_x = self.x - 20 * math.cos(self.angle)
            end_y = self.y + 20 * math.sin(self.angle)
            pygame.draw.line(win, "white", (self.x, self.y), (end_x, end_y), 3)

def draw(win, targets, arrows):
    win.fill(BG_COLOR)
    for target in targets:
        target.draw(win)
    for arrow in arrows:
        arrow.draw(win)

def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}.{milli}"

def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")
    win.blit(time_label, (5, 5))
    win.blit(speed_label, (200, 5))
    win.blit(hits_label, (450, 5))
    win.blit(lives_label, (650, 5))

def end_screen(win, elapsed_time, targets_pressed, clicks):
    win.fill(BG_COLOR)
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "white")
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")
    accuracy = round((targets_pressed / clicks) * 100, 1) if clicks > 0 else 0
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")
    win.blit(time_label, (get_middle(time_label), 100))
    win.blit(speed_label, (get_middle(speed_label), 200))
    win.blit(hits_label, (get_middle(hits_label), 300))
    win.blit(accuracy_label, (get_middle(accuracy_label), 400))
    pygame.display.update()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                run = False

def get_middle(surface):
    return WIDTH / 2 - surface.get_width() / 2

# Function to draw bow
def draw_bow(win, player_x, player_y, angle):
    bow_length = 40
    bow_end_x = player_x + bow_length * math.cos(angle)
    bow_end_y = player_y - bow_length * math.sin(angle)
    pygame.draw.line(win, "brown", (player_x, player_y), (bow_end_x, bow_end_y), 6)

def main():
    run = True
    targets = []
    arrows = []
    clock = pygame.time.Clock()
    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()
    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    player_x, player_y = WIDTH // 2, HEIGHT - 50

    while run:
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return
            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                targets.append(Target(x, y))
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1
                angle = math.atan2(player_y - mouse_pos[1], mouse_pos[0] - player_x)
                arrows.append(Arrow(player_x, player_y, angle))

        for target in targets:
            target.update()
            if target.size <= 0:
                targets.remove(target)
                misses += 1
            for arrow in arrows:
                if target.collide(arrow.x, arrow.y):
                    targets.remove(target)
                    targets_pressed += 1
                    arrow.hit = True

        for arrow in arrows[:]:
            arrow.update()
            if arrow.x < 0 or arrow.x > WIDTH or arrow.y < 0 or arrow.y > HEIGHT or arrow.hit:
                arrows.remove(arrow)

        if misses >= LIVES:
            end_screen(WIN, elapsed_time, targets_pressed, clicks)
            return

        draw(WIN, targets, arrows)
        angle = math.atan2(player_y - mouse_pos[1], mouse_pos[0] - player_x)
        draw_bow(WIN, player_x, player_y, angle)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
