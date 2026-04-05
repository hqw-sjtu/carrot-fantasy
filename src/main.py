import pygame
import os
import random
import time
import math
import datetime

# 截图保存目录
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot():
    """保存截图"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"carrot_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    pygame.image.save(SCREEN, filepath)
    print(f"📸 截图已保存: {filename}")
    return filename

# 路径区域（怪物行走路线）
PATH_RECT = pygame.Rect(100, 280, 600, 40)  # 路径矩形区域

# 游戏统计
stats = {
    "kills": 0,
    "damage_dealt": 0,
    "towers_built": 0,
    "towers_upgraded": 0,
    "gold_spent": 0,
    "gold_earned": 0,
}

# ==================== 成就系统 ====================
achievements = {
    "first_blood": {"name": "🎯 首次击杀", "desc": "击杀第一只怪物", "unlocked": False},
    "ten_kills": {"name": "💀 击杀10只", "desc": "累计击杀10只怪物", "unlocked": False},
    "fifty_kills": {"name": "💀 击杀50只", "desc": "累计击杀50只怪物", "unlocked": False},
    "upgrade_tower": {"name": "⬆️ 首次升级", "desc": "升级第一座塔", "unlocked": False},
    "sell_tower": {"name": "💰 首次出售", "desc": "出售第一座塔", "unlocked": False},
    "no_damage_wave": {"name": "🛡️ 无伤波次", "desc": "一波不失血", "unlocked": False},
    "fast_win": {"name": "⚡ 速通", "desc": "3分钟内通关", "unlocked": False},
}
total_kills = 0
achievement_notify = ""  # 当前显示的成就
achievement_timer = 0

# 波次无伤检测
wave_no_damage = True

# 游戏时间
game_start_time = time.time()

# FPS计算
fps = 60
fps_counter = 0
fps_timer = 0
display_time = 0  # 显示用

# 最后一波提示
final_wave_announced = False

# 通关时间记录
game_complete_time = None

# Boss血条
boss_bar_drawn = False

# 音乐控制
music_enabled = True
music_volume = 0.5
BGMusic = None

pygame.mixer.init()
from src.config_loader import load_config, get_config

# 游戏速度
game_speed = 1.0  # 1.0=正常, 2.0=快进, 0.5=慢放
speed_labels = {0.5: "🐢 慢放", 1.0: "▶️ 正常", 2.0: "⏩ 快进"}
from src.state_machine import GameStateMachine
from src.towers import TowerFactory, set_sound_player
from src.monsters import MonsterFactory
from src.projectiles import Projectile
from src.waves import WaveManager
from src.tower_placement import TowerPlacement

# 屏幕震动
screen_shake = 0
screen_shake_offset = [0, 0]

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

# 放置特效
place_effects = []  # [(x, y, color, timer), ...]

# 死亡特效列表
death_effects = []  # [(x, y, timer, color), ...]

# 升级特效
upgrade_effects = []  # [(x, y, timer), ...]

# 升级属性变化显示 [(x, y, old_damage, new_damage, old_range, new_range, timer)]
upgrade_info_display = []

# 金币动画列表
coin_animations = []  # [(x, y, amount, timer), ...]

# 连杀系统
kill_streak = 0  # 当前连杀数
kill_streak_timer = 0  # 连杀计时
combo_text = ""  # 连杀文字

# 金币不足警告
no_money_warning = ""
no_money_timer = 0

# 波次提示
wave_tip = ""  # 波次提示文字
wave_tip_timer = 0  # 提示显示计时

# 生命值警告
low_life_warning = False
low_life_timer = 0

# 显示详细血量
show_health_detail = False

# 显示统计面板
show_stats = False

# 波次间隔
wave_wait_timer = 0
wave_wait_duration = 5.0  # 每波间隔5秒

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
        self.mouse_preview = None  # 塔放置预览位置
        self.paused = False  # 暂停状态
        
    def reset(self):
        global final_wave_announced, game_complete_time
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
        # 游戏重置
        final_wave_announced = False
        game_complete_time = None

def draw_game():
    """绘制游戏画面"""
    # 应用屏幕震动
    global screen_shake, screen_shake_offset, time_str
    if screen_shake > 0:
        screen_shake_offset[0] = random.randint(-screen_shake, screen_shake)
        screen_shake_offset[1] = random.randint(-screen_shake, screen_shake)
        screen_shake *= 0.9  # 衰减
        if screen_shake < 0.5:
            screen_shake = 0
            screen_shake_offset = [0, 0]
    else:
        screen_shake_offset = [0, 0]
    
    # 清屏
    SCREEN.fill(BLACK)
    
    # 绘制背景
    # ... (existing drawing code would go here)
    
    # 示例: 绘制一个简单的场景
    # 这里应该包含所有游戏对象的绘制，但为了演示，我会简化
    shake_x, shake_y = screen_shake_offset
    
    # 绘制怪物行走路线
    path_color = (60, 60, 60)  # 深灰色路线
    path_width = 40
    pygame.draw.rect(SCREEN, path_color, (100, 300 - path_width//2, 600, path_width))
    
    # 路线装饰虚线
    for i in range(10):
        x = 100 + i * 60 + 30
        pygame.draw.line(SCREEN, (80, 80, 80), (x, 300 - 15), (x, 300 + 15), 2)
    
    # 绘制塔基座格子（8x4网格）
    TILE_SIZE = 60
    TILE_START_X = 80
    TILE_START_Y = 180
    
    # 可放置区域格子
    for row in range(4):
        for col in range(8):
            x = TILE_START_X + col * TILE_SIZE
            y = TILE_START_Y + row * TILE_SIZE
            
            # 检测格子是否在路径上
            tile_rect = pygame.Rect(x + 10, y + 10, TILE_SIZE - 20, TILE_SIZE - 20)
            if not PATH_RECT.colliderect(tile_rect):
                # 可放置格子 - 浅色边框
                pygame.draw.rect(SCREEN, (50, 50, 50), (x, y, TILE_SIZE, TILE_SIZE), 1)
                # 内部小点标记
                pygame.draw.circle(SCREEN, (40, 40, 40), (x + TILE_SIZE//2, y + TILE_SIZE//2), 3)
    
    # 起点和终点标记
    # 起点
    pygame.draw.circle(SCREEN, GREEN, (100, 300), 15)
    font_mark = pygame.font.Font(None, 20)
    start_text = font_mark.render("S", True, WHITE)
    SCREEN.blit(start_text, (95, 293))
    
    # 终点（萝卜位置）
    pygame.draw.circle(SCREEN, (255, 140, 0), (700 + shake_x, 300 + shake_y), 28)  # 深橙色外圈
    pygame.draw.circle(SCREEN, ORANGE, (700 + shake_x, 300 + shake_y), 22)  # 橙色主体
    pygame.draw.circle(SCREEN, (255, 200, 100), (700 + shake_x, 300 + shake_y), 14)  # 浅色高光
    
    # 绘制怪物（带震动偏移）
    for monster in state.monsters:
        x = int(100 + monster.position * 600)
        y = 300
        pygame.draw.circle(SCREEN, GREEN, (x + shake_x, y + shake_y), 12)
        
        # 绘制血条背景（带边框）
        pygame.draw.rect(SCREEN, (30, 30, 30), (x - 17 + shake_x, y - 27 + shake_y, 34, 9), 1)
        pygame.draw.rect(SCREEN, (60, 0, 0), (x - 16 + shake_x, y - 26 + shake_y, 32, 7))
        
        # 绘制血条
        health_ratio = monster.health / monster.max_health
        health_width = max(0, int(30 * health_ratio))
        # 颜色渐变
        if health_ratio > 0.6:
            health_color = (50, 200, 50)
        elif health_ratio > 0.3:
            health_color = (255, 200, 0)
        else:
            health_color = (220, 50, 50)
        pygame.draw.rect(SCREEN, health_color, (x - 15 + shake_x, y - 25 + shake_y, health_width, 5))
        
        # 详细血量显示（按H切换）
        if show_health_detail:
            font_health = pygame.font.Font(None, 18)
            health_text = font_health.render(f"{int(monster.health)}/{int(monster.max_health)}", True, WHITE)
            SCREEN.blit(health_text, (x - 20 + shake_x, y - 42 + shake_y))
    
    # 检测Boss并绘制特殊血条
    global boss_bar_drawn
    for monster in state.monsters:
        if hasattr(monster, 'is_boss') and monster.is_boss:
            # 绘制Boss血条（屏幕顶部）
            boss_bar_width = 400
            boss_bar_x = (SCREEN_WIDTH - boss_bar_width) // 2
            boss_bar_y = 10
            
            # 血条背景
            pygame.draw.rect(SCREEN, (50, 0, 0), (boss_bar_x, boss_bar_y, boss_bar_width, 20))
            pygame.draw.rect(SCREEN, (200, 0, 0), (boss_bar_x + 2, boss_bar_y + 2, boss_bar_width - 4, 16))
            
            # 血条
            boss_hp_ratio = monster.health / monster.max_health
            boss_hp_width = int((boss_bar_width - 4) * boss_hp_ratio)
            pygame.draw.rect(SCREEN, (255, 50, 50), (boss_bar_x + 2, boss_bar_y + 2, boss_hp_width, 16))
            
            # Boss文字
            font_boss = pygame.font.Font(None, 24)
            boss_text = font_boss.render("👹 BOSS", True, RED)
            SCREEN.blit(boss_text, (boss_bar_x - 50, boss_bar_y))
            
            boss_bar_drawn = True
            break
    
    # 绘制防御塔（不同形状）
    for tower in state.towers:
        tx, ty = int(tower.x), int(tower.y)
        
        # 判断塔是否被选中
        is_selected = (tower == state.selected_tower)
        
        # 塔的颜色（被选中时高亮）
        tower_color = YELLOW if is_selected else BLUE
        
        # 选中时显示攻击范围（圆形）- 使用塔类型颜色
        if is_selected:
            range_radius = int(tower.range * 50)
            
            # 根据塔类型选择颜色
            if "箭" in tower.name:
                range_color = (*BLUE, 80)  # 蓝色半透明
                border_color = BLUE
            elif "炮" in tower.name:
                range_color = (*RED, 80)
                border_color = RED
            elif "魔法" in tower.name:
                range_color = (*PURPLE, 80)
                border_color = PURPLE
            elif "减速" in tower.name:
                range_color = (*CYAN, 80)
                border_color = CYAN
            else:
                range_color = (100, 100, 100, 80)
                border_color = WHITE
            
            # 半透明填充圆
            range_surf = pygame.Surface((range_radius*2, range_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, range_color, (range_radius, range_radius), range_radius)
            SCREEN.blit(range_surf, (int(tower.x) - range_radius + shake_x, int(tower.y) - range_radius + shake_y))
            
            # 实线圆边框
            pygame.draw.circle(SCREEN, border_color, (int(tower.x) + shake_x, int(tower.y) + shake_y), range_radius, 2)
            
            # 内圈装饰点
            for angle in range(0, 360, 30):
                rad = angle * 3.14159 / 180
                px = int(tower.x + range_radius * 0.5 * math.cos(rad))
                py = int(tower.y + range_radius * 0.5 * math.sin(rad))
                pygame.draw.circle(SCREEN, (*border_color, 100), (px + shake_x, py + shake_y), 2)
            
            # 选中塔显示范围内敌人数量
            in_range_count = 0
            range_pixels = tower.range * 50
            for m in state.monsters:
                mx = 100 + m.position * 600
                my = 300
                dx = mx - tower.x
                dy = my - tower.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist <= range_pixels:
                    in_range_count += 1
            
            if in_range_count > 0:
                font_count = pygame.font.Font(None, 20)
                count_text = f"👾{in_range_count}"
                count_surf = font_count.render(count_text, True, RED)
                SCREEN.blit(count_surf, (int(tower.x) + 20 + shake_x, int(tower.y) - 25 + shake_y))
        
        # 绘制防御塔（不同形状）
        if "箭" in tower.name:
            # 箭塔：三角形
            points = [(tx, ty - 15), (tx - 12, ty + 10), (tx + 12, ty + 10)]
            pygame.draw.polygon(SCREEN, tower_color, points)
        elif "炮" in tower.name:
            # 炮塔：正方形
            pygame.draw.rect(SCREEN, tower_color, (tx - 12, ty - 12, 24, 24))
        elif "魔法" in tower.name:
            # 魔法塔：六边形（用圆模拟）
            pygame.draw.circle(SCREEN, tower_color, (tx, ty), 14)
            pygame.draw.circle(SCREEN, (200, 100, 255), (tx, ty), 8)
        elif "减速" in tower.name:
            # 减速塔：菱形
            points = [(tx, ty - 15), (tx + 15, ty), (tx, ty + 15), (tx - 15, ty)]
            pygame.draw.polygon(SCREEN, tower_color, points)
        else:
            # 默认：圆形
            pygame.draw.circle(SCREEN, tower_color, (tx, ty), 15)
    
    # 绘制防御塔攻击线（锁定目标）
    for tower in state.towers:
        if hasattr(tower, 'target') and tower.target and hasattr(tower.target, 'alive') and tower.target.alive:
            # 获取目标位置
            tx = int(100 + tower.target.position * 600)
            ty = 300
            
            # 塔颜色
            if "箭" in tower.name:
                color = BLUE
            elif "炮" in tower.name:
                color = RED
            elif "魔法" in tower.name:
                color = PURPLE
            elif "减速" in tower.name:
                color = CYAN
            else:
                color = WHITE
            
            # 目标锁定线（实线）
            pygame.draw.line(SCREEN, color, (int(tower.x) + shake_x, int(tower.y) + shake_y), (tx + shake_x, ty + shake_y), 2)
            
            # 目标点高亮（红色小点）
            pygame.draw.circle(SCREEN, (255, 50, 50), (tx + shake_x, ty + shake_y), 5)
            pygame.draw.circle(SCREEN, WHITE, (tx + shake_x, ty + shake_y), 3)
    
    # 绘制连杀提示
    if combo_text and kill_streak_timer > 0:
        font_combo = pygame.font.Font(None, 36)
        combo_surf = font_combo.render(combo_text, True, (255, 100, 0))
        SCREEN.blit(combo_surf, (SCREEN_WIDTH//2 - 60, 150))
    
    # 绘制金币不足警告
    if no_money_timer > 0:
        font_warn = pygame.font.Font(None, 36)
        warn_text = font_warn.render(no_money_warning, True, RED)
        # 闪烁效果
        if int(no_money_timer * 10) % 2 == 0:
            SCREEN.blit(warn_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2))
    
    # 绘制速度状态
    if game_speed != 1.0:
        font_speed = pygame.font.Font(None, 32)
        speed_text = font_speed.render(speed_labels[game_speed], True, YELLOW)
        SCREEN.blit(speed_text, (SCREEN_WIDTH - 100, 10))
    
    # 显示游戏时间（右上角）
    font_time = pygame.font.Font(None, 32)
    time_text = font_time.render(time_str, True, WHITE)
    SCREEN.blit(time_text, (SCREEN_WIDTH - 80, 50))
    
    # 显示FPS
    font_fps = pygame.font.Font(None, 24)
    fps_text = font_fps.render(f"FPS: {fps}", True, (100, 255, 100))
    SCREEN.blit(fps_text, (10, 10))
    
    # 绘制波次提示（最终波提示）
    if wave_tip and wave_tip_timer > 0:
        font_tip = pygame.font.Font(None, 48)
        tip_surf = font_tip.render(wave_tip, True, (255, 50, 50))
        SCREEN.blit(tip_surf, (SCREEN_WIDTH//2 - 100, 100))
    
    # 显示下一波预览
    if not state.wave_manager.is_waving and state.wave_manager.has_more_waves():
        next_wave = state.wave_manager.get_next_wave_index()
        wave_data = state.wave_manager.waves[next_wave] if next_wave < len(state.wave_manager.waves) else None
        if wave_data:
            font_preview = pygame.font.Font(None, 24)
            # 获取怪物类型名称
            monsters_list = wave_data.get('monsters', [])
            if monsters_list:
                monster_names = [m[0] for m in monsters_list]
                preview_text = f"下一波: {', '.join(monster_names)}"
            else:
                preview_text = "下一波: 混合"
            preview_surf = font_preview.render(preview_text, True, (200, 200, 200))
            SCREEN.blit(preview_surf, (SCREEN_WIDTH//2 - 60, 120))
    
    # 成就通知
    global achievement_timer
    if achievement_timer > 0:
        achievement_timer -= dt * game_speed
        font_ach = pygame.font.Font(None, 32)
        ach_text = font_ach.render(achievement_notify, True, YELLOW)
        SCREEN.blit(ach_text, (SCREEN_WIDTH//2 - 100, 180))
    
    # 生命值不足警告
    if low_life_warning and low_life_timer > 0:
        font_warn = pygame.font.Font(None, 48)
        warn_text = font_warn.render("❤️ 生命值告急！", True, RED)
        # 闪烁效果
        if int(low_life_timer * 5) % 2 == 0:
            SCREEN.blit(warn_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 100))
    
    # 绘制胜利画面
    if game_complete_time is not None:
        victory_minutes = game_complete_time // 60
        victory_seconds = game_complete_time % 60
        time_str = f"通关时间: {victory_minutes}分{victory_seconds}秒"
        font_victory = pygame.font.Font(None, 64)
        victory_surf = font_victory.render("🎉 胜利！", True, (255, 215, 0))
        font_time2 = pygame.font.Font(None, 36)
        time_surf = font_time2.render(time_str, True, WHITE)
        SCREEN.blit(victory_surf, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 50))
        SCREEN.blit(time_surf, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20))
    
    # 底部操作提示
    font_hint = pygame.font.Font(None, 24)
    hint_text = f"Tab:速度 | 1-3:选塔 | U:升级 | H:血量 | T:统计 | M:音效 | 点击:放置  金币:{state.money}  生命:{state.lives}  波次:{state.wave}"
    hint_surf = font_hint.render(hint_text, True, GRAY)
    SCREEN.blit(hint_surf, (10, SCREEN_HEIGHT - 30))
    
    # 绘制升级特效
    for ef in upgrade_effects[:]:
        ef[2] -= dt * game_speed
        x, y, timer = ef
        # 金色光芒扩散
        radius = int(40 * (1 - timer))
        if radius > 0:
            pygame.draw.circle(SCREEN, YELLOW, (x + shake_x, y + shake_y), radius, 3)
        # 星星效果
        if timer > 0.5:
            for i in range(4):
                sx = int(x + 25 * (1-timer*2) * (1 if i%2==0 else -1) * (1 if i<2 else -1))
                sy = int(y + 25 * (1-timer*2) * (1 if i%2==1 else -1) * (1 if i<2 else -1))
                pygame.draw.circle(SCREEN, WHITE, (sx + shake_x, sy + shake_y), 3)
        if timer <= 0:
            upgrade_effects.remove(ef)
    
    # 绘制升级属性变化显示
    for info in upgrade_info_display[:]:
        info[6] -= dt * game_speed  # timer
        x, y, old_dmg, new_dmg, old_rng, new_rng, timer = info
        
        # 格式: ↑ 伤害:10→13 射程:100→110
        old_range_px = int(old_rng * 50)
        new_range_px = int(new_rng * 50)
        upgrade_text = f"↑ 伤害:{old_dmg}→{new_dmg} 射程:{old_range_px}→{new_range_px}"
        
        # 文字上浮效果
        float_y = y - 40 - int((1 - timer / 2.0) * 20)  # 上浮20像素
        
        font_up = pygame.font.Font(None, 24)
        up_surf = font_up.render(upgrade_text, True, YELLOW)
        # 文字描边效果
        outline_surf = font_up.render(upgrade_text, True, BLACK)
        SCREEN.blit(outline_surf, (int(x) - 58 + shake_x + 1, float_y + shake_y + 1))
        SCREEN.blit(up_surf, (int(x) - 58 + shake_x, float_y + shake_y))
        
        if timer <= 0:
            upgrade_info_display.remove(info)
    
    # 绘制放置特效
    for ef in place_effects[:]:
        ef[3] -= dt * game_speed
        x, y, color, timer = ef
        # 波纹扩散
        radius = int(40 * (0.8 - timer))
        if radius > 0 and radius < 40:
            pygame.draw.circle(SCREEN, color, (x + shake_x, y + shake_y), radius, 2)
        # 中心闪光
        if timer > 0.6:
            pygame.draw.circle(SCREEN, WHITE, (x + shake_x, y + shake_y), int(10 * (0.8-timer)*2), 2)
        if timer <= 0:
            place_effects.remove(ef)
    
    # 波次间隔倒计时显示
    global wave_wait_timer
    if wave_wait_timer > 0:
        wait_text = f"下一波: {int(wave_wait_timer) + 1}秒"
        font_wait = pygame.font.Font(None, 36)
        wait_surf = font_wait.render(wait_text, True, YELLOW)
        SCREEN.blit(wait_surf, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2))
    
    # 显示统计面板
    if show_stats:
        stats_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 200)
        pygame.draw.rect(SCREEN, (0, 0, 180), stats_rect)
        pygame.draw.rect(SCREEN, YELLOW, stats_rect, 2)
        
        font_stats = pygame.font.Font(None, 28)
        y = stats_rect.y + 20
        for key, label in [("kills", "击杀"), ("towers_built", "建造"), ("towers_upgraded", "升级"), ("gold_spent", "花费"), ("gold_earned", "获得")]:
            text = font_stats.render(f"{label}: {stats[key]}", True, WHITE)
            SCREEN.blit(text, (stats_rect.x + 20, y))
            y += 30

# 主循环
def main():
    """主循环"""
    global game_start_time, display_time, game_complete_time
    clock = pygame.time.Clock()
    running = True
    
    # 初始化游戏开始时间
    game_start_time = time.time()
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        effective_dt = dt * game_speed  # 应用游戏速度
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Tab切换速度
                if event.key == pygame.K_TAB:
                    if game_speed == 1.0:
                        game_speed = 2.0
                    elif game_speed == 2.0:
                        game_speed = 0.5
                    else:
                        game_speed = 1.0
                # H键切换血量显示
                elif event.key == pygame.K_h:
                    show_health_detail = not show_health_detail
                # 升级选中塔 (按U键)
                elif event.key == pygame.K_u and state.selected_tower:
                    tower = state.selected_tower
                    if tower.can_upgrade():
                        upgrade_cost = tower.get_upgrade_cost()
                        if state.money >= upgrade_cost:
                            # 记录升级前属性
                            old_damage = tower.damage
                            old_range = tower.range
                            
                            state.money -= upgrade_cost
                            tower.upgrade()
                            
                            # 统计更新
                            stats["towers_upgraded"] += 1
                            stats["gold_spent"] += upgrade_cost
                            
                            # 升级成功特效
                            upgrade_effects.append([int(tower.x), int(tower.y), 1.0])
                            
                            # 升级属性变化显示 (2秒后消失)
                            new_damage = tower.damage
                            new_range = tower.range
                            upgrade_info_display.append([
                                int(tower.x), int(tower.y),
                                old_damage, new_damage,
                                old_range, new_range,
                                2.0  # 显示2秒
                            ])
                            
                            # 成就: 首次升级
                            if not achievements["upgrade_tower"]["unlocked"]:
                                achievements["upgrade_tower"]["unlocked"] = True
                                achievement_notify = f"🏆 解锁: {achievements['upgrade_tower']['name']}"
                                achievement_timer = 3.0
                        else:
                            # 金币不足警告
                            no_money_warning = "💰 金币不足！"
                            no_money_timer = 1.5
                # T键切换统计面板
                elif event.key == pygame.K_t:
                    global show_stats
                    show_stats = not show_stats
                # M键切换音效
                elif event.key == pygame.K_m:
                    music_enabled = not music_enabled
                    if music_enabled:
                        print("🔊 音效开启")
                    else:
                        print("🔇 音效关闭")
                # F5键截图
                elif event.key == pygame.K_F5:
                    take_screenshot()
                # ESC键暂停/继续
                elif event.key == pygame.K_ESCAPE:
                    state.paused = not state.paused
                # P键切换选中塔的攻击优先级
                elif event.key == pygame.K_p:
                    if hasattr(state, 'selected_tower') and state.selected_tower:
                        tower = state.selected_tower
                        priorities = ["first", "last", "strong", "weak"]
                        current = priorities.index(tower.priority) if hasattr(tower, 'priority') and tower.priority in priorities else 0
                        tower.priority = priorities[(current + 1) % len(priorities)]
                        print(f"攻击优先级: {tower.priority}")
                # 键盘选择防御塔 (1-3)
                if event.key == pygame.K_1:
                    config['tower_selection'] = '箭塔'
                elif event.key == pygame.K_2:
                    config['tower_selection'] = '炮塔'
                elif event.key == pygame.K_3:
                    config['tower_selection'] = '魔法塔'
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 放置防御塔
                x, y = event.pos
                
                # 检查是否点击了已有塔（选中）
                clicked_tower = None
                for tower in state.towers:
                    dist = ((tower.x - x)**2 + (tower.y - y)**2) ** 0.5
                    if dist < 20:
                        clicked_tower = tower
                        break
                
                if clicked_tower:
                    # 选中塔
                    state.selected_tower = clicked_tower
                else:
                    # 放置防御塔
                    tower_type = config.get('tower_selection', None)
                if tower_type:
                    tower_info = config.get('towers', {}).get(tower_type, {})
                    cost = tower_info.get('cost', 50)
                    if state.money >= cost:
                        # 检查是否与其他塔冲突
                        can_place = True
                        for t in state.towers:
                            if ((t.x - x)**2 + (t.y - y)**2) ** 0.5 < 30:
                                can_place = False
                                break
                        if can_place:
                            # 检测是否在路径上
                            if PATH_RECT.collidepoint(x, y):
                                print("⚠️ 不能在路径上放置防御塔！")
                                no_money_warning = "🚫 不能在路径上！"
                                no_money_timer = 1.5
                            else:
                                # 检测与其他塔的距离（防止重叠）
                                too_close = False
                                for existing in state.towers:
                                    dx = existing.x - x
                                    dy = existing.y - y
                                    if (dx*dx + dy*dy) ** 0.5 < 40:
                                        print("⚠️ 与其他塔太近！")
                                        no_money_warning = "🚫 与其他塔太近！"
                                        no_money_timer = 1.5
                                        too_close = True
                                        break
                                
                                if not too_close:
                                    # 创建防御塔
                                    from src.towers import Tower
                                    color = tower_info.get('color', 'BLUE')
                                    color_map = {'BLUE': (0, 0, 255), 'RED': (255, 0, 0), 'PURPLE': (128, 0, 128), 'CYAN': (0, 255, 255)}
                                    preview_color = color_map.get(color, (0, 0, 255))
                                    
                                    tower = Tower(
                                        tower_type,
                                        tower_info.get('damage', 10),
                                        tower_info.get('range', 2.0),
                                        cost,
                                        tower_info.get('attack_speed', 1.0),
                                        x, y
                                    )
                                    state.towers.append(tower)
                                    state.money -= cost
                                    # 统计更新
                                    stats["towers_built"] += 1
                                    stats["gold_spent"] += cost
                                    # 放置成功特效
                                    place_effects.append([x, y, preview_color, 0.8])
        
        # 更新游戏逻辑
        # 计算游戏时间
        display_time = int(time.time() - game_start_time)
        minutes = display_time // 60
        seconds = display_time % 60
        time_str = f"⏱️ {minutes:02d}:{seconds:02d}"
        
        # 更新连杀计时
        global kill_streak, kill_streak_timer, combo_text
        kill_streak_timer -= effective_dt
        if kill_streak_timer <= 0:
            kill_streak = 0
            combo_text = ""
        
        # 更新金币不足警告计时
        if no_money_timer > 0:
            no_money_timer -= effective_dt
        
        # 更新波次提示计时
        global wave_tip_timer
        if wave_tip_timer > 0:
            wave_tip_timer -= effective_dt
        
        # 生命值检测
        if state.lives <= 3 and not low_life_warning:
            low_life_warning = True
            low_life_timer = 2.0
        elif state.lives > 3:
            low_life_warning = False
        
        # 生命值警告计时减少
        if low_life_timer > 0:
            low_life_timer -= effective_dt * game_speed
            if low_life_timer <= 0:
                low_life_warning = False
        
        # 波次间隔倒计时
        global wave_wait_timer, final_wave_announced
        if wave_wait_timer > 0:
            wave_wait_timer -= effective_dt
            if wave_wait_timer <= 0:
                # 倒计时结束，自动开始下一波
                state.wave_manager.start_wave(state.wave_manager.get_next_wave_index())
                state.wave += 1
                wave_wait_timer = 0
                
                # 检测是否最后一波
                total_waves = len(state.wave_manager.waves)
                if state.wave == total_waves and not final_wave_announced:
                    final_wave_announced = True
                    wave_tip = "⚠️ 最终波！加油！"
                    wave_tip_timer = 3.0
        # 检查波次是否完成，触发倒计时（只在未在倒计时时触发）
        elif state.wave_manager.is_wave_complete() and state.wave_manager.has_more_waves():
            # 波次完成，检测无伤成就
            global wave_no_damage
            if wave_no_damage and not achievements["no_damage_wave"]["unlocked"]:
                achievements["no_damage_wave"]["unlocked"] = True
                achievement_notify = f"🏆 解锁: {achievements['no_damage_wave']['name']}"
                achievement_timer = 3.0
            wave_no_damage = True  # 重置下一波检测
            wave_wait_timer = wave_wait_duration
        
        # 检查胜利条件（所有波次完成且无怪物）
        if not state.wave_manager.has_more_waves() and state.wave_manager.is_wave_complete() and not state.monsters and state.wave > 0:
            if game_complete_time is None:
                game_complete_time = display_time
                # 成就: 速通（3分钟内）
                if display_time < 180 and not achievements["fast_win"]["unlocked"]:
                    achievements["fast_win"]["unlocked"] = True
                    achievement_notify = f"🏆 解锁: {achievements['fast_win']['name']}"
                    achievement_timer = 3.0
        
        # 更新波次系统
        state.wave_manager.update(effective_dt, state)
        
        # 更新怪物位置
        for monster in state.monsters[:]:
            monster.x = int(100 + monster.position * 600)
            if monster.move(effective_dt):
                state.monsters.remove(monster)
                state.lives -= 1
                # 触发屏幕震动
                screen_shake = 10
                if state.lives <= 0:
                    state.game_over = True
                    wave_no_damage = False  # 掉血了
        
        # 怪物击杀检测（子弹击中怪物）
        for projectile in state.projectiles[:]:
            projectile.move(effective_dt)
            mx, my = projectile.x, projectile.y
            # 检测是否击中怪物
            for monster in state.monsters[:]:
                mx_monster = 100 + monster.position * 600
                distance = ((mx - mx_monster) ** 2 + (my - 300) ** 2) ** 0.5
                if distance < 20:  # 击中判定
                    state.projectiles.remove(projectile)
                    monster.health -= projectile.damage
                    # 记录击杀来源塔
                    source_tower = getattr(projectile, 'source_tower', None)
                    if monster.health <= 0:  # 怪物死亡
                        # 增加塔的击杀计数
                        if source_tower and hasattr(source_tower, 'kill_count'):
                            source_tower.kill_count += 1
                        
                        reward = 10  # 金币奖励
                        # 连杀判定
                        kill_streak += 1
                        kill_streak_timer = 3.0
                        bonus = 0
                        if kill_streak >= 3:
                            bonus = kill_streak * 2
                            combo_text = f"🔥 {kill_streak}连杀! +{bonus}"
                        elif kill_streak >= 2:
                            combo_text = f"💥 {kill_streak}连击!"
                        state.money += reward + bonus
                        # 统计更新
                        stats["kills"] += 1
                        stats["damage_dealt"] += projectile.damage
                        stats["gold_earned"] += reward + bonus
                        coin_animations.append([mx, 280, f"+{reward}", 1.0])
                        if bonus > 0:
                            coin_animations.append([mx + 30, 280, f"+{bonus}(连杀)", 1.5])
                        if monster in state.monsters:
                            state.monsters.remove(monster)
                            # 成就: 击杀相关
                            total_kills += 1
                            if not achievements["first_blood"]["unlocked"]:
                                achievements["first_blood"]["unlocked"] = True
                                achievement_notify = f"🏆 解锁: {achievements['first_blood']['name']}"
                                achievement_timer = 3.0
                            if total_kills >= 10 and not achievements["ten_kills"]["unlocked"]:
                                achievements["ten_kills"]["unlocked"] = True
                                achievement_notify = f"🏆 解锁: {achievements['ten_kills']['name']}"
                                achievement_timer = 3.0
                            if total_kills >= 50 and not achievements["fifty_kills"]["unlocked"]:
                                achievements["fifty_kills"]["unlocked"] = True
                                achievement_notify = f"🏆 解锁: {achievements['fifty_kills']['name']}"
                                achievement_timer = 3.0
                    break
        
        # 计算FPS
        fps_counter += 1
        fps_timer += dt
        if fps_timer >= 1.0:
            fps = int(fps_counter / fps_timer)
            fps_counter = 0
            fps_timer = 0
        
        # 绘制游戏画面
        draw_game()
        
        # 暂停时显示详细信息
        if state.paused:
            # 半透明遮罩
            pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 150))
            SCREEN.blit(pause_overlay, (0, 0))
            
            font_title = pygame.font.Font(None, 64)
            title = font_title.render("⏸️ 暂停", True, WHITE)
            SCREEN.blit(title, (SCREEN_WIDTH//2 - 80, 100))
            
            # 显示当前状态
            font_info = pygame.font.Font(None, 28)
            y = 200
            info_lines = [
                f"波次: {state.wave + 1}/10",
                f"金币: {state.money}",
                f"生命: {state.lives}",
                f"防御塔: {len(state.towers)}座",
                f"击杀: {stats['kills']}",
                f"游戏时间: {display_time//60}:{display_time%60:02d}",
            ]
            
            for line in info_lines:
                text = font_info.render(line, True, YELLOW)
                SCREEN.blit(text, (SCREEN_WIDTH//2 - 80, y))
                y += 35
            
            # 操作提示
            font_hint = pygame.font.Font(None, 24)
            hints = [
                "ESC - 继续",
                "S - 保存",
                "L - 读取",
            ]
            y += 20
            for hint in hints:
                h_text = font_hint.render(hint, True, GRAY)
                SCREEN.blit(h_text, (SCREEN_WIDTH//2 - 50, y))
                y += 25
            
            pygame.display.flip()
            continue
    
    pygame.quit()

if __name__ == "__main__":
    main()