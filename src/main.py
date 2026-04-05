import pygame
import os
pygame.mixer.init()
from src.config_loader import load_config, get_config
from src.state_machine import GameStateMachine
from src.towers import TowerFactory, set_sound_player
from src.monsters import MonsterFactory
from src.projectiles import Projectile
from src.waves import WaveManager
from src.tower_placement import TowerPlacement
from src.ui_panel import UIPanel

# 加载配置
config = load_config()
SCREEN_WIDTH = config['screen']['SCREEN_WIDTH']
SCREEN_HEIGHT = config['screen']['SCREEN_HEIGHT']

# 颜色
WHITE = tuple(config['colors']['WHITE'])
BLACK = tuple(config['colors']['BLACK'])
GREEN = tuple(config['colors']['GREEN'])
RED = tuple(config['colors']['RED'])
BLUE = tuple(config['colors']['BLUE'])
YELLOW = tuple(config['colors']['YELLOW'])
ORANGE = tuple(config['colors']['ORANGE'])
PURPLE = tuple(config['colors']['PURPLE'])
CYAN = tuple(config['colors']['CYAN'])
GRAY = tuple(config['colors']['GRAY'])
SKY_BLUE = tuple(config['colors']['sky_blue'])
GRASS_DARK = tuple(config['colors']['grass_dark'])
GRASS_LIGHT = tuple(config['colors']['grass_light'])
PATH_BROWN = tuple(config['colors']['path_brown'])
PATH_LIGHT_BROWN = tuple(config['colors']['path_light'])

pygame.init()

# 尝试加载音效（可选）
SHOOT_SOUND_PATH = '/usr/share/sounds/pygame/stereo/player_shot.wav'
try:
    shoot_sound = pygame.mixer.Sound(SHOOT_SOUND_PATH) if os.path.exists(SHOOT_SOUND_PATH) else None
except:
    shoot_sound = None

def play_sound(sound):
    if sound:
        try:
            sound.play()
        except:
            pass

# 设置全局音效播放器
set_sound_player(lambda: play_sound(shoot_sound))

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("保卫萝卜 - Carrot Fantasy v0.3")

# 死亡特效列表
death_effects = []  # [(x, y, timer, color), ...]

# 全局游戏状态
state = GameState()

class GameState:
    def __init__(self):
        self.money = 200
        self.lives = 10
        self.wave = 0
        self.level = 1
        self.towers = []
        self.monsters = []
        self.projectiles = []
        self.selected_tower = None
        self.game_over = False
        self.wave_manager = WaveManager()
        self.wave_complete = False
        
    def reset(self):
        self.money = 200
        self.lives = 10
        self.wave = 0
        self.level = 1
        self.towers = []
        self.monsters = []
        self.projectiles = []
        self.selected_tower = None
        self.game_over = False
        self.wave_complete = False
        self.wave_manager = WaveManager()

