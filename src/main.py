import pygame
pygame.init()
pygame.font.init()
from src.towers import TowerFactory
from src.monsters import MonsterFactory
from src.levels import LEVELS
from src.projectiles import Projectile
from src.waves import WaveManager

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("保卫萝卜 - Carrot Fantasy v0.2")

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
ORANGE = (255, 165, 0)
YELLOW = (255, 215, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

# 背景美化颜色
SKY_BLUE = (135, 206, 235)
LIGHT_SKY_BLUE = (176, 224, 230)
GRASS_DARK = (0, 100, 0)
GRASS_LIGHT = (50, 205, 50)
PATH_BROWN = (139, 69, 19)
PATH_LIGHT_BROWN = (160, 120, 90)
FLOWER_PINK = (255, 182, 193)
FLOWER_YELLOW = (255, 255, 0)
STONE_GRAY = (105, 105, 105)
SUNLIGHT_YELLOW = (255, 255, 200)
SUNLIGHT_YELLOW_ALPHA = (255, 255, 200, 64)  # 带透明度的暖黄色

# 游戏状态
class GameState:
    def __init__(self):
        self.money = 200
        self.lives = 10
        self.wave = 0
        self.level = 1
        self.towers = []
        self.monsters = []
        self.projectiles = []  # 所有子弹
        self.game_over = False
        self.wave_manager = WaveManager()  # 波次管理器

state = GameState()

def draw_ui():
    """绘制美化UI"""
    # 顶部信息栏背景框
    ui_bg = pygame.Surface((300, 100), pygame.SRCALPHA)
    ui_bg.fill((0, 0, 0, 128))  # 半透明黑色背景
    SCREEN.blit(ui_bg, (5, 5))
    
    # 信息栏边框
    pygame.draw.rect(SCREEN, YELLOW, (5, 5, 300, 100), 2)
    
    font = pygame.font.Font(None, 28)
    info = f"💰 {state.money}  |  ❤️ {state.lives}  |  🌊 第{state.wave}波  |  📺 {state.level}关"
    text = font.render(info, True, WHITE)
    SCREEN.blit(text, (15, 15))
    
    # 防御塔列表
    tower_list = TowerFactory.list_towers()
    for i, tower in enumerate(tower_list):
        info = TowerFactory.get_info(tower)
        t_text = font.render(f"{i+1}.{tower} 💰{info['cost']}", True, YELLOW)
        SCREEN.blit(t_text, (10, 40 + i * 20))

def draw_gradient_sky():
    """绘制渐变天空"""
    for y in range(0, 300):  # 天空部分高度
        # 计算渐变比例
        ratio = y / 300.0
        # 从浅蓝色到白色渐变
        r = int(SKY_BLUE[0] * (1 - ratio) + WHITE[0] * ratio)
        g = int(SKY_BLUE[1] * (1 - ratio) + WHITE[1] * ratio)
        b = int(SKY_BLUE[2] * (1 - ratio) + WHITE[2] * ratio)
        color = (r, g, b)
        pygame.draw.line(SCREEN, color, (0, y), (SCREEN_WIDTH, y))

def draw_grass_texture():
    """绘制草地纹理"""
    # 先绘制基础草地颜色
    pygame.draw.rect(SCREEN, GRASS_LIGHT, (0, 300, SCREEN_WIDTH, SCREEN_HEIGHT - 300))
    
    # 添加草地质感小方块
    for i in range(0, SCREEN_WIDTH, 10):
        for j in range(300, SCREEN_HEIGHT, 10):
            # 随机深浅绿色
            if (i + j) % 20 < 10:
                grass_color = GRASS_DARK
            else:
                grass_color = GRASS_LIGHT
            
            # 随机偏移使草地看起来更自然
            offset_x = (i + j) % 7 - 3
            offset_y = (i * 2 - j) % 5 - 2
            
            pygame.draw.rect(SCREEN, grass_color, 
                            (i + offset_x, j + offset_y, 8, 8))

def draw_path_with_details():
    """绘制带细节的路径"""
    # 主路径
    pygame.draw.rect(SCREEN, PATH_BROWN, (100, 250, 600, 100))
    
    # 路径边缘细节
    pygame.draw.rect(SCREEN, PATH_LIGHT_BROWN, (95, 245, 610, 10))  # 上边缘
    pygame.draw.rect(SCREEN, PATH_LIGHT_BROWN, (95, 345, 610, 10))  # 下边缘
    pygame.draw.rect(SCREEN, PATH_LIGHT_BROWN, (90, 250, 10, 100))  # 左边缘
    pygame.draw.rect(SCREEN, PATH_LIGHT_BROWN, (695, 250, 10, 100))  # 右边缘
    
    # 路径纹理细节
    for i in range(10):
        x = 120 + i * 60
        y = 270 + (i % 3) * 20
        pygame.draw.ellipse(SCREEN, PATH_LIGHT_BROWN, (x, y, 40, 15))

def draw_decorations():
    """绘制装饰元素"""
    # 随机位置的小花
    flower_positions = [
        (50, 400), (150, 450), (250, 380), (350, 420), 
        (450, 390), (550, 440), (650, 410), (750, 380)
    ]
    
    for x, y in flower_positions:
        # 随机选择花色
        if (x + y) % 3 == 0:
            flower_color = FLOWER_PINK
        else:
            flower_color = FLOWER_YELLOW
        
        # 绘制花朵
        pygame.draw.circle(SCREEN, flower_color, (x, y), 6)
        # 绘制花心
        pygame.draw.circle(SCREEN, YELLOW, (x, y), 2)
    
    # 随机位置的小石头
    stone_positions = [
        (80, 500), (180, 520), (280, 480), (380, 510),
        (480, 490), (580, 530), (680, 495), (780, 515)
    ]
    
    for x, y in stone_positions:
        pygame.draw.ellipse(SCREEN, STONE_GRAY, (x - 5, y - 3, 10, 6))

def draw_sunlight_effect():
    """绘制暖色调光照效果"""
    # 创建一个半透明的表面来添加暖色调
    sunlight_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    # 使用RGBA颜色填充表面
    sunlight_surface.fill((255, 255, 200, 64))
    SCREEN.blit(sunlight_surface, (0, 0))

def draw_game():
    """绘制游戏画面"""
    # 清屏
    SCREEN.fill(BLACK)
    
    # 绘制背景美化元素
    draw_gradient_sky()
    draw_grass_texture()
    draw_path_with_details()
    draw_decorations()
    draw_sunlight_effect()
    
    # 绘制路径（原路径已被美化函数覆盖）
    
    # 绘制美化终点(萝卜)
    carrot_pos = (700, 300)
    # 萝卜身体（多层圆形叠加）
    pygame.draw.circle(SCREEN, (255, 140, 0), carrot_pos, 28)  # 深橙色外圈
    pygame.draw.circle(SCREEN, ORANGE, carrot_pos, 22)  # 橙色主体
    pygame.draw.circle(SCREEN, (255, 200, 100), carrot_pos, 14)  # 浅色高光
    # 萝卜叶子
    pygame.draw.polygon(SCREEN, (34, 139, 34), [(680, 270), (700, 240), (720, 270)])
    pygame.draw.polygon(SCREEN, (50, 205, 50), [(695, 275), (720, 250), (710, 280)])
    
    # 绘制美化起点（传送门效果）
    start_pos = (100, 300)
    # 外圈光环
    pygame.draw.circle(SCREEN, (200, 50, 50), start_pos, 28, 3)
    pygame.draw.circle(SCREEN, (255, 100, 100), start_pos, 22, 2)
    # 中心
    pygame.draw.circle(SCREEN, RED, start_pos, 15)
    pygame.draw.circle(SCREEN, (255, 150, 150), start_pos, 8)
    
    # 绘制防御塔
    for tower in state.towers:
        color = BLUE if "箭" in tower.name else (RED if "炮" in tower.name else PURPLE)
        pygame.draw.circle(SCREEN, color, (int(tower.x), int(tower.y)), 15)
        # 绘制攻击范围(可选)
        # pygame.draw.circle(SCREEN, (255,255,255), (int(tower.x), int(tower.y)), int(tower.range*50), 1)
    
    # 绘制怪物
    for monster in state.monsters:
        color_map = {"green": GREEN, "yellow": YELLOW, "orange": ORANGE, "red": RED, "purple": PURPLE}
        color = color_map.get(monster.monster_type, GRAY)
        x = int(100 + monster.position * 600)
        y = 300
        
        # 绘制怪物身体
        pygame.draw.circle(SCREEN, color, (x, y), 12)
        
        # 绘制血条背景（带边框）
        pygame.draw.rect(SCREEN, (50, 0, 0), (x - 16, y - 26, 32, 7))  # 边框
        pygame.draw.rect(SCREEN, (80, 0, 0), (x - 15, y - 25, 30, 5))  # 背景
        
        # 绘制血条
        health_ratio = monster.health / monster.max_health
        health_width = max(0, int(30 * health_ratio))  # 防止负数
        
        # 血条颜色根据血量变化
        if health_ratio > 0.6:
            health_color = (0, 255, 0)  # 绿色
        elif health_ratio > 0.3:
            health_color = (255, 255, 0)  # 黄色
        else:
            health_color = (255, 0, 0)  # 红色
        
        pygame.draw.rect(SCREEN, health_color, (x - 15, y - 25, health_width, 5))
    
    # 绘制子弹
    for p in state.projectiles:
        p.draw(SCREEN)
    
    # 绘制波次信息
    if state.wave_manager.is_waving:
        font = pygame.font.Font(None, 36)
        wave_text = font.render(f"🌊 波次 {state.wave_manager.current_wave + 1}", True, WHITE)
        SCREEN.blit(wave_text, (SCREEN_WIDTH//2 - 80, 50))

def main():
    """主循环"""
    clock = pygame.time.Clock()
    running = True
    selected_tower = None
    
    # 初始化波次
    state.wave_manager.start_wave(0)
    state.wave = 1
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_tower = TowerFactory.list_towers()[0]
                elif event.key == pygame.K_2:
                    selected_tower = TowerFactory.list_towers()[1]
                elif event.key == pygame.K_3:
                    selected_tower = TowerFactory.list_towers()[2]
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 跳过当前波次
                    if state.wave_manager.has_more_waves():
                        state.wave_manager.start_wave(state.wave_manager.get_next_wave_index())
                        state.wave += 1
        
        # 更新波次系统
        state.wave_manager.update(dt, state)
        
        # 如果波次完成了，开始下一波
        if state.wave_manager.is_wave_complete() and state.wave_manager.has_more_waves():
            state.wave_manager.start_wave(state.wave_manager.get_next_wave_index())
            state.wave += 1
        
        # 更新怪物位置
        for monster in state.monsters[:]:
            monster.x = int(100 + monster.position * 600)
            if monster.move(dt):
                state.monsters.remove(monster)
                state.lives -= 1
                if state.lives <= 0:
                    state.game_over = True
        
        # 防御塔攻击
        for tower in state.towers:
            tower.attack(state.monsters, state.projectiles)
            
        # 更新子弹
        for p in state.projectiles[:]:
            p.update(dt)
            if not p.active:
                state.projectiles.remove(p)
        
        # 绘制
        draw_game()
        
        if state.game_over:
            font = pygame.font.Font(None, 48)
            text = font.render("💀 GAME OVER", True, RED)
            SCREEN.blit(text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()