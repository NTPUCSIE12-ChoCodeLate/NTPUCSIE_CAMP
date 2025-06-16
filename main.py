import pygame
import math
import random
import os

FPS = 60
# 大小設定
WIDTH, HEIGHT = 800, 700
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_MARGIN  = 70
BRICK_SPACING = 8
BRICK_WIDTH = (WIDTH - BRICK_MARGIN * 2) // BRICK_COLS - BRICK_SPACING
BRICK_HEIGHT = 45
BOARD_SIZE = (150, 30)
BALL_RADIUS = 15
GAME_OVER_LEN = 400
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 60
# 顏色設定
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# 遊戲初始化
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("打磚塊遊戲")
clock = pygame.time.Clock()

# 載入圖片
# 背景圖片
background_img = pygame.image.load(os.path.join('img', 'background.jpg')).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
# 磚塊圖片
brick_img = pygame.image.load(os.path.join('img', 'chocolate.png')).convert()
brick_img = pygame.transform.scale(brick_img, (BRICK_WIDTH, BRICK_HEIGHT))
brick_img.set_colorkey(BLACK)
# 板子圖片
board_img = pygame.image.load(os.path.join('img', 'wood.png')).convert()
board_img = pygame.transform.scale(board_img, BOARD_SIZE)
board_img.set_colorkey(BLACK)
# 球圖片
ball_img = pygame.image.load(os.path.join('img', 'ball.png')).convert()
ball_img = pygame.transform.scale(ball_img, (BALL_RADIUS * 2, BALL_RADIUS * 2))
ball_img.set_colorkey(BLACK)
# 視窗圖示
icon_img = pygame.image.load(os.path.join('img', 'icon.jpg')).convert()
pygame.display.set_icon(icon_img)
# 遊戲結束視窗
game_over_img = pygame.image.load(os.path.join('img', 'game_over.png')).convert()
game_over_img = pygame.transform.scale(game_over_img, (GAME_OVER_LEN, GAME_OVER_LEN))
game_over_img.set_colorkey(BLACK)

# 載入音效
hit_sound = pygame.mixer.Sound(os.path.join('sound', 'hit.mp3'))

font_path = 'font.ttf'

def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_path, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)

