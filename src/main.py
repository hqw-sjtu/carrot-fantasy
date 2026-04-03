"""
保卫萝卜 - Carrot Fantasy
塔防游戏主程序
"""
import pygame
from src.towers import TowerFactory
from src.monsters import MonsterFactory
from src.levels import LEVELS

# 初始化
pygame.init()

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

# 游戏状态
class GameState:
    def __init__(self):
        self.money = 200
        self.lives = 10
        self.wave = 0
        self.level = 1
        self.towers = []
        self.monsters = []
        self.game_over = False
        self.victory = False

state = GameState()

def draw_ui():
    """绘制UI"""
    font = pygame.font.Font(None, 24)
    info = f"💰 {state.money} | ❤️ {state.lives} | 🌊 第{state.wave}波 | 📺 关卡{state.level}"
    text = font.render(info, True, WHITE)
    SCREEN.blit(text, (10, 10))
    
    # 防御塔列表
    tower_list = TowerFactory.list_towers()
    for i, tower in enumerate(tower_list):
        info = TowerFactory.get_info(tower)
        t_text = font.render(f"{i+1}.{tower} 💰{info['cost']}", True, YELLOW)
        SCREEN.blit(t_text, (10, 40 + i * 20))

def draw_game():
    """绘制游戏画面"""
    SCREEN.fill(GREEN)
    
    # 绘制路径
    pygame.draw.rect(SCREEN, LIGHT_GREEN, (100, 250, 600, 100))
    
    # 绘制终点(萝卜)
    carrot_pos = (700, 300)
    pygame.draw.circle(SCREEN, ORANGE, carrot_pos, 25)
    pygame.draw.circle(SCREEN, YELLOW, carrot_pos, 15)
    
    # 绘制起点
    pygame.draw.circle(SCREEN, RED, (100, 300), 20)
    
    # 绘制防御塔
    for tower in state.towers:
        color = BLUE if "箭" in tower.name else (RED if "炮" in tower.name else PURPLE)
        pygame.draw.circle(SCREEN, color, (int(tower.x), int(tower.y)), 15)
    
    # 绘制怪物
    for monster in state.monsters:
        color_map = {"green": GREEN, "yellow": YELLOW, "orange": ORANGE, "red": RED, "purple": PURPLE}
        color = color_map.get(monster.monster_type, GRAY)
        x = int(100 + monster.position * 600)
        pygame.draw.circle(SCREEN, color, (x, 300), 12)
    
    draw_ui()

def main():
    """主循环"""
    clock = pygame.time.Clock()
    running = True
    selected_tower = None
    
    # 生成怪物测试
    state.monsters.append(MonsterFactory.create("小怪物"))
    
    while running:
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
        
        # 更新怪物
        for monster in state.monsters[:]:
            if monster.move(1/60):
                state.monsters.remove(monster)
                state.lives -= 1
                if state.lives <= 0:
                    state.game_over = True
        
        # 绘制
        draw_game()
        
        if state.game_over:
            font = pygame.font.Font(None, 48)
            text = font.render("💀 GAME OVER", True, RED)
            SCREEN.blit(text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()