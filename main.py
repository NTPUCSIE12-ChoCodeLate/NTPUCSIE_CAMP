import pygame
import random

# 初始化 Pygame
pygame.init()

# 遊戲參數
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRID_SIZE = 100
ROAD_COUNT = SCREEN_HEIGHT // GRID_SIZE - 1  # 道路數量（避開底部植物選單區域）
TITLE_ICON_SIZE = (64, 64)
BULLET_SIZE = (30, 30)
GOBLIN_SIZE = (90, 100)
REFRESH_SIZE = (60, 60)
TITLE = "ChocoLate"

# 顏色
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

icon_img = pygame.image.load("image/icon.png")
icon_img = pygame.transform.scale(icon_img, TITLE_ICON_SIZE)

bullet_img = pygame.image.load("image/bullet.png")
bullet_img = pygame.transform.scale(bullet_img, BULLET_SIZE)

goblin_img = pygame.image.load("image/goblin.png")
goblin_img = pygame.transform.scale(goblin_img, GOBLIN_SIZE)
goblin_img.set_colorkey(WHITE)

refresh_img = pygame.image.load("image/refresh.png")
refresh_img = pygame.transform.scale(refresh_img, REFRESH_SIZE)

# 創建遊戲窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
pygame.display.set_icon(icon_img)

# 字體
font = pygame.font.SysFont(None, 36)

# 遊戲物件類別
class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y, plant_type):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.plant_type = plant_type
        if plant_type == "normal":
            self.image.fill(GREEN)
            self.health = 100
        elif plant_type == "sunflower":
            self.image.fill(YELLOW)
            self.health = 80

    def draw_health(self, screen):
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, GRID_SIZE, 5))
        pygame.draw.rect(
            screen, GREEN, (self.rect.x, self.rect.y - 10, GRID_SIZE * (self.health / 100), 5)
        )

    def update(self):
        if self.health <= 0:
            self.kill()


class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, zombie_type):
        super().__init__()
        self.image = goblin_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.zombie_type = zombie_type
        if zombie_type == "normal":
            # self.image.fill(RED)
            self.speed = 1
            self.health = 50
        elif zombie_type == "fast":
            # self.image.fill(BLUE)
            self.speed = 2
            self.health = 30
        elif zombie_type == "explosive":
            # self.image.fill(BLACK)
            self.speed = 1.2
            self.health = 100

    def update(self):
        self.rect.x -= self.speed
        if self.health <= 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        # self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH:
            self.kill()

#遊戲結束畫面
def game_over():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(150)
    screen.blit(overlay, (0, 0))
    game_over_font = pygame.font.SysFont(None, 80)
    game_over_text = game_over_font.render(f"Game Over", True, RED)
    text_x = (SCREEN_WIDTH - game_over_text.get_width()) / 2
    text_y = SCREEN_HEIGHT / 2 - 100
    screen.blit(game_over_text, (text_x, text_y))

# 遊戲組件
plants = pygame.sprite.Group()
zombies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# 設定時鐘
clock = pygame.time.Clock()

# 遊戲變數
score = 0
zombies_escaped = 0
is_game_over = False
spawn_timer = 0
zombie_spawn_speed = 180  # 初始生成速度

# 選擇植物
selected_plant = "normal"
plant_menu = {"normal": GREEN, "sunflower": YELLOW}

#儲存植物放置位置
plant_position = []
one_line = []
for i in range(7):
    one_line.append(False)
for i in range(5):
    plant_position.append(one_line.copy())
for i in range(5):
    for j in range(7):
        print(plant_position[i][j], end = " ")
    print()

