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

# 路径区域(怪物行走路线)
PATH_RECT = pygame.Rect(100, 280, 600, 40)  # 路径矩形区域

# 游戏统计
stats = {
    "kills": 0,
    "damage_dealt": 0,
    "towers_built": 0,
    "towers_upgraded": 0,
    "gold_spent": 0,
    "gold_earned": 0,
    "waves_completed": 0,
}

# 游戏结束报告函数
def draw_end_report(screen, won, stats, time_seconds):
    """绘制游戏结束统计报告"""
    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # 标题
    font_title = pygame.font.Font(None, 60)
    if won:
        title = font_title.render("🎉 胜利!", True, GOLD)
    else:
        title = font_title.render("💀 失败", True, RED)
    screen.blit(title, (SCREEN_WIDTH//2 - 80, 80))
    
    # 统计内容
    font_info = pygame.font.Font(None, 32)
    y = 180
    lines = [
        f"游戏时间: {time_seconds//60}:{time_seconds%60:02d}",
        f"存活波次: {stats.get('waves_completed', 0)}/10",
        f"总击杀: {stats.get('kills', 0)}",
        f"建造塔数: {stats.get('towers_built', 0)}",
        f"升级次数: {stats.get('towers_upgraded', 0)}",
        f"花费金币: {stats.get('gold_spent', 0)}",
        f"获得金币: {stats.get('gold_earned', 0)}",
        f"总伤害: {stats.get('damage_dealt', 0)}",
    ]
    
    for line in lines:
        surf = font_info.render(line, True, WHITE)
        screen.blit(surf, (SCREEN_WIDTH//2 - 120, y))
        y += 35
    
    # 评价
    font_eval = pygame.font.Font(None, 40)
    kills = stats.get('kills', 0)
    if won and kills >= 50:
        eval_text = "⭐⭐⭐ 完美通关! ⭐⭐⭐"
    elif won and kills >= 30:
        eval_text = "⭐⭐ 优秀! ⭐⭐"
    elif won:
        eval_text = "⭐ 通过! ⭐"
    else:
        eval_text = "再接再厉!"
    
    eval_surf = font_eval.render(eval_text, True, YELLOW)
    screen.blit(eval_surf, (SCREEN_WIDTH//2 - 100, y + 30))

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

# ==================== 成就徽章UI ====================
def draw_achievement_badges():
    """绘制已解锁成就徽章（右上角）"""
    badge_x = SCREEN_WIDTH - 30
    badge_y = 120
    
    unlocked = [k for k, v in achievements.items() if v.get("unlocked")]
    
    for i, achievement_key in enumerate(unlocked[:5]):  # 最多显示5个
        badge_y = 120 + i * 35
        
        # 徽章背景（金色圆形）
        pygame.draw.circle(SCREEN, GOLD, (badge_x, badge_y), 15)
        pygame.draw.circle(SCREEN, (200, 150, 0), (badge_x, badge_y), 12)
        
        # 徽章图标（使用成就key的首字母作为图标）
        icon_map = {
            "first_blood": "🎯",
            "ten_kills": "💀",
            "fifty_kills": "💀",
            "upgrade_tower": "⬆️",
            "sell_tower": "💰",
            "no_damage_wave": "🛡️",
            "fast_win": "⚡",
        }
        icon = icon_map.get(achievement_key, "⭐")
        font_icon = pygame.font.Font(None, 20)
        icon_surf = font_icon.render(icon, True, WHITE)
        SCREEN.blit(icon_surf, (badge_x - 8, badge_y - 10))
        
        # 成就名称（左侧显示）
        name = achievements[achievement_key].get("name", achievement_key)
        font_name = pygame.font.Font(None, 18)
        name_surf = font_name.render(name[:4], True, WHITE)
        SCREEN.blit(name_surf, (badge_x - 50, badge_y - 5))

# 波次无伤检测
wave_no_damage = True

# 游戏时间
game_start_time = time.time()

# 难度设置
DIFFICULTY_EASY = 0.7
DIFFICULTY_NORMAL = 1.0
DIFFICULTY_HARD = 1.5
game_difficulty = DIFFICULTY_NORMAL  # 默认普通难度
difficulty_selected = False  # 难度是否已选择

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

# 难度选择屏幕
def draw_difficulty_screen():
    """绘制难度选择界面"""
    SCREEN.fill((20, 20, 40))

    font_title = pygame.font.Font(None, 60)
    title = font_title.render("选择难度", True, YELLOW)
    SCREEN.blit(title, (SCREEN_WIDTH//2 - 80, 100))

    difficulties = [
        ("简单 - 怪物血量x0.7", (100, 200), (100, 200, 100)),
        ("普通 - 怪物血量x1.0", (100, 280), (100, 100, 200)),
        ("困难 - 怪物血量x1.5", (100, 360), (200, 100, 100)),
    ]

    for text, pos, color in difficulties:
        font = pygame.font.Font(None, 36)
        surf = font.render(text, True, color)
        SCREEN.blit(surf, pos)

    font_tip = pygame.font.Font(None, 24)
    tip = font_tip.render("按 1/2/3 选择难度", True, GRAY)
    SCREEN.blit(tip, (SCREEN_WIDTH//2 - 80, 450))

    # 显示当前选中的难度
    if game_difficulty == DIFFICULTY_EASY:
        selected_text = "已选择: 简单"
        selected_color = (100, 200, 100)
    elif game_difficulty == DIFFICULTY_NORMAL:
        selected_text = "已选择: 普通"
        selected_color = (100, 100, 200)
    else:
        selected_text = "已选择: 困难"
        selected_color = (200, 100, 100)

    font_selected = pygame.font.Font(None, 28)
    selected_surf = font_selected.render(selected_text, True, selected_color)
    SCREEN.blit(selected_surf, (SCREEN_WIDTH//2 - 60, 500))

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
GOLD = (255, 215, 0)  # 金色用于胜利标题

# ==================== 随机事件系统 ====================
random_events = {
    "gold_rain": {"name": "💰 金币雨", "duration": 10, "active": False, "timer": 0, "color": (255, 215, 0)},
    "double_damage": {"name": "⚔️ 双倍伤害", "duration": 15, "active": False, "timer": 0, "color": (255, 100, 100)},
    "slow_all": {"name": "❄️ 全屏减速", "duration": 12, "active": False, "timer": 0, "color": (100, 200, 255)},
}
# 随机事件上次触发时间
last_event_check = 0
EVENT_CHECK_INTERVAL = 30000  # 30秒检查一次
EVENT_TRIGGER_CHANCE = 0.10  # 10%触发几率
SKY_BLUE = tuple(config['colors']['sky_blue'])
GRASS_DARK = tuple(config['colors']['grass_dark'])
GRASS_LIGHT = tuple(config['colors']['grass_light'])
PATH_BROWN = tuple(config['colors']['path_brown'])
PATH_LIGHT_BROWN = tuple(config['colors']['path_light'])

pygame.init()

# 尝试加载音效(可选)
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

# 暴击特效列表
crit_effects = []  # [(x, y, timer)]

# 金币动画列表
coin_animations = []  # [(x, y, amount, timer), ...]

# 连杀系统
kill_streak = 0  # 当前连杀数
kill_streak_timer = 0  # 连杀计时
combo_text = ""  # 连杀文字

# 连杀特效列表 [(x, y, text, color, timer)]
combo_texts = []

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

# 显示塔图鉴
show_tower_book = False

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
        global final_wave_announced, game_complete_time, difficulty_selected
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
        difficulty_selected = False  # 重置难度选择状态

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
    # 这里应该包含所有游戏对象的绘制,但为了演示,我会简化
    shake_x, shake_y = screen_shake_offset

    # 绘制怪物行走路线
    path_color = (60, 60, 60)  # 深灰色路线
    path_width = 40
    pygame.draw.rect(SCREEN, path_color, (100, 300 - path_width//2, 600, path_width))

    # 路线装饰虚线
    for i in range(10):
        x = 100 + i * 60 + 30
        pygame.draw.line(SCREEN, (80, 80, 80), (x, 300 - 15), (x, 300 + 15), 2)

    # 绘制塔基座格子(8x4网格)
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

    # 终点(萝卜位置)
    pygame.draw.circle(SCREEN, (255, 140, 0), (700 + shake_x, 300 + shake_y), 28)  # 深橙色外圈
    pygame.draw.circle(SCREEN, ORANGE, (700 + shake_x, 300 + shake_y), 22)  # 橙色主体
    pygame.draw.circle(SCREEN, (255, 200, 100), (700 + shake_x, 300 + shake_y), 14)  # 浅色高光

    # 绘制怪物(带震动偏移)- 根据怪物类型显示不同形状
    for monster in state.monsters:
        x = int(100 + monster.position * 600)
        y = 300
        
        # 怪物生成动画（从0缩放到1）
        spawn_scale = getattr(monster, 'spawn_scale', 1.0)
        if spawn_scale < 1.0:
            # 还在生成中，绘制缩放的怪物并跳过血条
            radius = int(14 * spawn_scale)
            pygame.draw.circle(SCREEN, (50, 100, 200), (x + shake_x, y + shake_y), radius)
            continue

        # 怪物阴影(增加立体感)- 在本体绘制前显示
        shadow_rect = pygame.Rect(int(x) - 14, int(y) + 8, 28, 12)
        pygame.draw.ellipse(SCREEN, (25, 25, 25), (shadow_rect.x + shake_x, shadow_rect.y + shake_y, shadow_rect.width, shadow_rect.height))

        # 根据怪物类型绘制不同形状
        monster_type = getattr(monster, 'type', 'normal')

        if monster_type == 'boss':
            # Boss: 大红圆,带光环
            pygame.draw.circle(SCREEN, (200, 0, 0), (x + shake_x, y + shake_y), 22)
            pygame.draw.circle(SCREEN, (255, 50, 50), (x + shake_x, y + shake_y), 18)
            # 光环
            pygame.draw.circle(SCREEN, (255, 0, 0), (x + shake_x, y + shake_y), 26, 2)
        elif monster_type == 'fast':
            # 快速怪: 绿色小三角形
            points = [(x + shake_x, y - 14 + shake_y),
                      (x - 10 + shake_x, y + 10 + shake_y),
                      (x + 10 + shake_x, y + 10 + shake_y)]
            pygame.draw.polygon(SCREEN, (50, 200, 50), points)
        elif monster_type == 'armor':
            # 装甲怪: 灰色方形
            pygame.draw.rect(SCREEN, (100, 100, 100),
                           (x - 12 + shake_x, y - 12 + shake_y, 24, 24))
            pygame.draw.rect(SCREEN, (150, 150, 150),
                           (x - 8 + shake_x, y - 8 + shake_y, 16, 16))
        else:
            # 普通怪: 蓝色圆形
            pygame.draw.circle(SCREEN, (50, 100, 200), (x + shake_x, y + shake_y), 14)

        # 绘制血条背景(带边框 - 更高更显眼)
        pygame.draw.rect(SCREEN, (255, 255, 255), (x - 18 + shake_x, y - 30 + shake_y, 38, 14), 2)  # 白色外边框
        pygame.draw.rect(SCREEN, (60, 0, 0), (x - 16 + shake_x, y - 28 + shake_y, 34, 10))

        # 绘制血条
        health_ratio = monster.health / monster.max_health
        health_width = max(0, int(32 * health_ratio))
        # 颜色渐变
        if health_ratio > 0.6:
            health_color = (50, 200, 50)
        elif health_ratio > 0.3:
            health_color = (255, 200, 0)
        else:
            health_color = (220, 50, 50)
        pygame.draw.rect(SCREEN, health_color, (x - 16 + shake_x, y - 28 + shake_y, health_width, 10))

        # 详细血量显示(按H切换)
        if show_health_detail:
            font_health = pygame.font.Font(None, 18)
            health_text = font_health.render(f"{int(monster.health)}/{int(monster.max_health)}", True, WHITE)
            SCREEN.blit(health_text, (x - 20 + shake_x, y - 42 + shake_y))

    # 检测Boss并绘制特殊血条
    global boss_bar_drawn
    for monster in state.monsters:
        if hasattr(monster, 'is_boss') and monster.is_boss:
            # 绘制Boss血条(屏幕顶部)
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

    # 绘制防御塔(不同形状)
    for tower in state.towers:
        tx, ty = int(tower.x), int(tower.y)

        # 判断塔是否被选中
        is_selected = (tower == state.selected_tower)

        # 选中时塔基座发光效果
        if is_selected:
            # 外发光效果(多层半透明圆)
            glow_radius = 25
            for i in range(3):
                alpha = 30 - i * 10
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                color = (*YELLOW, alpha)
                pygame.draw.circle(glow_surf, color, (glow_radius, glow_radius), glow_radius - i * 5)
                SCREEN.blit(glow_surf, (int(tower.x) - glow_radius + shake_x, int(tower.y) - glow_radius + shake_y))

            # 金色实线边框
            pygame.draw.circle(SCREEN, YELLOW, (int(tower.x) + shake_x, int(tower.y) + shake_y), 20, 3)

        # 塔的颜色(被选中时高亮)
        tower_color = YELLOW if is_selected else BLUE

        # 选中时显示攻击范围(圆形)- 使用塔类型颜色
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
            
            # 显示组合状态（同类型相邻加成）
            synergy = tower.check_synergy(state.towers)
            if synergy > 1.0:
                synergy_text = f"组合: +{int((synergy-1)*100)}%"
                synergy_color = GOLD
            else:
                synergy_text = "组合: 无"
                synergy_color = GRAY
            
            font_synergy = pygame.font.Font(None, 20)
            synergy_surf = font_synergy.render(synergy_text, True, synergy_color)
            SCREEN.blit(synergy_surf, (int(tower.x) + 20 + shake_x, int(tower.y) + 5 + shake_y))

            # 升级路线预览（选中塔时）
            if is_selected and hasattr(tower, 'level') and tower.level < 3:
                # 计算升级后的属性
                next_level = tower.level + 1
                next_damage = int(tower.damage * 1.3)
                next_range = int(tower.range * 1.1 * 50)
                next_cost = tower.get_upgrade_cost()
                
                # 显示预览
                font_preview = pygame.font.Font(None, 22)
                preview_y = int(tower.y) + 30
                
                # 箭头
                arrow = font_preview.render("↓ 升级预览", True, YELLOW)
                SCREEN.blit(arrow, (int(tower.x) - 40, preview_y + shake_y))
                preview_y += 18
                
                # 伤害
                dmg_text = font_preview.render(f"伤害: {int(tower.damage)} → {next_damage}", True, GREEN)
                SCREEN.blit(dmg_text, (int(tower.x) - 45, preview_y + shake_y))
                preview_y += 16
                
                # 射程
                current_range_px = int(tower.range * 50)
                rng_text = font_preview.render(f"射程: {current_range_px} → {next_range}", True, CYAN)
                SCREEN.blit(rng_text, (int(tower.x) - 45, preview_y + shake_y))
                preview_y += 16
                
                # 费用
                cost_text = font_preview.render(f"费用: {next_cost}", True, GREEN if state.money >= next_cost else RED)
                SCREEN.blit(cost_text, (int(tower.x) - 25, preview_y + shake_y))

        # 绘制防御塔(不同形状)
        if "箭" in tower.name:
            # 箭塔:三角形
            points = [(tx, ty - 15), (tx - 12, ty + 10), (tx + 12, ty + 10)]
            pygame.draw.polygon(SCREEN, tower_color, points)
        elif "炮" in tower.name:
            # 炮塔:正方形
            pygame.draw.rect(SCREEN, tower_color, (tx - 12, ty - 12, 24, 24))
        elif "魔法" in tower.name:
            # 魔法塔:六边形(用圆模拟)
            pygame.draw.circle(SCREEN, tower_color, (tx, ty), 14)
            pygame.draw.circle(SCREEN, (200, 100, 255), (tx, ty), 8)
        elif "减速" in tower.name:
            # 减速塔:菱形
            points = [(tx, ty - 15), (tx + 15, ty), (tx, ty + 15), (tx - 15, ty)]
            pygame.draw.polygon(SCREEN, tower_color, points)
        else:
            # 默认:圆形
            pygame.draw.circle(SCREEN, tower_color, (tx, ty), 15)
        
        # 品质边框显示
        if hasattr(tower, 'quality'):
            if tower.quality == "epic":
                border_color = (255, 215, 0)  # 金色
                border_width = 3
            elif tower.quality == "rare":
                border_color = (0, 191, 255)  # 蓝色
                border_width = 2
            else:
                border_color = WHITE
                border_width = 1
            pygame.draw.circle(SCREEN, border_color, (tx, ty), 17, border_width)

    # 绘制防御塔攻击线(锁定目标)
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

            # 目标锁定线(实线)
            pygame.draw.line(SCREEN, color, (int(tower.x) + shake_x, int(tower.y) + shake_y), (tx + shake_x, ty + shake_y), 2)

            # 目标点高亮(红色小点)
            pygame.draw.circle(SCREEN, (255, 50, 50), (tx + shake_x, ty + shake_y), 5)
            pygame.draw.circle(SCREEN, WHITE, (tx + shake_x, ty + shake_y), 3)

            # 目标锁定框特效
            import math
            time_now = pygame.time.get_ticks() / 200
            size = 20 + math.sin(time_now) * 3

            # 四角锁定框(无旋转)
            corners = [
                (tx + shake_x - size, ty + shake_y - size),
                (tx + shake_x + size, ty + shake_y - size),
                (tx + shake_x + size, ty + shake_y + size),
                (tx + shake_x - size, ty + shake_y + size)
            ]

            # 绘制四条边
            pygame.draw.line(SCREEN, (255, 0, 0), corners[0], corners[1], 2)  # 上边
            pygame.draw.line(SCREEN, (255, 0, 0), corners[2], corners[3], 2)  # 下边
            pygame.draw.line(SCREEN, (255, 0, 0), corners[0], corners[3], 2)  # 左边
            pygame.draw.line(SCREEN, (255, 0, 0), corners[1], corners[2], 2)  # 右边

            # 中心红点
            pygame.draw.circle(SCREEN, (255, 0, 0), (tx + shake_x, ty + shake_y), 3)

    # 绘制连杀提示(顶部中央)
    if combo_text and kill_streak_timer > 0:
        font_combo = pygame.font.Font(None, 36)
        combo_surf = font_combo.render(combo_text, True, (255, 100, 0))
        SCREEN.blit(combo_surf, (SCREEN_WIDTH//2 - 60, 150))

    # 绘制连杀浮动特效(在怪物死亡位置)
    for ct in combo_texts[:]:
        cx, cy, ctext, ccolor, ctimer = ct
        ctimer -= dt * game_speed
        cy -= 30 * dt * game_speed  # 上浮

        font_ct = pygame.font.Font(None, 28)
        ct_surf = font_ct.render(ctext, True, ccolor)
        # 文字描边效果
        outline_surf = font_ct.render(ctext, True, BLACK)
        SCREEN.blit(outline_surf, (int(cx) - 28 + shake_x + 1, int(cy) + shake_y + 1))
        SCREEN.blit(ct_surf, (int(cx) - 28 + shake_x, int(cy) + shake_y))

        # 更新计时器
        ct[4] = ctimer
        if ctimer <= 0:
            combo_texts.remove(ct)

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

    # 塔放置预览增强(包含范围)
    if hasattr(state, "mouse_preview") and state.mouse_preview:
        mx, my, tower_type = state.mouse_preview

        # 获取塔的范围
        tower_info = config.get("towers", {}).get(tower_type, {})
        preview_range = tower_info.get("range", 3) * 50

        # 范围填充(半透明)
        range_surf = pygame.Surface((preview_range*2, preview_range*2), pygame.SRCALPHA)
        color = BLUE if "箭" in tower_type else (RED if "炮" in tower_type else PURPLE)
        if "减速" in tower_type:
            color = CYAN
        pygame.draw.circle(range_surf, (*color, 30), (preview_range, preview_range), preview_range)
        SCREEN.blit(range_surf, (mx - preview_range, my - preview_range))

        # 范围边框
        pygame.draw.circle(SCREEN, color, (mx, my), preview_range, 2)

        # 中心塔形状预览
        points = [(mx, my - 12), (mx - 10, my + 8), (mx + 10, my + 8)]
        pygame.draw.polygon(SCREEN, color, points)

    # 显示游戏时间(右上角)
    font_time = pygame.font.Font(None, 32)
    time_text = font_time.render(time_str, True, WHITE)
    SCREEN.blit(time_text, (SCREEN_WIDTH - 80, 50))

    # 显示FPS
    font_fps = pygame.font.Font(None, 24)
    fps_text = font_fps.render(f"FPS: {fps}", True, (100, 255, 100))
    SCREEN.blit(fps_text, (10, 10))

    # 绘制波次提示(最终波提示)
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

    # 波次进度条(波次进行时显示)
    if state.wave_manager.is_waving:
        # 计算波次进度
        wave_progress = 0
        if hasattr(state.wave_manager, 'current_wave_data'):
            total = len(state.wave_manager.current_wave_data.get('monsters', [1]))
            current = total - len(state.monsters)
            wave_progress = current / total if total > 0 else 0

        # 绘制进度条背景
        bar_width = 200
        bar_height = 10
        bar_x = SCREEN_WIDTH//2 - bar_width//2
        bar_y = 45

        pygame.draw.rect(SCREEN, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(SCREEN, (100, 100, 100), (bar_x + 1, bar_y + 1, bar_width - 2, bar_height - 2))

        # 绘制进度
        progress_width = int((bar_width - 2) * wave_progress)
        pygame.draw.rect(SCREEN, GREEN, (bar_x + 1, bar_y + 1, progress_width, bar_height - 2))

    # 成就通知
    global achievement_timer
    if achievement_timer > 0:
        achievement_timer -= dt * game_speed
        font_ach = pygame.font.Font(None, 32)
        ach_text = font_ach.render(achievement_notify, True, YELLOW)
        SCREEN.blit(ach_text, (SCREEN_WIDTH//2 - 100, 180))

    # ==================== 随机事件UI显示 ====================
    event_y = 80
    for event_key, event_data in random_events.items():
        if event_data["active"]:
            font_event = pygame.font.Font(None, 28)
            # 显示事件名称和剩余时间
            timer_text = f"{event_data['name']} ({event_data['timer']:.1f}s)"
            event_text = font_event.render(timer_text, True, event_data["color"])
            SCREEN.blit(event_text, (SCREEN_WIDTH - 200, event_y))
            event_y += 25

    # 生命值不足警告
    if low_life_warning and low_life_timer > 0:
        font_warn = pygame.font.Font(None, 48)
        warn_text = font_warn.render("❤️ 生命值告急!", True, RED)
        # 闪烁效果
        if int(low_life_timer * 5) % 2 == 0:
            SCREEN.blit(warn_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 100))

    # 绘制胜利画面
    if game_complete_time is not None:
        stats['waves_completed'] = state.wave
        draw_end_report(SCREEN, True, stats, game_complete_time)
    
    # 绘制失败画面
    if state.game_over:
        stats['waves_completed'] = state.wave - 1 if state.wave > 0 else 0
        draw_end_report(SCREEN, False, stats, display_time)

    # 底部技能按钮面板
    skill_bar_y = SCREEN_HEIGHT - 50

    # 技能按钮
    skills = [
        ("Q", "减速技能", CYAN),
        ("W", "冰冻技能", BLUE),
        ("E", "群攻技能", RED),
    ]

    for i, (key, name, color) in enumerate(skills):
        bx = 150 + i * 100
        by = skill_bar_y
        
        # 按钮背景
        pygame.draw.rect(SCREEN, (40, 40, 60), (bx, by, 80, 35), border_radius=5)
        # 边框
        pygame.draw.rect(SCREEN, color, (bx, by, 80, 35), 2, border_radius=5)
        
        # 文字
        font_skill = pygame.font.Font(None, 28)
        key_surf = font_skill.render(f"{key}: {name}", True, color)
        SCREEN.blit(key_surf, (bx + 5, by + 8))

    # 提示
    font_tip = pygame.font.Font(None, 20)
    tip_surf = font_tip.render("快捷技能", True, GRAY)
    SCREEN.blit(tip_surf, (80, skill_bar_y + 10))

    # 底部操作提示
    font_hint = pygame.font.Font(None, 24)
    hint_text = f"Tab:速度 | 1-3:选塔 | U:升级 | H:血量 | T:统计 | M:音效 | 点击:放置  金币:{state.money}  生命:{state.lives}  波次:{state.wave}"
    hint_surf = font_hint.render(hint_text, True, GRAY)
    SCREEN.blit(hint_surf, (10, SCREEN_HEIGHT - 30))

    # 绘制升级特效
    for ef in upgrade_effects[:]:
        ef[2] -= dt * game_speed
        ux, uy, timer = ef
        # 扩散光环
        radius = int((1.0 - timer) * 60)
        if radius > 0:
            alpha = int(timer * 150)
            eff_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(eff_surf, (255, 215, 0, alpha), (radius, radius), radius)
            SCREEN.blit(eff_surf, (ux - radius + shake_x, uy - radius + shake_y))
        # 向上飘的星星
        for i in range(3):
            star_offset = (1.0 - timer) * 40 + i * 10
            star_y = uy - star_offset
            star_x = ux + math.sin(star_offset) * 20
            pygame.draw.circle(SCREEN, YELLOW, (int(star_x) + shake_x, int(star_y) + shake_y), 3)
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

    # 绘制暴击特效
    for ce in crit_effects[:]:
        ce[2] -= dt * game_speed
        cx, cy, timer = ce
        
        # 暴击文字
        font_crit = pygame.font.Font(None, 40)
        crit_text = font_crit.render("暴击!", True, (255, 0, 0))
        SCREEN.blit(crit_text, (int(cx) - 30 + shake_x, int(cy) - 30 + shake_y))
        
        # 红色星星飞散
        for i in range(5):
            angle = i * 72
            rad = angle * 3.14159 / 180
            dist = (1.0 - timer) * 30
            px = int(cx + dist * math.cos(rad))
            py = int(cy - 30 + dist * math.sin(rad))
            pygame.draw.circle(SCREEN, RED, (px + shake_x, py + shake_y), 3)
        
        if timer <= 0:
            crit_effects.remove(ce)

    # 波次倒计时大字(5秒倒计时)
    global wave_wait_timer
    if wave_wait_timer > 0:
        countdown = int(wave_wait_timer) + 1
        if countdown > 0 and countdown <= 5:
            # 大字倒计时
            font_big = pygame.font.Font(None, 120)
            countdown_text = str(countdown)

            # 闪烁效果
            if int(wave_wait_timer * 4) % 2 == 0:
                text_color = RED
            else:
                text_color = YELLOW

            text_surf = font_big.render(countdown_text, True, text_color)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

            # 黑色描边
            for offset in [(-3,-3), (-3,3), (3,-3), (3,3), (0,-3), (0,3), (-3,0), (3,0)]:
                outline_surf = font_big.render(countdown_text, True, BLACK)
                SCREEN.blit(outline_surf, (text_rect.x + offset[0], text_rect.y + offset[1]))

            SCREEN.blit(text_surf, text_rect)

            # "下一波即将来临" 提示
            font_tip = pygame.font.Font(None, 36)
            tip_surf = font_tip.render("下一波即将来临!", True, WHITE)
            tip_rect = tip_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            SCREEN.blit(tip_surf, tip_rect)

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

    # 绘制成就徽章（右上角）
    draw_achievement_badges()

    # 绘制塔图鉴
    if show_tower_book:
        draw_tower_book()

# 塔图鉴
def draw_tower_book():
    """绘制塔图鉴界面"""
    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    SCREEN.blit(overlay, (0, 0))
    
    # 标题
    font_title = pygame.font.Font(None, 50)
    title = font_title.render("📖 塔图鉴", True, GOLD)
    SCREEN.blit(title, (SCREEN_WIDTH//2 - 60, 50))
    
    # 塔类型信息
    towers_info = [
        ("箭塔", "远程单体", "蓝色三角形", "射速快"),
        ("炮塔", "范围伤害", "红色正方形", "伤害高"),
        ("魔法塔", "高伤害", "紫色菱形", "进阶塔"),
        ("减速塔", "减速敌人", "青色菱形", "辅助塔"),
    ]
    
    font_info = pygame.font.Font(None, 28)
    for i, (name, type_, shape, feature) in enumerate(towers_info):
        y = 130 + i * 80
        
        # 塔形状示例
        cx, cy = 150, y + 20
        if "箭" in name:
            points = [(cx, cy - 15), (cx - 12, cy + 10), (cx + 12, cy + 10)]
            pygame.draw.polygon(SCREEN, BLUE, points)
        elif "炮" in name:
            pygame.draw.rect(SCREEN, RED, (cx - 12, cy - 12, 24, 24))
        elif "魔法" in name:
            points = [(cx, cy - 15), (cx + 12, cy), (cx, cy + 15), (cx - 12, cy)]
            pygame.draw.polygon(SCREEN, PURPLE, points)
        elif "减速" in name:
            points = [(cx, cy - 15), (cx + 15, cy), (cx, cy + 15), (cx - 15, cy)]
            pygame.draw.polygon(SCREEN, CYAN, points)
        
        # 文字
        name_surf = font_info.render(f"{name} - {type_}", True, WHITE)
        SCREEN.blit(name_surf, (200, y))
        
        detail_surf = font_info.render(f"形状: {shape} | 特点: {feature}", True, GRAY)
        SCREEN.blit(detail_surf, (200, y + 30))
    
    # 关闭提示
    font_tip = pygame.font.Font(None, 24)
    tip = font_tip.render("按 I 键关闭图鉴", True, YELLOW)
    SCREEN.blit(tip, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT - 50))

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
                # 难度选择(游戏开始前)
                if not difficulty_selected:
                    if event.key == pygame.K_1:
                        game_difficulty = DIFFICULTY_EASY
                    elif event.key == pygame.K_2:
                        game_difficulty = DIFFICULTY_NORMAL
                    elif event.key == pygame.K_3:
                        game_difficulty = DIFFICULTY_HARD
                    elif event.key == pygame.K_SPACE:
                        difficulty_selected = True

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
                            print("⬆️ 升级成功")

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
                            no_money_warning = "💰 金币不足!"
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
                # Q/W/E技能按键
                elif event.key == pygame.K_q:
                    # 减速技能
                    print("❄️ 减速技能激活!")
                elif event.key == pygame.K_w:
                    # 冰冻技能
                    print("🧊 冰冻技能激活!")
                elif event.key == pygame.K_e:
                    # 群攻技能
                    print("💥 群攻技能激活!")
                # I键打开/关闭塔图鉴
                elif event.key == pygame.K_i:
                    global show_tower_book
                    show_tower_book = not show_tower_book

            elif event.type == pygame.MOUSEMOTION:
                # 鼠标移动时设置预览位置
                x, y = event.pos
                tower_type = config.get('tower_selection', None)
                if tower_type:
                    state.mouse_preview = (x, y, tower_type)
                else:
                    state.mouse_preview = None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 放置防御塔
                x, y = event.pos

                # 检查是否点击了已有塔(选中)
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
                                print("⚠️ 无法放置")
                                no_money_warning = "🚫 不能在路径上!"
                                no_money_timer = 1.5
                            else:
                                # 检测与其他塔的距离(防止重叠)
                                too_close = False
                                for existing in state.towers:
                                    dx = existing.x - x
                                    dy = existing.y - y
                                    if (dx*dx + dy*dy) ** 0.5 < 40:
                                        print("⚠️ 无法放置")
                                        no_money_warning = "🚫 与其他塔太近!"
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
                                    print("🔔 放置成功")

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
                # 倒计时结束,自动开始下一波
                state.wave_manager.start_wave(state.wave_manager.get_next_wave_index())
                state.wave += 1
                wave_wait_timer = 0
                print("🌊 波次开始!")

                # 检测是否最后一波
                total_waves = len(state.wave_manager.waves)
                if state.wave == total_waves and not final_wave_announced:
                    final_wave_announced = True
                    wave_tip = "⚠️ 最终波!加油!"
                    wave_tip_timer = 3.0
        # 检查波次是否完成,触发倒计时(只在未在倒计时时触发)
        elif state.wave_manager.is_wave_complete() and state.wave_manager.has_more_waves():
            # 波次完成,检测无伤成就
            global wave_no_damage
            if wave_no_damage and not achievements["no_damage_wave"]["unlocked"]:
                achievements["no_damage_wave"]["unlocked"] = True
                achievement_notify = f"🏆 解锁: {achievements['no_damage_wave']['name']}"
                achievement_timer = 3.0
            wave_no_damage = True  # 重置下一波检测
            wave_wait_timer = wave_wait_duration

        # 检查胜利条件(所有波次完成且无怪物)
        if not state.wave_manager.has_more_waves() and state.wave_manager.is_wave_complete() and not state.monsters and state.wave > 0:
            if game_complete_time is None:
                game_complete_time = display_time
                # 成就: 速通(3分钟内)
                if display_time < 180 and not achievements["fast_win"]["unlocked"]:
                    achievements["fast_win"]["unlocked"] = True
                    achievement_notify = f"🏆 解锁: {achievements['fast_win']['name']}"
                    achievement_timer = 3.0

        # 更新波次系统
        state.wave_manager.update(effective_dt, state, game_difficulty)

        # ==================== 随机事件系统 ====================
        current_time = pygame.time.get_ticks()
        
        # 事件持续时间更新
        for event_key, event_data in random_events.items():
            if event_data["active"]:
                event_data["timer"] -= effective_dt
                if event_data["timer"] <= 0:
                    event_data["active"] = False
                    event_data["timer"] = 0
                    print(f"⏰ 随机事件结束: {event_data['name']}")
        
        # 随机事件触发（每30秒10%几率）
        if current_time - last_event_check >= EVENT_CHECK_INTERVAL:
            last_event_check = current_time
            # 只有当没有活跃事件时才触发
            if not any(e["active"] for e in random_events.values()):
                if random.random() < EVENT_TRIGGER_CHANCE:
                    event_key = random.choice(list(random_events.keys()))
                    random_events[event_key]["active"] = True
                    random_events[event_key]["timer"] = random_events[event_key]["duration"]
                    print(f"🎲 随机事件触发: {random_events[event_key]['name']}!")

        # 更新怪物位置
        for monster in state.monsters[:]:
            # 随机事件：全屏减速
            if random_events["slow_all"]["active"]:
                monster.apply_slow(0.5, 0.1)  # 50%速度
            monster.update(effective_dt)  # 更新生成动画和减速状态
            monster.x = int(100 + monster.position * 600)
            if monster.move(effective_dt):
                state.monsters.remove(monster)
                state.lives -= 1
                # 触发屏幕震动
                screen_shake = 10
                if state.lives <= 0:
                    state.game_over = True
                    wave_no_damage = False  # 掉血了

        # 塔攻击逻辑 - 添加组合系统
        for tower in state.towers:
            tower.attack(state.monsters, state.projectiles, state.towers)

        # 怪物击杀检测(子弹击中怪物)
        for projectile in state.projectiles[:]:
            projectile.move(effective_dt)
            mx, my = projectile.x, projectile.y
            # 检测是否击中怪物
            for monster in state.monsters[:]:
                mx_monster = 100 + monster.position * 600
                distance = ((mx - mx_monster) ** 2 + (my - 300) ** 2) ** 0.5
                if distance < 20:  # 击中判定
                    state.projectiles.remove(projectile)
                    # 随机事件：双倍伤害
                    damage_mult = 2.0 if random_events["double_damage"]["active"] else 1.0
                    actual_damage = int(projectile.damage * damage_mult)
                    monster.health -= actual_damage
                    # 记录击杀来源塔
                    source_tower = getattr(projectile, 'source_tower', None)
                    if monster.health <= 0:  # 怪物死亡
                        # 增加塔的击杀计数
                        if source_tower and hasattr(source_tower, 'kill_count'):
                            source_tower.kill_count += 1

                        reward = 10  # 金币奖励
                        
                        # 随机事件：金币雨 - 击杀额外金币
                        if random_events["gold_rain"]["active"]:
                            reward += 5
                        
                        # 暴击检测（10%几率）
                        if random.random() < 0.1:
                            crit_effects.append([int(mx), int(my), 1.0])
                            reward *= 2  # 暴击金币翻倍
                            print("💥 暴击!")
                        
                        # 连杀判定
                        kill_streak += 1
                        kill_streak_timer = 3.0
                        bonus = 0
                        if kill_streak >= 3:
                            bonus = kill_streak * 2
                            combo_text = f"🔥 {kill_streak}连杀! +{bonus}"
                            # 添加浮动连杀特效文字
                            combo_texts.append([mx, my - 20, f"{kill_streak}连杀!", (255, 215, 0), 1.5])
                        elif kill_streak >= 5:
                            # 暴击特效
                            combo_texts.append([mx, my - 20, f"暴击!{kill_streak}X", (255, 0, 0), 2.0])
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
        if not difficulty_selected:
            draw_difficulty_screen()
        else:
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