import pygame
import sys
import random
import time
import heapq
from collections import deque

# ==========================================
# 1. 視線與光線追蹤 (Line of Sight)
# ==========================================
def get_line(x1, y1, x2, y2):
    points = []
    N = max(abs(x2 - x1), abs(y2 - y1))
    for step in range(N + 1):
        t = step / N if N > 0 else 0.0
        nx = round(x1 + t * (x2 - x1))
        ny = round(y1 + t * (y2 - y1))
        points.append((nx, ny))
    return points

def get_fov(px, py, maze, radius=3):
    visible = set()
    height, width = len(maze), len(maze[0])
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx*dx + dy*dy <= radius*radius:
                tx, ty = px + dx, py + dy
                if 0 <= tx < width and 0 <= ty < height:
                    line = get_line(px, py, tx, ty)
                    for lx, ly in line:
                        visible.add((lx, ly))
                        if maze[ly][lx] == 1: break 
    return visible

# ==========================================
# 2. 演算法
# ==========================================
def solve_bfs(maze, start, end):
    start_time = time.perf_counter()
    height, width = len(maze), len(maze[0])
    queue = deque([start])
    visited = set([start])
    parent = {}
    visited_order = []
    
    while queue:
        curr = queue.popleft()
        visited_order.append(curr)
        if curr == end: break
        
        x, y = curr
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if maze[ny][nx] != 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = curr
                    queue.append((nx, ny))
                    
    time_taken = (time.perf_counter() - start_time) * 1000
    path = []
    if end in parent:
        curr = end
        while curr != start:
            path.append(curr)
            curr = parent[curr]
        path.reverse()
    return visited_order, path, time_taken