# 半透明黑色遮罩
black_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
black_surface.fill((0, 0, 0, 128))
# 再玩一次按鈕
again_button = pygame.Surface((BUTTON_WIDTH, BUTTON_HEIGHT))
again_button.fill(WHITE)
draw_text(again_button, "再玩一次", 32, BUTTON_WIDTH // 2, BUTTON_HEIGHT // 2, BLACK)
button_rect = again_button.get_rect()
button_rect.center = (WIDTH // 2, HEIGHT // 2 + 130)

def show_game_over():
    screen.blit(background_img, (0, 0))
    draw_text(screen, f"分數: {score}", 32, WIDTH // 2, 35)
    all_sprites.draw(screen)
    screen.blit(black_surface, (0, 0))
    screen.blit(game_over_img, (WIDTH // 2 - GAME_OVER_LEN // 2, HEIGHT // 2 - GAME_OVER_LEN // 2))
    draw_text(screen, "遊戲結束", 48, WIDTH // 2, HEIGHT // 2 - 130)
    draw_text(screen, "本次分數", 32, WIDTH // 2 - 90, HEIGHT // 2 - 25)
    draw_text(screen, str(score), 32, WIDTH // 2 - 90, HEIGHT // 2 + 25)
    draw_text(screen, "最高分數", 32, WIDTH // 2 + 90, HEIGHT // 2 - 25)
    draw_text(screen, str(max_score), 32, WIDTH // 2 + 90, HEIGHT // 2 + 25)
    screen.blit(again_button, button_rect)
    pygame.display.update()

def start_game():
    global all_sprites, board, balls, bricks, score, game_over
    
    score = 0
    game_over = False
    Ball.speed = 7

    # 初始宣告遊戲物件
    all_sprites = pygame.sprite.Group()
    # 板子
    board = Board((WIDTH // 2, HEIGHT - 60))
    all_sprites.add(board)
    # 球
    balls = pygame.sprite.Group()
    ball = Ball(math.pi / 4, (WIDTH // 2, HEIGHT - 150))
    balls.add(ball)
    all_sprites.add(ball)
    # 磚塊
    bricks = pygame.sprite.Group()
    for r in range(BRICK_ROWS):
        for c in range(BRICK_COLS):
            x = BRICK_MARGIN + c * (BRICK_WIDTH + BRICK_SPACING) + BRICK_SPACING / 2
            y = BRICK_MARGIN + r * (BRICK_HEIGHT + BRICK_SPACING)
            brick = Brick(x, y)
            bricks.add(brick)
    all_sprites.add(bricks)

# 磚塊類別
class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = brick_img
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y

# 板子類別
class Board(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = board_img
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = 15
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.rect.left < 0:
                self.rect.left = 0
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH

# 球類別
class Ball(pygame.sprite.Sprite):
    speed = 7
    def __init__(self, angle, center):
        super().__init__()
        self.image = ball_img
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.dx = Ball.speed * math.sin(angle)
        self.dy = -Ball.speed * math.cos(angle)
        self.speed_factor = 1.03

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        # 邊界反彈
        if self.rect.left < 0:
            self.rect.left = 0
            self.dx = -self.dx
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.dx = -self.dx
        if self.rect.top <= 0:
            self.rect.top = 0
            self.dy = -self.dy
        elif self.rect.top >= HEIGHT:
            self.kill()

    def hit_board(self, board_rect):
        # 計算角度
        max_angle = math.pi / 3
        offset = (self.rect.centerx - board_rect.centerx) / (board_rect.width / 2)
        angle = max_angle * offset
        # 計算 dx, dy
        self.dx = Ball.speed * math.sin(angle)
        self.dy = -Ball.speed * math.cos(angle)
    
    def hit_brick(self, brick_rect):
        hit_sound.play()
        # 加速
        self.dx *= self.speed_factor
        self.dy *= self.speed_factor
        Ball.speed *= self.speed_factor
        # 計算四個方向的重疊量
        overlap_left = abs(self.rect.right - brick_rect.left)
        overlap_right = abs(self.rect.left - brick_rect.right)
        overlap_top = abs(self.rect.bottom - brick_rect.top)
        overlap_bottom = abs(self.rect.top - brick_rect.bottom)
        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
        # 判斷反彈方向
        if min_overlap == overlap_left and self.dx > 0:
            self.dx = -self.dx
        elif min_overlap == overlap_right and self.dx < 0:
            self.dx = -self.dx
        else:
            self.dy = -self.dy
        # 隨機產生新球
        if random.random() < 0.1:
            self.create_new_ball()
    
    def create_new_ball(self):
        new_ball = Ball(-math.pi / 4, self.rect.center)
        balls.add(new_ball)
        all_sprites.add(new_ball)

start_game()
max_score = 0

# 主迴圈
running = True
while running:
    clock.tick(FPS)
    # 輸入處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if game_over:
        show_game_over()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                start_game()
        continue
    
    # 更新遊戲
    all_sprites.update()

    if len(balls) == 0:
        max_score = max(max_score, score)
        game_over = True

    # 球碰板子
    hits = pygame.sprite.spritecollide(board, balls, False)
    for ball in hits:
        ball.hit_board(board.rect)
    # 球碰磚塊
    hits = pygame.sprite.groupcollide(bricks, balls, True, False)
    for brick, hit_balls in hits.items():
        hit_balls[0].hit_brick(brick.rect)
        score += 1
    
    # 畫面顯示
    screen.blit(background_img, (0, 0))
    draw_text(screen, f"分數: {score}", 32, WIDTH // 2, 35)
    all_sprites.draw(screen)
    pygame.display.update()

pygame.quit()