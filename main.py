import pygame
import math
import os

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

# 載入圖片
brick_image = pygame.image.load(os.path.join("img", "chocolate.png"))
brick_image = pygame.transform.scale(brick_image, (BRICK_WIDTH - 6, BRICK_HEIGHT - 6))
brick_image.set_colorkey((0, 0, 0))  # 設定透明色
paddle_image = pygame.image.load(os.path.join("img", "wood.png"))
paddle_image = pygame.transform.scale(paddle_image, (PADDLE_WIDTH, PADDLE_HEIGHT))
background_img = pygame.image.load(os.path.join('img', 'background.jpg')).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
ball_img = pygame.image.load(os.path.join('img', 'ball.png')).convert()
ball_img = pygame.transform.scale(ball_img, (10 * 2, 10 * 2))
ball_img.set_colorkey(BLACK)

def show_message(text, color, size, center):
    font = pygame.font.SysFont(None, size)
    msg = font.render(text, True, color)
    rect = msg.get_rect(center=center)
    screen.blit(msg, rect)

def start_game():
    global score, all_sprites, balls, bricks, paddle
    Ball.speed = 5
    score = 0
    all_sprites = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    bricks = pygame.sprite.Group()
    all_sprites.empty()
    balls.empty()
    bricks.empty()
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

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = brick_image
        self.rect = self.image.get_rect()
        self.rect.center = x, y

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = paddle_image
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
    speed = 5
    def __init__(self, angle = math.pi / 4, center = (WIDTH//2, HEIGHT - 100)):
        super().__init__()
        radius = 10
        diameter = radius * 2
        self.image = ball_img
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.dx = Ball.speed * math.cos(angle)
        self.dy = -Ball.speed * math.sin(angle)
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
        elif self.rect.top >= HEIGHT:
            self.kill()

    def hit_brick(self, brick_rect, score):
        Ball.speed *= self.speed_factor
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
        if score % 5 == 0:
            self.create_new_ball()
    
    def create_new_ball(self):
        new_ball = Ball(math.pi * 3 / 4, (self.rect.centerx, self.rect.centery))
        balls.add(new_ball)
        all_sprites.add(new_ball)

    def hit_paddle(self, paddle_rect):
        max_angle = math.pi / 3
        offset = (self.rect.centerx - paddle_rect.centerx) / (paddle_rect.width / 2)
        angle = offset * max_angle
        self.dx = math.sin(angle) * Ball.speed
        self.dy = -math.cos(angle) * Ball.speed

clock = pygame.time.Clock()
start_game()

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
    hits = pygame.sprite.groupcollide(bricks, balls, True, False)
    for hit_brick, hit_balls in hits.items():
        score += 1
        hit_balls[0].hit_brick(hit_brick.rect, score)

    all_sprites.update()

    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    show_message(f"Score: {score}", WHITE, 32, (WIDTH//2, 25))

    # 遊戲結束判斷
    if not balls:
        show_message("You loss!", RED, 56, (WIDTH//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        start_game()

    elif not bricks:
        show_message("You win!", GREEN, 56, (WIDTH//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()

pygame.quit()