def heuristic(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def solve_astar(maze, start, end):
    start_time = time.perf_counter()
    height, width = len(maze), len(maze[0])
    open_set = []
    heapq.heappush(open_set, (heuristic(start, end), 0, start))
    visited = set()
    g_score = {start: 0}
    parent = {}
    visited_order = []
    
    while open_set:
        _, curr_g, curr = heapq.heappop(open_set)
        if curr in visited: continue
        visited.add(curr)
        visited_order.append(curr)
        if curr == end: break
        
        x, y = curr
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if maze[ny][nx] != 1:
                    tentative_g = curr_g + 1
                    if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                        g_score[(nx, ny)] = tentative_g
                        f_score = tentative_g + heuristic((nx, ny), end)
                        parent[(nx, ny)] = curr
                        heapq.heappush(open_set, (f_score, tentative_g, (nx, ny)))
                        
    time_taken = (time.perf_counter() - start_time) * 1000
    path = []
    if end in parent:
        curr = end
        while curr != start:
            path.append(curr)
            curr = parent[curr]
        path.reverse()
    return visited_order, path, time_taken

def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    def walk(x, y):
        maze[y][x] = 0
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                walk(nx, ny)
    walk(1, 1)
    maze[height - 2][width - 2] = 2 
    # === 新增：隨機打通 10% 的牆壁，創造捷徑與空曠區 ===
    # 這會打破「完美迷宮」的限制，讓 A* 發揮實力
    walls_to_break = (width * height) // 10
    for _ in range(walls_to_break):
        rx = random.randint(1, width - 2)
        ry = random.randint(1, height - 2)
        if maze[ry][rx] == 1:
            maze[ry][rx] = 0 # 把牆壁變成路
    return maze

# ==========================================
# 3. Pygame 視窗與動態縮放設定
# ==========================================
pygame.init()

FIXED_WIDTH = 800
FIXED_HEIGHT = 600
MAZE_W, MAZE_H = 55, 57 

TILE_SIZE = min(FIXED_WIDTH // MAZE_W, FIXED_HEIGHT // MAZE_H)
OFFSET_X = (FIXED_WIDTH - (MAZE_W * TILE_SIZE)) // 2
OFFSET_Y = (FIXED_HEIGHT - (MAZE_H * TILE_SIZE)) // 2

maze = generate_maze(MAZE_W, MAZE_H)

WIDTH, HEIGHT = FIXED_WIDTH, FIXED_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("演算法專題：一鍵自動通關展示")

# 顏色定義
WALL_COLOR, PATH_COLOR = (45, 52, 54), (223, 230, 233)
PLAYER_COLOR, EXIT_COLOR = (214, 48, 49), (0, 184, 148)
DARK_WALL, DARK_PATH, DARK_EXIT = (15, 18, 18), (70, 75, 75), (0, 60, 40)
BFS_COLOR = (250, 177, 160)
ASTAR_COLOR = (85, 239, 196)
FINAL_PATH_COLOR = (253, 203, 110)
BG_COLOR = (30, 30, 30)

try:
    font_title = pygame.font.Font("msjh.ttf", 24)
    font_text = pygame.font.Font("msjh.ttf", 16)
except FileNotFoundError:
    font_title = pygame.font.SysFont("microsoftjhenghei", 24, bold=True)
    font_text = pygame.font.SysFont("microsoftjhenghei", 16, bold=False)

player_x, player_y = 1, 1 
explored_tiles = set()
visible_tiles = get_fov(player_x, player_y, maze, radius=3)
explored_tiles.update(visible_tiles)

# 新增狀態：AUTO_PILOT (自動駕駛)
game_state = "PLAYING"
anim_index = 0
bfs_order, bfs_path, bfs_time = [], [], 0
astar_order, astar_path, astar_time = [], [], 0

# 自動駕駛相關變數
auto_path = []
auto_index = 0

start_ticks = pygame.time.get_ticks()
time_limit = 60 

clock = pygame.time.Clock()
running = True

while running:
    # --- 時間更新 (遊玩中 或 自動駕駛中 都會扣時間) ---
    if game_state == "PLAYING" or game_state == "AUTO_PILOT":
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        time_left = max(0, time_limit - seconds_passed)
        if time_left == 0:
            game_state = "TIME_OUT"

    # --- 自動駕駛邏輯 ---
    if game_state == "AUTO_PILOT":
        if auto_index < len(auto_path):
            # 每幀移動一步，速度超快！(如果想變慢，可以用計時器限制)
            player_x, player_y = auto_path[auto_index]
            visible_tiles = get_fov(player_x, player_y, maze, radius=3)
            explored_tiles.update(visible_tiles) 
            auto_index += 1
            # 故意加入微小延遲讓移動有肉眼可見的動畫感，而不是瞬間移動
            pygame.time.delay(30) 
        else:
            # 走到終點了，觸發結算邏輯
            bfs_order, bfs_path, bfs_time = solve_bfs(maze, (1, 1), (player_x, player_y))
            astar_order, astar_path, astar_time = solve_astar(maze, (1, 1), (player_x, player_y))
            game_state = "ANIM_BFS"
            anim_index = 0

    # --- 事件處理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # 狀態：遊玩中
            if game_state == "PLAYING":
                # 方向鍵手動移動
                new_x, new_y = player_x, player_y
                if event.key == pygame.K_LEFT:  new_x -= 1
                if event.key == pygame.K_RIGHT: new_x += 1
                if event.key == pygame.K_UP:    new_y -= 1
                if event.key == pygame.K_DOWN:  new_y += 1
                
                # --- 新增：一鍵通關 (按 C 鍵) ---
                if event.key == pygame.K_c:
                    # 使用 A* 算出從「現在位置」到「終點」的路徑
                    end_pos = (MAZE_W - 2, MAZE_H - 2)
                    _, auto_path, _ = solve_astar(maze, (player_x, player_y), end_pos)
                    if auto_path: # 如果找得到路徑
                        game_state = "AUTO_PILOT"
                        auto_index = 0
                    continue # 跳過後面的手動移動邏輯
                
                # 碰撞與移動處理
                if maze[new_y][new_x] != 1:
                    player_x, player_y = new_x, new_y
                    visible_tiles = get_fov(player_x, player_y, maze, radius=3)
                    explored_tiles.update(visible_tiles) 
                
                # 手動走到終點
                if maze[player_y][player_x] == 2:
                    bfs_order, bfs_path, bfs_time = solve_bfs(maze, (1, 1), (player_x, player_y))
                    astar_order, astar_path, astar_time = solve_astar(maze, (1, 1), (player_x, player_y))
                    game_state = "ANIM_BFS"
                    anim_index = 0

            # 狀態：動畫播放完畢，等待空白鍵切換
            elif event.key == pygame.K_SPACE:
                if game_state == "ANIM_BFS" and anim_index >= len(bfs_order):
                    game_state = "ANIM_ASTAR"
                    anim_index = 0
                elif game_state == "ANIM_ASTAR" and anim_index >= len(astar_order):
                    game_state = "SHOW_PANEL"

    # --- 畫面繪製 ---
    screen.fill(BG_COLOR) 
    
    for row_idx, row in enumerate(maze):
        for col_idx, tile in enumerate(row):
            pos_rect = (OFFSET_X + col_idx * TILE_SIZE, OFFSET_Y + row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            # 遊玩中或自動駕駛中，都顯示迷霧
            if game_state in ["PLAYING", "AUTO_PILOT", "TIME_OUT"]:
                if (col_idx, row_idx) in visible_tiles:
                    if tile == 1: pygame.draw.rect(screen, WALL_COLOR, pos_rect)
                    elif tile == 2: pygame.draw.rect(screen, EXIT_COLOR, pos_rect)
                    else: pygame.draw.rect(screen, PATH_COLOR, pos_rect)
                elif (col_idx, row_idx) in explored_tiles:
                    if tile == 1: pygame.draw.rect(screen, DARK_WALL, pos_rect)
                    elif tile == 2: pygame.draw.rect(screen, DARK_EXIT, pos_rect)
                    else: pygame.draw.rect(screen, DARK_PATH, pos_rect)
            else:
                if tile == 1: pygame.draw.rect(screen, WALL_COLOR, pos_rect)
                elif tile == 2: pygame.draw.rect(screen, EXIT_COLOR, pos_rect)
                else: pygame.draw.rect(screen, PATH_COLOR, pos_rect)

    if game_state == "ANIM_BFS":
        for i in range(min(anim_index, len(bfs_order))):
            x, y = bfs_order[i]
            if maze[y][x] not in [1, 2]: 
                rect = (OFFSET_X + x * TILE_SIZE, OFFSET_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, BFS_COLOR, rect)
        tag = font_title.render("播放中: BFS 廣度優先搜尋", True, (255, 255, 255), (214, 48, 49))
        screen.blit(tag, (10, 10))
        if anim_index < len(bfs_order): anim_index += 3 
        else:
            prompt = font_title.render("請按 [空白鍵] 繼續播放 A* 演算法", True, (255, 255, 255), (50, 50, 50))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 50))

    elif game_state == "ANIM_ASTAR":
        for i in range(min(anim_index, len(astar_order))):
            x, y = astar_order[i]
            if maze[y][x] not in [1, 2]:
                rect = (OFFSET_X + x * TILE_SIZE, OFFSET_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, ASTAR_COLOR, rect)
        tag = font_title.render("播放中: A* 啟發式搜尋", True, (0, 0, 0), (0, 184, 148))
        screen.blit(tag, (10, 10))
        if anim_index < len(astar_order): anim_index += 3
        else:
            prompt = font_title.render("請按 [空白鍵] 查看效能分析報告", True, (255, 255, 255), (50, 50, 50))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 50))

    elif game_state == "SHOW_PANEL":
        for x, y in astar_order:
            if maze[y][x] not in [1, 2]:
                pygame.draw.rect(screen, ASTAR_COLOR, (OFFSET_X + x * TILE_SIZE, OFFSET_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        for x, y in astar_path:
            if maze[y][x] not in [1, 2]:
                pygame.draw.circle(screen, FINAL_PATH_COLOR, (OFFSET_X + x * TILE_SIZE + TILE_SIZE//2, OFFSET_Y + y * TILE_SIZE + TILE_SIZE//2), TILE_SIZE // 3)

        panel_w, panel_h = 450, 300
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2
        pygame.draw.rect(screen, (250, 250, 250), (panel_x, panel_y, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), (panel_x, panel_y, panel_w, panel_h), width=2, border_radius=10)
        
        title_surf = font_title.render("通關成功！尋路效能分析報告", True, (45, 52, 54))
        screen.blit(title_surf, (panel_x + 30, panel_y + 20))
        lines = [
            f"測試起點: (1, 1) -> 終點: ({player_x}, {player_y})",
            f"--------------------------------------------------",
            f"【 廣度優先搜尋 BFS (Queue) 】",
            f"  - 探索節點數 (紅色足跡): {len(bfs_order)} 格",
            f"  - 運算時間: {bfs_time:.4f} ms",
            f"--------------------------------------------------",
            f"【 A* 尋路演算法 (Min-Heap) 】",
            f"  - 探索節點數 (綠色足跡): {len(astar_order)} 格",
            f"  - 運算時間: {astar_time:.4f} ms",
            f"--------------------------------------------------",
            f"結論: A* 減少了 {((len(bfs_order) - len(astar_order))/len(bfs_order))*100:.1f}% 的探索浪費。"
        ]
        curr_y = panel_y + 65
        for line in lines:
            color = (214, 48, 49) if "BFS" in line else (0, 184, 148) if "A*" in line else (45, 52, 54)
            text_surf = font_text.render(line, True, color)
            screen.blit(text_surf, (panel_x + 30, curr_y))
            curr_y += 20

    if game_state != "TIME_OUT":
        pygame.draw.circle(screen, PLAYER_COLOR, 
                           (OFFSET_X + player_x * TILE_SIZE + TILE_SIZE // 2, 
                            OFFSET_Y + player_y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 3)

    if game_state == "PLAYING" or game_state == "AUTO_PILOT":
        timer_color = (255, 255, 255) if time_left > 10 else (255, 50, 50)
        timer_text = font_title.render(f"剩餘時間: {time_left} 秒 (按 C 鍵自動導航)", True, timer_color)
        screen.blit(timer_text, (10, 10))

    elif game_state == "TIME_OUT":
        panel_w, panel_h = 300, 150
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2
        pygame.draw.rect(screen, (45, 52, 54), (panel_x, panel_y, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(screen, (214, 48, 49), (panel_x, panel_y, panel_w, panel_h), width=3, border_radius=10)
        screen.blit(font_title.render("時間到！", True, (214, 48, 49)), (panel_x + 100, panel_y + 40))
        screen.blit(font_text.render("迷失在黑暗中了...", True, (250, 250, 250)), (panel_x + 85, panel_y + 90))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()