# 遊戲循環
running = True
while running:
    screen.fill(GRAY)

    # 繪製道路
    for row in range(0, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE):
        pygame.draw.rect(screen, BLACK, (0, row, SCREEN_WIDTH, GRID_SIZE), 1)

    # 繪製植物選單
    pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - GRID_SIZE, SCREEN_WIDTH, GRID_SIZE))
    x_offset = 10
    for plant_type, color in plant_menu.items():
        pygame.draw.rect(screen, color, (x_offset, SCREEN_HEIGHT - GRID_SIZE + 10, GRID_SIZE, GRID_SIZE - 20))
        if selected_plant == plant_type:
            pygame.draw.rect(screen, WHITE, (x_offset - 2, SCREEN_HEIGHT - GRID_SIZE + 8, GRID_SIZE + 4, GRID_SIZE - 16), 2)
        x_offset += GRID_SIZE + 10

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if y > SCREEN_HEIGHT - GRID_SIZE:  # 點擊選單區域
                x_offset = 10
                for plant_type in plant_menu.keys():
                    if x_offset <= x <= x_offset + GRID_SIZE:
                        selected_plant = plant_type
                    x_offset += GRID_SIZE + 10
            else:  # 點擊放置植物
                x_position = x // GRID_SIZE
                y_position = y // GRID_SIZE
                if score >= 5 and x_position < 7 and plant_position[y_position][x_position] == False:
                    plant = Plant(x_position * GRID_SIZE, y_position * GRID_SIZE, selected_plant)
                    plants.add(plant)
                    score -= 5
                    plant_position[y_position][x_position] = True
                    print(x_position, y_position)
                    for i in range(5):
                        for j in range(7):
                            print(plant_position[i][j], end = " ")
                        print()

    # 更新分數
    if not is_game_over:
        score += 1 / FPS

    # 生產殭屍
    spawn_timer += 1
    if spawn_timer > zombie_spawn_speed:
        spawn_timer = 0
        zombie_lane = random.randint(0, ROAD_COUNT - 1) * GRID_SIZE
        zombie_type = random.choices(["normal", "fast", "explosive"], weights=[50, 30, 20])[0]
        zombie = Zombie(SCREEN_WIDTH, zombie_lane, zombie_type)
        zombies.add(zombie)

    # 更新植物發射子彈或產生積分
    for plant in plants:
        if plant.plant_type == "normal" and random.random() < 0.02:
            bullet = Bullet(plant.rect.right, plant.rect.centery)
            bullets.add(bullet)
        elif plant.plant_type == "sunflower" and random.random() < 0.01:
            score += 0.5

    # 更新物件
    plants.update()
    zombies.update()
    bullets.update()

    # 碰撞檢測
    for bullet in bullets:
        collided_zombies = pygame.sprite.spritecollide(bullet, zombies, False)
        for zombie in collided_zombies:
            zombie.health -= 25
            bullet.kill()

    for zombie in zombies:
        collided_plants = pygame.sprite.spritecollide(zombie, plants, False)
        for plant in collided_plants:
            if zombie.zombie_type == "explosive":
                plant.health -= 50
                zombie.kill()
            else:
                plant.health -= 0.5

        # 檢測殭屍是否走出屏幕
        if zombie.rect.right < 0:
            zombie.kill()
            if zombies_escaped < 5:
                zombies_escaped += 1
                if zombies_escaped == 5:
                    is_game_over = True

    # 繪製物件
    plants.draw(screen)
    zombies.draw(screen)
    bullets.draw(screen)

    # 繪製血量
    for plant in plants:
        plant.draw_health(screen)
    for zombie in zombies:
        pygame.draw.rect(screen, RED, (zombie.rect.x, zombie.rect.y - 10, GRID_SIZE, 5))
        pygame.draw.rect(screen, GREEN, (zombie.rect.x, zombie.rect.y - 10, GRID_SIZE * (zombie.health / 50), 5))

    # 顯示積分
    score_text = font.render(f"Score: {int(score)}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

    # 顯示殭屍逃脫數
    escape_text = font.render(f"Zombies Escaped: {zombies_escaped}/5", True, WHITE)
    screen.blit(escape_text, (10, 10))

    # 顯示遊戲結束
    if is_game_over:
        game_over()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
