import pygame
import math

# 初始化
pygame.init()
WIDTH, HEIGHT = 580, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("彈珠打方塊")

# 顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
BLUE = (80, 80, 255)
GREEN = (80, 255, 80)

# 遊戲參數
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = (WIDTH - 100) // BRICK_COLS
BRICK_HEIGHT = 30

def show_message(text, color):
    msg = font.render(text, True, color)
    rect = msg.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(msg, rect)
    pygame.display.flip()
    pygame.time.wait(2000)

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BRICK_WIDTH - 6, BRICK_HEIGHT - 6))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = x, y

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (WIDTH//2 - PADDLE_WIDTH//2, HEIGHT - 50)
        self.speed = 10

    def update(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.rect.left < 0:
                self.rect.left = 0
        if key[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        radius = 10
        diameter = radius * 2
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)  # 使用 SRCALPHA 支援透明背景
        pygame.draw.circle(self.image, WHITE, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH//2, HEIGHT - 100)
        self.dx = 4
        self.dy = -4
        self.speed_factor = 1.03

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        # 邊界反彈
        if self.rect.left < 0:
            self.rect.x = 0
            self.dx = -self.dx
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.dx = -self.dx
        if self.rect.top <= 0:
            self.rect.top = 0
            self.dy = -self.dy

    def hit_brick(self, brick_rect):
        self.dx *= self.speed_factor
        self.dy *= self.speed_factor
        if abs(self.rect.right - brick_rect.left) < 10 and self.dx > 0:
            self.rect.right = brick_rect.left
            self.dx = -self.dx
        elif abs(self.rect.left - brick_rect.right) < 10 and self.dx < 0:
            self.rect.left = brick_rect.right
            self.dx = -self.dx
        elif abs(self.rect.bottom - brick_rect.top) < 10 and self.dy > 0:
            self.rect.bottom = brick_rect.top
            self.dy = -self.dy
        elif abs(self.rect.top - brick_rect.bottom) < 10 and self.dy < 0:
            self.rect.top = brick_rect.bottom
            self.dy = -self.dy

    def hit_paddle(self, paddle_rect):
        speed = math.sqrt(self.dx ** 2 + self.dy ** 2)
        offset = (self.rect.centerx - paddle_rect.centerx) / (paddle_rect.width / 2)
        max_angle = math.pi / 3
        angle = offset * max_angle
        self.dx = math.sin(angle) * speed
        self.dy = -math.cos(angle) * speed

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

all_sprites = pygame.sprite.Group()
balls = pygame.sprite.Group()
bricks = pygame.sprite.Group()
paddle = Paddle()
all_sprites.add(paddle)
ball = Ball()
balls.add(ball)
all_sprites.add(ball)
for r in range(BRICK_ROWS):
    for c in range(BRICK_COLS):
        brick = Brick(50 + (c + 0.5) * BRICK_WIDTH, 50 + (r + 0.5) * BRICK_HEIGHT)
        bricks.add(brick)
all_sprites.add(bricks)

# 主迴圈
running = True
while running:
    clock.tick(60)
    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 碰板子
    hits = pygame.sprite.spritecollide(paddle, balls, False)
    for ball in hits:
        ball.hit_paddle(paddle.rect)

    # 碰磚塊
    hits = pygame.sprite.groupcollide(balls, bricks, False, True)
    for ball, hit_bricks in hits.items():
        for brick in hit_bricks:
            ball.hit_brick(brick.rect)

    # 遊戲結束判斷
    if ball.rect.bottom >= HEIGHT:
        show_message("You loss!", RED)
        running = False
    elif not bricks:
        show_message("You win!", GREEN)
        running = False

    all_sprites.update()

    screen.fill(BLACK)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
