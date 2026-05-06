import pygame
import sys
import random

def generate_maze(width, height):
    # 1. 建立全是牆壁的初始地圖 (1 為牆)
    maze = [[1 for _ in range(width)] for _ in range(height)]
    
    def walk(x, y):
        maze[y][x] = 0  # 將當前位置挖通
        
        # 定義四個方向：上、下、左、右 (每次移動兩格)
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)  # 隨機打亂方向，確保迷宮每次都長得不一樣
        
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            # 檢查新位置是否在範圍內，且是否尚未被挖過
            if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
                # 挖通當前格與新位置之間的那面牆
                maze[y + dy // 2][x + dx // 2] = 0
                walk(nx, ny)

    # 2. 從座標 (1, 1) 開始挖掘
    walk(1, 1)
    
    # 3. 隨機放置終點 (2) 在一個是路 (0) 的地方
    maze[height - 2][width - 2] = 2 
    return maze

# 1. 基礎設定
pygame.init()
TILE_SIZE = 40
# 設定迷宮尺寸（必須是奇數，演算法才能正確運作）
MAZE_W, MAZE_H = 21, 15 
maze = generate_maze(MAZE_W, MAZE_H)

WIDTH, HEIGHT = MAZE_W * TILE_SIZE, MAZE_H * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("迷宮遊戲")

# 顏色
WALL_COLOR = (50, 50, 50)
PATH_COLOR = (200, 200, 200)
PLAYER_COLOR = (255, 100, 100)
EXIT_COLOR = (50, 205, 50) # 鮮綠色作為終點

# 字體設定 (用於顯示勝利文字)
font = pygame.font.SysFont("Arial", 48, bold=True)

player_x, player_y = 1, 1 
game_over = False # 新增一個狀態來記錄遊戲是否結束

# 主迴圈
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 只有在遊戲還沒結束時，才允許移動
        if not game_over and event.type == pygame.KEYDOWN:
            new_x, new_y = player_x, player_y
            if event.key == pygame.K_LEFT:  new_x -= 1
            if event.key == pygame.K_RIGHT: new_x += 1
            if event.key == pygame.K_UP:    new_y -= 1
            if event.key == pygame.K_DOWN:  new_y += 1
            
            # 碰撞偵測：只要不是牆壁 (1) 就可以走
            if maze[new_y][new_x] != 1:
                player_x, player_y = new_x, new_y
            
            # --- 勝利偵測 ---
            if maze[player_y][player_x] == 2:
                game_over = True

    # 畫面繪製
    screen.fill(PATH_COLOR)

    for row_idx, row in enumerate(maze):
        for col_idx, tile in enumerate(row):
            pos_rect = (col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if tile == 1:
                pygame.draw.rect(screen, WALL_COLOR, pos_rect)
            elif tile == 2:
                pygame.draw.rect(screen, EXIT_COLOR, pos_rect)

    # 畫玩家
    pygame.draw.circle(screen, PLAYER_COLOR, 
                       (player_x * TILE_SIZE + TILE_SIZE // 2, 
                        player_y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 3)

    # 如果勝利，顯示文字
    if game_over:
        text_surface = font.render("YOU WIN!", True, (0, 0, 0))
        # 讓文字出現在螢幕中央
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()