def draw_gradient_sky(screen, colors, screen_width, screen_height):
    """绘制渐变天空"""
    sky_blue = colors.get('sky_blue', (135, 206, 235))
    white = colors.get('WHITE', (255, 255, 255))
    
    for y in range(0, 300):  # 天空部分高度
        # 计算渐变比例
        ratio = y / 300.0
        # 从浅蓝色到白色渐变
        r = int(sky_blue[0] * (1 - ratio) + white[0] * ratio)
        g = int(sky_blue[1] * (1 - ratio) + white[1] * ratio)
        b = int(sky_blue[2] * (1 - ratio) + white[2] * ratio)
        color = (r, g, b)
        pygame.draw.line(screen, color, (0, y), (screen_width, y))

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
        if "减速" in tower.name:
            color = CYAN
        pygame.draw.circle(SCREEN, color, (int(tower.x), int(tower.y)), 15)
        # 绘制等级星标
        for i in range(tower.level):
            star_x = int(tower.x - 8 + i * 8)
            pygame.draw.circle(SCREEN, YELLOW, (star_x, int(tower.y) - 20), 3)
        # 选中时显示攻击范围
        if hasattr(state, 'selected_tower') and state.selected_tower == tower:
            range_radius = int(tower.range * 50)
            # 半透明范围圈
            range_surf = pygame.Surface((range_radius*2, range_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (*color, 50), (range_radius, range_radius), range_radius)
            pygame.draw.circle(range_surf, (*color, 150), (range_radius, range_radius), range_radius, 2)
            SCREEN.blit(range_surf, (int(tower.x) - range_radius, int(tower.y) - range_radius))
    
    # 绘制怪物
    for monster in state.monsters:
        color_map = {"green": GREEN, "yellow": YELLOW, "orange": ORANGE, "red": RED, "purple": PURPLE}
        color = color_map.get(monster.monster_type, GRAY)
        x = int(100 + monster.position * 600)
        y = 300
        
        # 绘制怪物身体
        pygame.draw.circle(SCREEN, color, (x, y), 12)
        
        # 绘制血条背景（深色边框）
        pygame.draw.rect(SCREEN, (30, 30, 30), (x - 17, y - 27, 34, 9), 1)  # 外框
        pygame.draw.rect(SCREEN, (60, 0, 0), (x - 16, y - 26, 32, 7))  # 背景
        
        # 绘制血条
        health_ratio = monster.health / monster.max_health
        health_width = max(0, int(30 * health_ratio))
        # 颜色渐变
        if health_ratio > 0.6:
            health_color = (50, 200, 50)  # 亮绿
        elif health_ratio > 0.3:
            health_color = (255, 200, 0)  # 金黄
        else:
            health_color = (220, 50, 50)  # 红
        
        pygame.draw.rect(SCREEN, health_color, (x - 15, y - 25, health_width, 5))
        # 高光效果
        if health_width > 5:
            pygame.draw.rect(SCREEN, (255, 255, 255), (x - 14, y - 24, 3, 2))
    
    # 绘制防御塔攻击线（激光效果）
    for tower in state.towers:
        if tower.target and hasattr(tower.target, 'alive') and tower.target.alive:
            # 获取目标屏幕坐标
            tx = int(100 + tower.target.position * 600)
            ty = 300
            # 根据塔类型选择颜色
            if "箭" in tower.name:
                color = BLUE
            elif "炮" in tower.name:
                color = RED
            elif "魔法" in tower.name:
                color = PURPLE
            else:
                color = CYAN
            # 绘制细线（攻击特效）
            pygame.draw.line(SCREEN, color, (int(tower.x), int(tower.y)), (tx, ty), 2)
    
    # 绘制子弹
    for p in state.projectiles:
        p.draw(SCREEN)
    
    # 绘制波次信息
    if state.wave_manager.is_waving:
        font = pygame.font.Font(None, 36)
        wave_text = font.render(f"🌊 波次 {state.wave_manager.current_wave + 1}", True, WHITE)
        SCREEN.blit(wave_text, (SCREEN_WIDTH//2 - 80, 50))
    
    # 绘制死亡特效
    for ef in death_effects[:]:
        ef[2] -= 1/60  # 减少计时
        x, y, timer, color = ef
        # 扩散圆圈效果
        radius = int(30 * (0.5 - timer) * 2)
        if radius > 0:
            pygame.draw.circle(SCREEN, color, (x, y), radius, 2)
        if timer <= 0:
            death_effects.remove(ef)

def draw_game_over_screen():
    """绘制游戏结束画面"""
    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    SCREEN.blit(overlay, (0, 0))
    
    if state.game_over:
        # 失败画面
        font_title = pygame.font.Font(None, 72)
        title = font_title.render("💀 游戏结束", True, RED)
        SCREEN.blit(title, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 80))
        
        font = pygame.font.Font(None, 36)
        info = font.render(f"坚持到第 {state.wave} 波", True, WHITE)
        SCREEN.blit(info, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
    else:
        # 胜利画面（所有波次完成）
        font_title = pygame.font.Font(None, 72)
        title = font_title.render("🎉 胜利！", True, YELLOW)
        SCREEN.blit(title, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 80))
        
        font = pygame.font.Font(None, 36)
        info = font.render("恭喜通关！", True, WHITE)
        SCREEN.blit(info, (SCREEN_WIDTH//2 - 70, SCREEN_HEIGHT//2))
    
    # 重新开始提示
    font_small = pygame.font.Font(None, 28)
    hint = font_small.render("按 R 重新开始", True, GRAY)
    SCREEN.blit(hint, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 60))

def main():
    """主循环"""
    clock = pygame.time.Clock()
    running = True
    
    # 简单的终端关卡选择
    levels = config.get('levels', [{'name': '草地平原', 'difficulty': 1.0}])
    current_level_idx = 0
    difficulty = 1.0
    
    print("=" * 40)
    print("欢迎来到保卫萝卜!")
    print("=" * 40)
    print("选择关卡:")
    for i, level in enumerate(levels):
        print(f"  {i+1}. {level['name']} (难度:{level['difficulty']})")
    print("=" * 40)
    
    # 初始化系统
    tower_placement = TowerPlacement(config)
    ui_panel = UIPanel(config)
    
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
                    tower_placement.select_tower(TowerFactory.list_towers()[0])
                elif event.key == pygame.K_2:
                    tower_placement.select_tower(TowerFactory.list_towers()[1])
                elif event.key == pygame.K_3:
                    tower_placement.select_tower(TowerFactory.list_towers()[2])
                elif event.key == pygame.K_U:
                    # 切换升级模式
                    if tower_placement.upgrade_mode:
                        tower_placement.upgrade_mode = False
                        tower_placement.selected_tower_obj = None
                        state.selected_tower = None
                    else:
                        # 如果已有选中塔，进入升级模式
                        if state.selected_tower:
                            tower_placement.select_tower_for_upgrade(state.selected_tower)
                        else:
                            # 如果没有选中塔，先显示提示信息
                            print("请先选择要升级的防御塔")
                elif event.key == pygame.K_ESCAPE:
                    state.paused = not getattr(state, 'paused', False)
                elif event.key == pygame.K_SPACE:
                    # 跳过当前波次
                    if state.wave_manager.has_more_waves():
                        state.wave_manager.start_wave(state.wave_manager.get_next_wave_index())
                        state.wave += 1
                elif event.key == pygame.K_s:
                    from src.save_system import save_game
                    save_game(state)
                    print("游戏已保存")
                elif event.key == pygame.K_l:
                    from src.save_system import load_game
                    data = load_game()
                    if data:
                        state.money = data.get("money", 200)
                        state.lives = data.get("lives", 10)
                        state.wave = data.get("wave", 0)
                        print("游戏已读取")
                elif event.key == pygame.K_r:
                    # 重新开始游戏
                    state.reset()
                    state.wave_manager = WaveManager()
                    state.wave_manager.start_wave(0)
                    state.wave = 1
                    print("游戏重新开始")
        
        # 处理鼠标事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    tower_placement.select_tower(TowerFactory.list_towers()[0])
                elif event.key == pygame.K_2:
                    tower_placement.select_tower(TowerFactory.list_towers()[1])
                elif event.key == pygame.K_3:
                    tower_placement.select_tower(TowerFactory.list_towers()[2])
                elif event.key == pygame.K_U:
                    # 跳过当前波次
                    if state.wave_manager.has_more_waves():
                        state.wave_manager.start_wave(state.wave_manager.get_next_wave_index())
                        state.wave += 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 处理防御塔放置或升级
                placed = tower_placement.handle_event(event, state)
                
                if placed:
                    # 放置模式：创建防御塔
                    if tower_placement.get_selected_tower():
                        x, y = event.pos
                        tower_type = tower_placement.get_selected_tower()
                        
                        # 创建防御塔
                        tower = TowerFactory.create_tower(tower_type, x, y, config)
                        state.towers.append(tower)
                        
                        # 扣除金币
                        tower_info = config.get('towers', {}).get(tower_type, {})
                        cost = tower_info.get('cost', 0)
                        state.money -= cost
                        
                        # 重置选择状态
                        tower_placement.select_tower(None)
                        
                    # 升级模式：升级防御塔
                    elif tower_placement.upgrade_mode and tower_placement.selected_tower_obj:
                        tower = tower_placement.selected_tower_obj
                        
                        # 检查是否可以升级
                        if tower.can_upgrade():
                            upgrade_cost = tower.get_upgrade_cost()
                            
                            # 检查金币是否足够
                            if state.money >= upgrade_cost:
                                # 升级防御塔
                                tower.upgrade()
                                state.money -= upgrade_cost
                                
                                # 重置升级模式
                                tower_placement.upgrade_mode = False
                                tower_placement.selected_tower_obj = None
                                
                                # 更新选中塔状态
                                if state.selected_tower == tower:
                                    state.selected_tower = tower
                            else:
                                print("金币不足，无法升级")
                        else:
                            print("防御塔已达到最大等级")
                
                # 检查是否点击了防御塔进行选择
                else:
                    x, y = event.pos
                    for tower in state.towers:
                        dx = tower.x - x
                        dy = tower.y - y
                        if (dx*dx + dy*dy) ** 0.5 < 15:  # 点击防御塔范围内
                            state.selected_tower = tower
                            break
                    else:
                        state.selected_tower = None
        
        # 暂停处理
        if getattr(state, 'paused', False):
            # 绘制暂停菜单
            pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 150))
            SCREEN.blit(pause_overlay, (0, 0))
            
            font = pygame.font.Font(None, 64)
            text = font.render("⏸️ 暂停", True, WHITE)
            SCREEN.blit(text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 50))
            
            font_small = pygame.font.Font(None, 32)
            hint = font_small.render("按 ESC 继续 | S 保存 | L 读取", True, YELLOW)
            SCREEN.blit(hint, (SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT//2 + 20))
            
            pygame.display.flip()
            continue
        
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
        
        # 检测并处理死亡的怪物（添加击杀特效）
        for monster in state.monsters[:]:
            if not monster.alive:
                # 添加爆炸特效
                mx = int(100 + monster.position * 600)
                death_effects.append([mx, 300, 0.5, RED])  # 0.5秒红色爆炸
                state.monsters.remove(monster)
                # 加钱
                state.money += getattr(monster, 'reward', 10)
        
        # 绘制
        draw_game()
        
        # 绘制UI面板
        ui_panel.draw(SCREEN, state)
        
        # 绘制防御塔放置预览
        tower_placement.draw_placement_preview(SCREEN, state)
        
        # 绘制游戏状态
        if tower_placement.upgrade_mode:
            font = pygame.font.Font(None, 32)
            upgrade_text = font.render("升级模式: 点击要升级的防御塔", True, (255, 255, 0))
            SCREEN.blit(upgrade_text, (SCREEN_WIDTH//2 - 140, 20))
        
        # 绘制游戏结束画面（胜利或失败）
        if state.game_over or (state.wave >= 10 and len(state.monsters) == 0):
            draw_game_over_screen()
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()