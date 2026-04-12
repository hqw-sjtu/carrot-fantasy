import sys
import os
import pygame
import random
import time
import math
import datetime
sys.path.append(os.path.dirname(__file__))
from daily_challenge import daily_challenge, CHALLENGES, get_today_challenge, check_challenge_completion, draw_daily_challenge_panel
from celebration_effects import CelebrationEffect, StageCompleteEffect
from extra_effects import UpgradeBeamEffect, TowerSelectionPulse, TrailFadeEffect, BlackHoleEffect

# ==================== 中文字体支持 ====================
# Windows 常用中文字体列表
CHINESE_FONTS = [
    "Microsoft YaHei",
    "Microsoft YaHei UI",
    "SimHei",
    "SimSun",
    "DengXian",
    "FangSong",
    "KaiTi",
    "NSimSun",
    "YouYuan",
    "STKaiti",
    "STSong",
    "STZhongsong",
]

def get_font(size, bold=False):
    """获取支持中文的字体
    
    Args:
        size: 字体大小
        bold: 是否粗体
    
    Returns:
        pygame.font.Font 对象
    """
    # 尝试使用中文字体
    for font_name in CHINESE_FONTS:
        try:
            font = pygame.font.SysFont(font_name, size, bold=bold)
            # 测试字体是否能渲染中文
            test_surface = font.render("中", True, (255, 255, 255))
            if test_surface.get_width() > 0:
                return font
        except:
            continue
    
    # 回退到默认字体
    return get_font( size)


# ==================== 技能冷却显示系统 ====================
# 技能冷却配置: 按键, 名称, 冷却时间(秒), 图标颜色
SKILL_COOLDOWNS = [
    {'key': 'Q', 'name': '减速', 'cooldown': 15.0, 'color': (100, 200, 255)},
    {'key': 'W', 'name': '冰冻', 'cooldown': 20.0, 'color': (150, 230, 255)},
    {'key': 'E', 'name': '群攻', 'cooldown': 25.0, 'color': (255, 150, 50)},
]

def draw_skill_cooldown_panel():
    """绘制技能冷却显示面板"""
    # 面板位置: 底部中央
    panel_x = SCREEN_WIDTH // 2 - 150
    panel_y = SCREEN_HEIGHT - 120
    skill_slot_width = 80
    skill_slot_height = 70
    gap = 15
    
    # 背景面板
    panel_bg = pygame.Surface((skill_slot_width * 3 + gap * 2 + 20, skill_slot_height + 30), pygame.SRCALPHA)
    panel_bg.fill((20, 20, 40, 200))
    SCREEN.blit(panel_bg, (panel_x - 10, panel_y - 15))
    pygame.draw.rect(SCREEN, (60, 60, 90), (panel_x - 10, panel_y - 15, skill_slot_width * 3 + gap * 2 + 20, skill_slot_height + 30), 2, border_radius=8)
    
    for i, skill in enumerate(SKILL_COOLDOWNS):
        slot_x = panel_x + i * (skill_slot_width + gap)
        slot_rect = pygame.Rect(slot_x, panel_y, skill_slot_width, skill_slot_height)
        
        # 获取当前冷却时间
        cooldown_left = 0
        if i == 0:  # Q减速
            cooldown_left = getattr(state, 'slow_skill_timer', 0)
        elif i == 1:  # W冰冻
            cooldown_left = getattr(state, 'freeze_skill_timer', 0)
        elif i == 2:  # E群攻
            cooldown_left = getattr(state, 'aoe_skill_timer', 0)
        
        cooldown_ratio = cooldown_left / skill['cooldown']
        is_ready = cooldown_left <= 0
        
        # 槽位背景
        bg_color = (40, 40, 60) if is_ready else (30, 30, 50)
        pygame.draw.rect(SCREEN, bg_color, slot_rect, border_radius=8)
        
        # 冷却进度条
        if cooldown_ratio > 0:
            fill_height = int(slot_rect.height * cooldown_ratio)
            fill_rect = pygame.Rect(slot_x, panel_y + slot_rect.height - fill_height, skill_slot_width, fill_height)
            pygame.draw.rect(SCREEN, (*skill['color'], 150), fill_rect, border_radius=8)
            
            # 冷却遮罩 (模拟冷却中)
            mask_surf = pygame.Surface((skill_slot_width, skill_slot_height), pygame.SRCALPHA)
            mask_surf.fill((0, 0, 0, 120))
            SCREEN.blit(mask_surf, (slot_x, panel_y))
            
            # 剩余时间文字
            font_cd = get_font(18)
            cd_text = font_cd.render(f"{cooldown_left:.1f}s", True, (255, 255, 255))
            SCREEN.blit(cd_text, (slot_x + skill_slot_width//2 - cd_text.get_width()//2, panel_y + skill_slot_height//2))
        else:
            # 就绪状态发光效果
            glow_rect = pygame.Rect(slot_x - 2, panel_y - 2, skill_slot_width + 4, skill_slot_height + 4)
            pygame.draw.rect(SCREEN, (*skill['color'], 100), glow_rect, 3, border_radius=10)
        
        # 边框
        border_color = skill['color'] if is_ready else (80, 80, 100)
        pygame.draw.rect(SCREEN, border_color, slot_rect, 2, border_radius=8)
        
        # 技能按键
        font_key = get_font(16, bold=True)
        key_text = font_key.render(skill['key'], True, skill['color'])
        SCREEN.blit(key_text, (slot_x + 8, panel_y + 8))
        
        # 技能名称
        font_name = get_font(14)
        name_text = font_name.render(skill['name'], True, (200, 200, 220))
        SCREEN.blit(name_text, (slot_x + skill_slot_width//2 - name_text.get_width()//2, panel_y + skill_slot_height - 22))

# ==================== 精致UI边框和动画系统 ====================

def draw_ui_border():
    """绘制精致UI边框"""
    # 顶部标题栏渐变边框
    pygame.draw.line(SCREEN, (60, 60, 80), (0, 0), (SCREEN_WIDTH, 0), 3)
    pygame.draw.line(SCREEN, (100, 100, 120), (0, 1), (SCREEN_WIDTH, 1), 2)
    
    # 左侧生命值栏 - 带渐变背景
    lives_rect = pygame.Rect(10, 50, 180, 40)
    lives_surf = pygame.Surface((180, 40), pygame.SRCALPHA)
    lives_surf.fill((30, 30, 50, 200))
    SCREEN.blit(lives_surf, (10, 50))
    pygame.draw.rect(SCREEN, (80, 60, 40), lives_rect, 2, border_radius=5)
    
    # 右侧金币 - 带渐变背景
    gold_rect = pygame.Rect(SCREEN_WIDTH - 130, 50, 120, 40)
    gold_surf = pygame.Surface((120, 40), pygame.SRCALPHA)
    gold_surf.fill((30, 30, 50, 200))
    SCREEN.blit(gold_surf, (SCREEN_WIDTH - 130, 50))
    pygame.draw.rect(SCREEN, (80, 60, 40), gold_rect, 2, border_radius=5)
    
    # 波次信息框 - 带背景
    wave_box_x, wave_box_y = SCREEN_WIDTH//2 - 80, 10
    wave_surf = pygame.Surface((160, 35), pygame.SRCALPHA)
    wave_surf.fill((30, 30, 50, 180))
    SCREEN.blit(wave_surf, (wave_box_x, wave_box_y))
    pygame.draw.rect(SCREEN, (50, 50, 70), (wave_box_x, wave_box_y, 160, 35), 2, border_radius=8)
    
    # 修复：塔按钮区域移到右侧，避免与底部提示栏重叠
    # 右侧塔按钮面板
    tower_panel_x = SCREEN_WIDTH - 100
    tower_panel_y = 80
    tower_button_width = 90
    tower_button_height = 40
    tower_types = ['箭塔', '炮塔', '魔法塔', '减速塔', '冰霜塔']
    selected = config.get('tower_selection', None)
    for i, tower_type in enumerate(tower_types):
        btn_rect = pygame.Rect(tower_panel_x, tower_panel_y + i * (tower_button_height + 5), tower_button_width, tower_button_height)
        # 背景
        pygame.draw.rect(SCREEN, (60, 60, 80), btn_rect, border_radius=6)
        # 普通按钮边框
        pygame.draw.rect(SCREEN, (80, 80, 100), btn_rect, 2, border_radius=6)
        # 选中高亮
        if selected == tower_type:
            pygame.draw.rect(SCREEN, GOLD, btn_rect, 3, border_radius=6)
        # 塔名称
        btn_font = get_font(20)
        btn_text = btn_font.render(tower_type[:2], True, WHITE)  # 只显示前2个字符
        text_rect = btn_text.get_rect(center=btn_rect.center)
        SCREEN.blit(btn_text, text_rect)

def draw_button_hover():
    """按钮悬停/点击效果 + 攻击范围预览"""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    tower_types = ['箭塔', '炮塔', '魔法塔', '减速塔', '冰霜塔']
    for i, tower_type in enumerate(tower_types):
        btn_rect = pygame.Rect(30 + i * 85, SCREEN_HEIGHT - 60, 75, 50)
        if btn_rect.collidepoint(mouse_x, mouse_y):
            # 悬停发光效果
            glow_surf = pygame.Surface((70, 50), pygame.SRCALPHA)
            glow_surf.fill((255, 255, 200, 50))
            SCREEN.blit(glow_surf, (50 + i * 80, SCREEN_HEIGHT - 60))
            
            # 悬停时在鼠标位置显示攻击范围预览
            tower_stats = config.get('towers', {}).get(tower_type, {})
            if tower_stats:
                tower_range = tower_stats.get('range', 1.5)
                range_radius = int(tower_range * 50)
                
                # 根据塔类型选择颜色
                if "箭" in tower_type:
                    range_color = (*BLUE, 60)
                    border_color = BLUE
                elif "炮" in tower_type:
                    range_color = (*RED, 60)
                    border_color = RED
                elif "魔法" in tower_type:
                    range_color = (*PURPLE, 60)
                    border_color = PURPLE
                elif "减速" in tower_type or "冰霜" in tower_type:
                    range_color = (*CYAN, 60)
                    border_color = CYAN
                else:
                    range_color = (100, 100, 100, 60)
                    border_color = WHITE
                
                # 绘制半透明范围圆
                if show_attack_range:
                    range_surf = pygame.Surface((range_radius*2, range_radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(range_surf, range_color, (range_radius, range_radius), range_radius)
                    SCREEN.blit(range_surf, (mouse_x - range_radius, mouse_y - range_radius))
                    
                    # 实线边框
                    pygame.draw.circle(SCREEN, border_color, (mouse_x, mouse_y), range_radius, 2)

def animate_text(text, x, y, color, flicker=False):
    """带闪烁效果的文字"""
    if flicker:
        alpha = 150 + math.sin(pygame.time.get_ticks() * 0.01) * 100
    else:
        alpha = 255
    
    font = get_font( 28)
    surf = font.render(text, True, color)
    surf.set_alpha(int(alpha))
    SCREEN.blit(surf, (x, y))

# 截图保存目录
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ==================== 渐变表面缓存 ====================
_gradient_cache = {}

def get_cached_gradient(size, color1, color2, direction='horizontal'):
    """获取或创建渐变表面缓存"""
    key = (size, color1, color2, direction)
    if key in _gradient_cache:
        return _gradient_cache[key]
    
    surf = pygame.Surface(size, pygame.SRCALPHA)
    if direction == 'horizontal':
        for x in range(size[0]):
            ratio = x / size[0]
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surf, (r, g, b, 255), (x, 0), (x, size[1]))
    else:  # vertical
        for y in range(size[1]):
            ratio = y / size[1]
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surf, (r, g, b, 255), (0, y), (size[0], y))
    
    _gradient_cache[key] = surf
    return surf

def clear_gradient_cache():
    """清除渐变缓存"""
    global _gradient_cache
    _gradient_cache = {}

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

# ==================== 动态光影系统 ====================
lights = []  # 光源列表: [{"x": x, "y": y, "radius": radius, "color": color, "intensity": intensity}]

def add_light(x, y, radius=50, color=(255, 200, 100), intensity=1.0):
    """添加光源"""
    lights.append({"x": x, "y": y, "radius": radius, "color": color, "intensity": intensity})

def update_lights():
    """更新光源（闪烁效果）"""
    global lights
    for light in lights:
        # 闪烁效果
        flicker = math.sin(pygame.time.get_ticks() * 0.005) * 0.1 + 0.9
        light["intensity"] = flicker

def draw_lights():
    # 绘制每日挑战面板
    draw_daily_challenge_panel(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT)
    """绘制光影叠加层"""
    if not lights:
        return
    
    # 创建光照层
    light_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    for light in lights:
        x, y = light["x"], light["y"]
        radius = light["radius"] * light["intensity"]
        color = light["color"]
        intensity = light["intensity"]
        
        # 光晕渐变
        for r in range(int(radius), 0, -5):
            alpha = int((1 - r/radius) * 80 * intensity)
            pygame.draw.circle(light_layer, (*color, alpha), (int(x), int(y)), r)
    
    SCREEN.blit(light_layer, (0, 0))

def apply_dynamic_lights():
    """根据游戏状态动态添加光源"""
    global lights
    lights.clear()
    
    # 1. 萝卜处光源（始终存在）
    carrot_light_radius = 30 + math.sin(pygame.time.get_ticks() * 0.002) * 5
    add_light(700, 300, carrot_light_radius, (100, 255, 100), 0.6)
    
    # 2. 选中塔时添加光源
    if state.selected_tower:
        tower = state.selected_tower
        add_light(tower.x, tower.y, 40, (255, 215, 0), 0.8)
    
    # 3. Boss出现时添加光源
    for monster in state.monsters:
        if hasattr(monster, 'is_boss') and monster.is_boss:
            mx = 100 + monster.position * 600
            my = 300
            add_light(mx, my, 80, (255, 50, 50), 1.0)
            break

# ==================== 粒子系统（对象池优化）====================
particles = []  # [(x, y, vx, vy, color, life, size)]
MAX_PARTICLES = 200  # 粒子数量上限
particle_surfaces = {}  # 预渲染表面缓存

def create_particle_surface(size):
    """创建粒子预渲染表面（用于对象池）"""
    if size not in particle_surfaces:
        s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 255), (size, size), size)
        particle_surfaces[size] = s
    return particle_surfaces[size]

def spawn_particles(x, y, color, count=10):
    """生成粒子（带对象池复用）"""
    available = MAX_PARTICLES - len(particles)
    if available <= 0:
        return
    count = min(count, available)
    
    for _ in range(count):
        angle = random.uniform(0, 6.28)
        speed = random.uniform(50, 150)
        particles.append([
            x, y,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            color,
            1.0,  # 生命周期
            random.randint(2, 5)
        ])

def update_particles(dt):
    """更新粒子"""
    global particles
    for p in particles[:]:
        p[0] += p[2] * dt
        p[1] += p[3] * dt
        p[5] -= dt * 1.5
        p[3] += 50 * dt
        
        if p[5] <= 0:
            particles.remove(p)

def draw_particles():
    """绘制粒子（优化版）"""
    for p in particles:
        x, y, _, _, color, life, size = p
        alpha = int(life * 255)
        # 复用预渲染表面
        if size not in particle_surfaces:
            particle_surfaces[size] = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surfaces[size], (255, 255, 255, 255), (size, size), size)
        s = particle_surfaces[size].copy()
        # 快速着色
        pygame.draw.circle(s, (*color, alpha), (size, size), size)
        SCREEN.blit(s, (int(x - size), int(y - size)))

# 游戏结束报告函数
def draw_end_report(screen, won, stats, time_seconds):
    """绘制游戏结束统计报告"""
    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # 标题
    font_title = get_font( 60)
    if won:
        title = font_title.render("🎉 胜利!", True, GOLD)
    else:
        title = font_title.render("💀 失败", True, RED)
    screen.blit(title, (SCREEN_WIDTH//2 - 80, 80))
    
    # 统计内容
    font_info = get_font( 32)
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
    font_eval = get_font( 40)
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

# ==================== 每日任务系统 ====================
import datetime

# 获取今天的日期字符串作为任务刷新标记
def get_daily_key():
    return datetime.datetime.now().strftime("%Y%m%d")

# 每日任务数据
daily_quests = {
    "kill_30": {"name": "击杀30只怪物", "target": 30, "progress": 0, "reward": 100, "completed": False},
    "earn_500": {"name": "获得500金币", "target": 500, "progress": 0, "reward": 150, "completed": False},
    "build_5": {"name": "建造5座塔", "target": 5, "progress": 0, "reward": 200, "completed": False},
    "wave_5": {"name": "通过第5波", "target": 5, "progress": 0, "reward": 300, "completed": False},
}

# 记录累计获得金币（用于任务进度）
total_gold_earned_session = 0  # 本局获得的金币
last_daily_key = get_daily_key()  # 上次检查的日期

# 任务通知
quest_notify = ""
quest_timer = 0

# 检查并重置每日任务
def check_daily_reset():
    global last_daily_key, daily_quests
    current_key = get_daily_key()
    if current_key != last_daily_key:
        # 新的一天，重置任务
        last_daily_key = current_key
        for key in daily_quests:
            daily_quests[key]["progress"] = 0
            daily_quests[key]["completed"] = False
        print("📅 每日任务已刷新!")

# 更新任务进度
def update_quest(quest_key, amount=1):
    global quest_notify, quest_timer
    if quest_key in daily_quests:
        quest = daily_quests[quest_key]
        if not quest["completed"]:
            quest["progress"] = min(quest["progress"] + amount, quest["target"])
            if quest["progress"] >= quest["target"]:
                quest["completed"] = True
                state.money += quest["reward"]
                quest_notify = f"🎯 任务完成: {quest['name']}! +{quest['reward']}金币"
                quest_timer = 3.0
                print(f"🎯 任务完成: {quest['name']}! +{quest['reward']}金币")

# 绘制任务面板
def draw_quest_panel():
    quest_x = 10
    # 修复：每日任务面板放到右下方，避免与怪物路径(y=300)和底部提示栏重叠
    quest_y = 430
    
    # 面板背景 - 调整为更小的高度适应底部
    panel_width = 180
    panel_height = 120  # 从140改为120以避免与底部重叠
    panel_rect = pygame.Rect(quest_x - 5, quest_y - 5, panel_width, panel_height)
    pygame.draw.rect(SCREEN, (30, 30, 50), panel_rect, border_radius=5)
    pygame.draw.rect(SCREEN, GOLD, panel_rect, 2, border_radius=5)
    
    # 标题
    font_title = get_font( 22)
    title = font_title.render("📋 每日任务", True, GOLD)
    SCREEN.blit(title, (quest_x, quest_y))
    
    font_quest = get_font( 16)  # 字体稍小以适应小面板
    for key, quest in daily_quests.items():
        quest_y += 22  # 减少间距
        
        if quest["completed"]:
            color = GREEN
            status = "✓"
        else:
            color = WHITE
            status = f"{quest['progress']}/{quest['target']}"
        
        # 任务名称（截断过长）
        name = quest["name"][:8] + ".." if len(quest["name"]) > 8 else quest["name"]
        text = f"{name} {status}"
        surf = font_quest.render(text, True, color)
        SCREEN.blit(surf, (quest_x, quest_y))

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

# ==================== 成就解锁动画 ====================
achievement_unlock_anim = None  # {"name": "", "icon": "", "timer": 0}
dt = 0  # 全局delta time用于动画

def show_achievement_unlock(name, icon):
    """显示成就解锁动画"""
    global achievement_unlock_anim
    achievement_unlock_anim = {"name": name, "icon": icon, "timer": 3.0}

def draw_achievement_unlock():
    """绘制成就解锁动画 - 从右侧滑入"""
    global achievement_unlock_anim
    
    if achievement_unlock_anim is None:
        return
    
    timer = achievement_unlock_anim["timer"]
    timer -= dt * game_speed
    achievement_unlock_anim["timer"] = timer
    
    if timer <= 0:
        achievement_unlock_anim = None
        return
    
    # 从右侧滑入动画
    anim_progress = (3.0 - timer) / 3.0
    if anim_progress < 0.2:
        x = SCREEN_WIDTH - (anim_progress * 5) * 200
    else:
        x = SCREEN_WIDTH - 200
    
    y = 100
    
    # 背景
    pygame.draw.rect(SCREEN, (50, 50, 80), (x, y, 190, 60), border_radius=10)
    pygame.draw.rect(SCREEN, GOLD, (x, y, 190, 60), 3, border_radius=10)
    
    # 图标和文字
    font = get_font( 28)
    icon = achievement_unlock_anim["icon"]
    name = achievement_unlock_anim["name"]
    
    icon_surf = font.render(icon, True, YELLOW)
    name_surf = font.render(f"成就解锁: {name}", True, WHITE)
    
    SCREEN.blit(icon_surf, (x + 10, y + 15))
    SCREEN.blit(name_surf, (x + 45, y + 20))

# ==================== 成就徽章UI ====================
def draw_achievement_badges():
    """绘制已解锁成就徽章（顶部居中）"""
    unlocked = [k for k, v in achievements.items() if v.get("unlocked")]
    
    if not unlocked:
        return
    
    # 顶部居中显示
    badge_count = min(len(unlocked), 8)  # 最多8个
    total_width = badge_count * 45
    start_x = (SCREEN_WIDTH - total_width) // 2
    badge_y = 35
    
    # 成就图标映射
    icon_map = {
        "first_blood": "⚔️", "ten_kills": "🗡️", "fifty_kills": "🏹",
        "hundred_kills": "💀", "upgrade_tower": "⬆️", "sell_tower": "💰",
        "no_damage_wave": "🛡️", "fast_win": "⚡", "rich": "💎",
    }
    
    for i, achievement_key in enumerate(unlocked[:badge_count]):
        badge_x = start_x + i * 45 + 22
        
        # 脉冲发光效果
        pulse = (math.sin(time.time() * 3 + i) + 1) / 2
        glow_size = 3 + pulse * 2
        
        # 悬停检测
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - badge_x
        dy = mouse_pos[1] - badge_y
        hovered = (dx * dx + dy * dy) < 400
        
        # 发光边框
        glow_color = (255, 215, 0, 180) if hovered else (255, 215, 0, 100)
        if hovered:
            pygame.draw.circle(SCREEN, glow_color, (badge_x, badge_y), 20 + glow_size)
        
        # 徽章背景（金色圆形）
        pygame.draw.circle(SCREEN, GOLD, (badge_x, badge_y), 18)
        pygame.draw.circle(SCREEN, (200, 150, 0), (badge_x, badge_y), 15)
        
        # 徽章图标
        icon = icon_map.get(achievement_key, "⭐")
        font_icon = get_font(18)
        icon_surf = font_icon.render(icon, True, WHITE)
        SCREEN.blit(icon_surf, (badge_x - 9, badge_y - 10))
        
        # 悬停显示名称
        if hovered:
            name = achievements[achievement_key].get("name", achievement_key)
            font_name = get_font(16)
            name_surf = font_name.render(name, True, WHITE)
            bg_rect = pygame.Surface((name_surf.get_width() + 12, name_surf.get_height() + 6), pygame.SRCALPHA)
            bg_rect.fill((0, 0, 0, 220))
            SCREEN.blit(bg_rect, (badge_x - name_surf.get_width() // 2 - 6, badge_y - 30))
            SCREEN.blit(name_surf, (badge_x - name_surf.get_width() // 2, badge_y - 27))

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

# ==================== 关卡选择 ====================
level_select_mode = True  # 关卡选择模式
selected_level = 0  # 当前选中的关卡索引
selected_level_data = None  # 选中的关卡数据

def draw_level_select():
    """绘制关卡选择界面"""
    SCREEN.fill((20, 25, 45))
    
    font_title = get_font( 50)
    title = font_title.render("选择关卡", True, GOLD)
    SCREEN.blit(title, (SCREEN_WIDTH//2 - 60, 30))
    
    # 加载关卡
    levels = config.get("levels", [])
    
    for i, level in enumerate(levels):
        y = 100 + i * 45
        
        # 选中高亮
        if i == selected_level:
            pygame.draw.rect(SCREEN, (50, 80, 120), (50, y - 5, SCREEN_WIDTH - 100, 40))
            color = YELLOW
        else:
            color = WHITE
        
        # 关卡信息
        font = get_font( 30)
        level_text = f"{i+1}. {level['name']} - {level['waves']}波 (x{level['difficulty']})"
        surf = font.render(level_text, True, color)
        SCREEN.blit(surf, (70, y))
    
    # 提示
    font_tip = get_font( 24)
    tip = font_tip.render("↑↓选择  Enter确认  ESC退出", True, GRAY)
    SCREEN.blit(tip, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 50))

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

    font_title = get_font( 60)
    title = font_title.render("选择难度", True, YELLOW)
    SCREEN.blit(title, (SCREEN_WIDTH//2 - 80, 100))

    difficulties = [
        ("简单 - 怪物血量x0.7", (100, 200), (100, 200, 100)),
        ("普通 - 怪物血量x1.0", (100, 280), (100, 100, 200)),
        ("困难 - 怪物血量x1.5", (100, 360), (200, 100, 100)),
    ]

    for text, pos, color in difficulties:
        font = get_font( 36)
        surf = font.render(text, True, color)
        SCREEN.blit(surf, pos)

    font_tip = get_font( 24)
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

    font_selected = get_font( 28)
    selected_surf = font_selected.render(selected_text, True, selected_color)
    SCREEN.blit(selected_surf, (SCREEN_WIDTH//2 - 60, 500))

# 音乐控制
music_enabled = True
music_volume = 0.5
BGMusic = None

from sound_manager import SoundManager

def init_audio():
    """初始化音频系统 - 延迟到游戏启动时调用"""
    global sound_manager
    try:
        pygame.mixer.init()
        # 初始化音效管理器
        sound_manager = SoundManager()
    except pygame.error as e:
        print(f"⚠️ 音频初始化失败: {e}")
        sound_manager = None
    return sound_manager is not None

# 音效管理器 - 延迟到main()中初始化
sound_manager = None

from config_loader import load_config, get_config
from checkin_system import checkin_data, try_checkin, draw_checkin_panel

# 游戏速度
game_speed = 1.0  # 1.0=正常, 2.0=快进, 0.5=慢放
speed_labels = {0.5: "🐢 慢放", 1.0: "▶️ 正常", 2.0: "⏩ 快进"}
from state_machine import GameStateMachine
from towers import TowerFactory, Tower, set_sound_player, set_sound_manager
from monsters import MonsterFactory
from projectiles import Projectile
from projectiles import set_sound_manager_for_projectiles
from waves import WaveManager
from tower_placement import TowerPlacement
from particle_system import get_particle_system
from damage_numbers import DamageNumberManager
from combo_system import get_combo_system
from base_effects import get_base_effect_manager
from synergy_system import get_synergy_manager

# 设置全局音效管理器给towers模块
set_sound_manager(sound_manager)
set_sound_manager_for_projectiles(sound_manager)

# 屏幕震动
screen_shake = 0

# 连击系统
combo_system = None
screen_shake_offset = [0, 0]

# Boss警告特效列表
boss_warning_effects = []  # [BossWarningEffect, ...]

def trigger_screen_shake(intensity=10, duration=0.3):
    """触发屏幕震动"""
    global screen_shake
    screen_shake = intensity

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

shoot_sound = None

def init_game():
    """初始化游戏 - 在main()开头调用"""
    global shoot_sound
    
    # 初始化pygame
    try:
        pygame.init()
    except pygame.error as e:
        print(f"⚠️ Pygame初始化失败: {e}")
    
    # 初始化显示和音频
    init_display()
    init_audio()
    
    # 尝试加载音效(可选)
    SHOOT_SOUND_PATH = '/usr/share/sounds/pygame/stereo/player_shot.wav'
    try:
        shoot_sound = pygame.mixer.Sound(SHOOT_SOUND_PATH) if os.path.exists(SHOOT_SOUND_PATH) else None
    except:
        shoot_sound = None
    
    # 设置全局音效播放器
    set_sound_player(lambda: play_sound(shoot_sound))

def play_sound(sound):
    if sound:
        try:
            sound.play()
        except:
            pass

# 全局屏幕对象 - 延迟到init_game()中初始化
SCREEN = None

def init_display():
    """初始化显示系统"""
    global SCREEN
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("保卫萝卜 - Carrot Fantasy v0.3")
    return SCREEN

# 放置特效
place_effects = []  # [(x, y, color, timer), ...]

# 死亡特效列表
death_effects = []  # [(x, y, timer, color), ...]

# 升级特效
upgrade_effects = []  # [(x, y, timer), ...]

# 升级光柱特效列表 (新)
upgrade_beam_effects = []  # [UpgradeBeamEffect, ...]

# 塔选中脉冲特效列表 (新)
tower_selection_pulses = []  # [TowerSelectionPulse, ...]

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

# ==================== 背包系统 ====================
inventory = {"arrow": 0, "cannon": 0, "magic": 0, "ice": 0}  # 存放拆卸的塔
show_inventory = False  # 背包面板显示开关

def sell_tower_to_inventory(tower):
    """出售塔到背包（返还一半金币到背包）"""
    refund = tower.level * 30  # 等级*30金币
    tower_type = tower.name
    # 映射塔名称到背包key
    type_map = {"箭塔": "arrow", "炮塔": "cannon", "魔法塔": "magic", "减速塔": "ice"}
    inv_key = type_map.get(tower_type, tower_type)
    if inv_key in inventory:
        inventory[inv_key] += 1
    else:
        inventory[inv_key] = 1
    state.money += refund
    sound_manager.play('sell')
    print(f"🔄 {tower_type}塔存入背包，返还{refund}金币")

def use_inventory_tower(tower_type):
    """从背包取出塔（消耗1个）"""
    type_map = {"箭塔": "arrow", "炮塔": "cannon", "魔法塔": "magic", "减速塔": "ice"}
    inv_key = type_map.get(tower_type, tower_type)
    if inv_key in inventory and inventory[inv_key] > 0:
        inventory[inv_key] -= 1
        return True
    return False

def draw_inventory_panel():
    """绘制背包面板 - 按B键查看"""
    panel_w, panel_h = 200, 120
    panel_x = SCREEN_WIDTH - panel_w - 10
    panel_y = SCREEN_HEIGHT - 140
    
    # 背景
    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s.fill((40, 40, 60, 220))
    SCREEN.blit(s, (panel_x, panel_y))
    
    # 边框
    pygame.draw.rect(SCREEN, (100, 100, 150), (panel_x, panel_y, panel_w, panel_h), 2, border_radius=5)
    
    # 标题
    font = get_font( 22)
    title = font.render("🎒 背包 (B)", True, (255, 215, 0))
    SCREEN.blit(title, (panel_x + 10, panel_y + 5))
    
    # 塔数量
    icons = {"arrow": "🏹", "cannon": "💣", "magic": "🔮", "ice": "❄️"}
    for i, (tower_type, count) in enumerate(inventory.items()):
        row = i // 2
        col = i % 2
        x = panel_x + 10 + col * 90
        y = panel_y + 30 + row * 30
        text = font.render(f"{icons[tower_type]} {count}", True, (200, 200, 200))
        SCREEN.blit(text, (x, y))

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

# 显示攻击范围
show_attack_range = True

# 显示塔图鉴
show_tower_book = False

# 显示怪物图鉴
show_monster_book = False

# 波次预览系统
show_wave_preview = False

# 波次间隔
wave_wait_timer = 0
wave_wait_duration = 5.0  # 每波间隔5秒

# 波次击杀计数（用于大量击杀震动）
kills_this_wave = 0

class GameData:
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
        # 技能系统状态
        self.slow_skill_active = False
        self.slow_skill_timer = 0.0
        self.slow_skill_cooldown = 0.0  # 15秒冷却
        self.freeze_skill_active = False
        self.freeze_skill_timer = 0.0
        self.freeze_skill_cooldown = 0.0  # 20秒冷却
        self.aoe_skill_active = False
        self.aoe_skill_timer = 0.0
        self.aoe_skill_cooldown = 0.0  # 25秒冷却
        # 庆祝特效系统
        self.celebration_effect = None
        self.stage_complete_effect = None

    def reset(self):
        global final_wave_announced, game_complete_time, difficulty_selected, level_select_mode, selected_level
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
        # 清除庆祝特效
        self.celebration_effect = None
        self.stage_complete_effect = None
        # 游戏重置
        final_wave_announced = False
        game_complete_time = None
        difficulty_selected = False  # 重置难度选择状态
        level_select_mode = True  # 重新进入关卡选择
        selected_level = 0
# 全局游戏状态
state = GameData()

# 游戏对象 - 在init_new_game()中初始化
global_base_effect_manager = None
global_particle_system = None
global_damage_number_manager = None

def init_new_game():
    """初始化新游戏 - 在难度选择完成后调用"""
    global global_base_effect_manager, global_particle_system, global_damage_number_manager, combo_system
    
    # 初始化粒子系统
    global_particle_system = get_particle_system()
    # 初始化塔基特效系统
    global_base_effect_manager = get_base_effect_manager()
    # 初始化伤害数字系统
    global_damage_number_manager = DamageNumberManager()
    # 初始化连击系统
    combo_system = get_combo_system()
    
    # 修复：自动开始第一波
    global wave_wait_timer
    wave_wait_timer = 2.0  # 2秒后自动开始第一波
    
    print("游戏初始化完成!")
    return global_base_effect_manager, global_particle_system, global_damage_number_manager

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
    
    # 更新和绘制动态光影
    update_lights()
    apply_dynamic_lights()
    draw_lights()
    # 绘制每日挑战面板
    draw_daily_challenge_panel(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT)

    # 绘制渐变天空背景
    sky_height = 150
    for y in range(sky_height):
        # 从深蓝到浅蓝的渐变
        r = int(30 + (y / sky_height) * 40)
        g = int(40 + (y / sky_height) * 60)
        b = int(80 + (y / sky_height) * 80)
        pygame.draw.line(SCREEN, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # 绘制草地背景
    grass_color = (45, 100, 45)
    pygame.draw.rect(SCREEN, grass_color, (0, sky_height, SCREEN_WIDTH, SCREEN_HEIGHT - sky_height))
    
    # 草地纹理(随机小点)
    random.seed(42)  # 固定种子保持一致
    for _ in range(200):
        gx = random.randint(0, SCREEN_WIDTH)
        gy = random.randint(sky_height, SCREEN_HEIGHT)
        pygame.draw.circle(SCREEN, (35, 80, 35), (gx, gy), 1)
    random.seed()  # 恢复随机种子

    # 绘制怪物行走路线(带边缘装饰)
    path_color = (70, 70, 70)  # 路线颜色
    path_width = 44  # 略宽一点
    path_y = 300
    pygame.draw.rect(SCREEN, (50, 50, 50), (95, path_y - path_width//2, 610, path_width))  # 边缘深色
    pygame.draw.rect(SCREEN, path_color, (100, path_y - path_width//2 + 2, 600, path_width - 4))  # 主体

    # 路线装饰虚线
    for i in range(10):
        x = 100 + i * 60 + 30
        pygame.draw.line(SCREEN, (90, 90, 90), (x, path_y - 15), (x, path_y + 15), 2)

    # ====== 传送门特效 ======
    # 入口传送门 (左侧发光)
    portal_time = pygame.time.get_ticks() * 0.003
    # 外圈旋转光环
    for i in range(3):
        radius = 25 + i * 8 + int(math.sin(portal_time + i) * 5)
        alpha = max(0, 150 - i * 40)
        portal_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(portal_surf, (100, 200, 255, alpha), (radius, radius), radius, 3)
        SCREEN.blit(portal_surf, (100 - radius, path_y - radius))
    # 入口闪光核心
    pygame.draw.circle(SCREEN, (150, 220, 255), (100, path_y), 12)
    pygame.draw.circle(SCREEN, WHITE, (100, path_y), 6)
    
    # 出口传送门 (右侧发光)
    exit_x = 700
    for i in range(3):
        radius = 25 + i * 8 + int(math.cos(portal_time + i) * 5)
        alpha = max(0, 150 - i * 40)
        portal_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(portal_surf, (255, 150, 100, alpha), (radius, radius), radius, 3)
        SCREEN.blit(portal_surf, (exit_x - radius, path_y - radius))
    # 出口闪光核心
    pygame.draw.circle(SCREEN, (255, 180, 120), (exit_x, path_y), 12)
    pygame.draw.circle(SCREEN, (255, 255, 200), (exit_x, path_y), 6)

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

    # === 传送门装饰效果 ===
    def draw_portal(cx, cy, color_primary, color_secondary, time_offset=0):
        """绘制传送门效果"""
        t = pygame.time.get_ticks() / 1000.0 + time_offset
        
        # 外层光环 - 脉冲效果
        pulse = 1.0 + 0.1 * math.sin(t * 3)
        radius_outer = int(25 * pulse)
        
        # 绘制多层光环
        for i in range(3):
            alpha = 60 - i * 15
            radius = radius_outer - i * 5
            portal_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(portal_surf, (*color_primary, alpha), (radius, radius), radius, 2)
            SCREEN.blit(portal_surf, (cx - radius, cy - radius))
        
        # 旋转的能量环
        angle = t * 2
        for i in range(4):
            rot_angle = angle + i * (math.pi / 2)
            ex = cx + math.cos(rot_angle) * 18
            ey = cy + math.sin(rot_angle) * 18
            pygame.draw.circle(SCREEN, color_secondary, (int(ex), int(ey)), 4)
        
        # 中心发光
        center_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(center_surf, (*color_primary, 100), (15, 15), 12)
        pygame.draw.circle(center_surf, (*color_secondary, 180), (15, 15), 6)
        SCREEN.blit(center_surf, (cx - 15, cy - 15))
    
    # 起点传送门(绿色)
    draw_portal(100, 300, (0, 200, 100), (100, 255, 150), 0)
    font_mark = get_font( 20)
    start_text = font_mark.render("S", True, WHITE)
    SCREEN.blit(start_text, (95, 260))

    # 终点传送门(金色 - 萝卜)
    draw_portal(700 + shake_x, 300 + shake_y, (255, 180, 0), (255, 220, 100), 1.5)
    
    # 萝卜本身
    pygame.draw.circle(SCREEN, (255, 140, 0), (700 + shake_x, 300 + shake_y), 28)  # 深橙色外圈
    pygame.draw.circle(SCREEN, ORANGE, (700 + shake_x, 300 + shake_y), 22)  # 橙色主体
    pygame.draw.circle(SCREEN, (255, 200, 100), (700 + shake_x, 300 + shake_y), 14)  # 浅色高光
    # 萝卜叶子
    pygame.draw.line(SCREEN, (50, 180, 50), (700 + shake_x - 5, 300 + shake_y - 22), (700 + shake_x - 8, 300 + shake_y - 32), 3)
    pygame.draw.line(SCREEN, (50, 180, 50), (700 + shake_x + 5, 300 + shake_y - 22), (700 + shake_x + 8, 300 + shake_y - 32), 3)
    
    # 萝卜血条显示
    if show_health_detail or state.lives <= 7:  # 血量低于70%始终显示
        carrot_hp_ratio = state.lives / 10.0
        bar_width = 50
        bar_height = 8
        bar_x = 700 - bar_width // 2 + shake_x
        bar_y = 300 + 35 + shake_y
        # 血条背景
        pygame.draw.rect(SCREEN, (40, 40, 40), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), border_radius=3)
        # 血条填充
        hp_color = (50, 200, 50) if carrot_hp_ratio > 0.5 else (255, 180, 0) if carrot_hp_ratio > 0.25 else (255, 60, 60)
        pygame.draw.rect(SCREEN, hp_color, (bar_x, bar_y, int(bar_width * carrot_hp_ratio), bar_height), border_radius=2)

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
        
        # 冰冻视觉效果
        frozen_frames = getattr(monster, 'frozen', 0)
        if frozen_frames > 0:
            # 冰冻时显示蓝色光环+冰晶
            ice_alpha = min(180, frozen_frames * 8)
            freeze_pulse = int(math.sin(pygame.time.get_ticks() * 0.02) * 20 + 100)
            # 外层冰环
            ice_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(ice_surf, (100, 200, 255, freeze_pulse), (25, 25), 22, 3)
            SCREEN.blit(ice_surf, (x - 25 + shake_x, y - 25 + shake_y))
            # 冰晶粒子
            time_offset = pygame.time.get_ticks() * 0.01
            for i in range(6):
                angle = i * 60 + time_offset * 20
                ix = x + math.cos(math.radians(angle)) * 18 + shake_x
                iy = y + math.sin(math.radians(angle)) * 18 + shake_y
                pygame.draw.circle(SCREEN, (150, 230, 255), (int(ix), int(iy)), 3)

        # 绘制血条背景(带边框 - 更高更显眼) - 美化版本
        # 外边框白色
        pygame.draw.rect(SCREEN, (255, 255, 255), (x - 18 + shake_x, y - 30 + shake_y, 38, 14), 2, border_radius=3)
        # 背景深色
        bg_color = (40, 40, 50)
        pygame.draw.rect(SCREEN, bg_color, (x - 16 + shake_x, y - 28 + shake_y, 34, 10), border_radius=2)
        
        # 绘制血条(带渐变效果)
        health_ratio = monster.health / monster.max_health
        health_width = max(0, int(32 * health_ratio))
        # 颜色渐变 - 更丰富的色彩
        if health_ratio > 0.6:
            health_color = (80, 220, 80)  # 鲜绿
        elif health_ratio > 0.3:
            health_color = (255, 180, 0)  # 橙黄
        else:
            health_color = (255, 60, 60)  # 红色
        # 低血量发光效果
        if health_ratio <= 0.3:
            glow_intensity = int((math.sin(pygame.time.get_ticks() * 0.01) + 1) * 30 + 60)
            glow_color = (glow_intensity, 0, 0)
            # 绘制发光层
            glow_rect = pygame.Rect(x - 19 + shake_x, y - 31 + shake_y, 40, 16)
            pygame.draw.rect(SCREEN, glow_color, glow_rect, 3, border_radius=4)
        # 绘制主体血条
        pygame.draw.rect(SCREEN, health_color, (x - 16 + shake_x, y - 28 + shake_y, health_width, 10), border_radius=2)
        # 高光效果
        if health_width > 4:
            pygame.draw.rect(SCREEN, (255, 255, 255, 80), (x - 16 + shake_x, y - 28 + shake_y, health_width, 3), border_radius=1)

        # 详细血量显示(按H切换)
        if show_health_detail:
            font_health = get_font( 18)
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
            font_boss = get_font( 24)
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

        # 升级动画效果
        if hasattr(tower, 'upgrade_animation') and tower.upgrade_animation > 0:
            tower.upgrade_animation -= 1
            tower.glow_intensity = tower.upgrade_animation / 30.0
            # 创建扩展的光环
            glow_radius = 30 + (30 - tower.upgrade_animation) * 2
            glow_alpha = int(200 * tower.glow_intensity)
            glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 215, 0, glow_alpha), (glow_radius, glow_radius), glow_radius, 4)
            SCREEN.blit(glow_surf, (int(tower.x) - glow_radius + shake_x, int(tower.y) - glow_radius + shake_y))

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
            if show_attack_range:
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
                font_count = get_font( 20)
                count_text = f"👾{in_range_count}"
                count_surf = font_count.render(count_text, True, RED)
                SCREEN.blit(count_surf, (int(tower.x) + 20 + shake_x, int(tower.y) - 25 + shake_y))
            
            # 显示组合状态（同类型相邻加成）
            synergy = tower.check_synergy(state.towers)
            if synergy > 1.0:
                synergy_text = f"组合: +{int((synergy-1)*100)}%"
        
        # ===== 瞄准线预览系统 =====
        # 当塔未选中时，显示指向当前目标的瞄准线
        if not is_selected and state.game_running:
            current_target = tower.find_target(state.monsters)
            if current_target:
                # 更新瞄准线透明度（淡入）
                if tower.targeting_line_alpha < 180:
                    tower.targeting_line_alpha = min(180, tower.targeting_line_alpha + 15)
                
                # 计算目标位置
                m_x = 100 + current_target.position * 600
                m_y = 300
                
                # 计算瞄准线角度和长度
                dx = m_x - tower.x
                dy = m_y - tower.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    # 归一化方向
                    nx, ny = dx/dist, dy/dist
                    
                    # 瞄准线从塔中心延伸到目标方向（到塔边缘为止）
                    line_start_x = int(tower.x + nx * 25)
                    line_start_y = int(tower.y + ny * 25)
                    line_end_x = int(tower.x + nx * min(dist - 15, 60))  # 限制长度
                    line_end_y = int(tower.y + ny * min(dist - 15, 60))
                    
                    # 绘制瞄准线（虚线效果）
                    alpha = tower.targeting_line_alpha
                    line_color = (*YELLOW, alpha)
                    
                    # 主瞄准线
                    pygame.draw.line(SCREEN, line_color, 
                                   (line_start_x + shake_x, line_start_y + shake_y),
                                   (line_end_x + shake_x, line_end_y + shake_y), 2)
                    
                    # 瞄准箭头
                    arrow_size = 8
                    arrow_angle = math.atan2(ny, nx)
                    arrow_pt1 = (line_end_x + shake_x, line_end_y + shake_y)
                    arrow_pt2 = (int(line_end_x - arrow_size * math.cos(arrow_angle - 0.5)) + shake_x,
                                int(line_end_y - arrow_size * math.sin(arrow_angle - 0.5)) + shake_y)
                    arrow_pt3 = (int(line_end_x - arrow_size * math.cos(arrow_angle + 0.5)) + shake_x,
                                int(line_end_y - arrow_size * math.sin(arrow_angle + 0.5)) + shake_y)
                    pygame.draw.line(SCREEN, line_color, arrow_pt1, arrow_pt2, 2)
                    pygame.draw.line(SCREEN, line_color, arrow_pt1, arrow_pt3, 2)
            # 显示组合状态（同类型相邻加成）- 移到瞄准线系统之前
            synergy = tower.check_synergy(state.towers)
            if synergy > 1.0:
                synergy_text = f"组合: +{int((synergy-1)*100)}%"
                synergy_color = GOLD
            else:
                synergy_text = "组合: 无"
                synergy_color = GRAY
            
            font_synergy = get_font( 20)
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
                font_preview = get_font( 22)
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
    
    # 绘制塔基持续发光效果
    global_base_effect_manager.draw_tower_base_glows(SCREEN, state.towers)

    # 绘制防御塔攻击线(锁定目标) - 增强版
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

            # 目标锁定线 - 双层效果(外发光+内实线)
            # 外层发光
            glow_surf = pygame.Surface((abs(tx - int(tower.x)) + 20, 12), pygame.SRCALPHA)
            pygame.draw.line(glow_surf, (*color, 60), (10, 6), (abs(tx - int(tower.x)) + 10, 6), 6)
            SCREEN.blit(glow_surf, (min(int(tower.x), tx) - 10 + shake_x, int(tower.y) - 6 + shake_y))
            # 内层实线
            pygame.draw.line(SCREEN, color, (int(tower.x) + shake_x, int(tower.y) + shake_y), (tx + shake_x, ty + shake_y), 2)

            # 目标点高亮(红色小点)
            pygame.draw.circle(SCREEN, (255, 50, 50), (tx + shake_x, ty + shake_y), 5)
            pygame.draw.circle(SCREEN, WHITE, (tx + shake_x, ty + shake_y), 3)

            # 目标锁定框特效
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
        font_combo = get_font( 36)
        combo_surf = font_combo.render(combo_text, True, (255, 100, 0))
        SCREEN.blit(combo_surf, (SCREEN_WIDTH//2 - 60, 150))

    # 绘制连杀浮动特效(在怪物死亡位置)
    for ct in combo_texts[:]:
        cx, cy, ctext, ccolor, ctimer = ct
        ctimer -= dt * game_speed
        cy -= 30 * dt * game_speed  # 上浮

        font_ct = get_font( 28)
        ct_surf = font_ct.render(ctext, True, ccolor)
        # 文字描边效果
        outline_surf = font_ct.render(ctext, True, BLACK)
        SCREEN.blit(outline_surf, (int(cx) - 28 + shake_x + 1, int(cy) + shake_y + 1))
        SCREEN.blit(ct_surf, (int(cx) - 28 + shake_x, int(cy) + shake_y))

        # 更新计时器
        ct[4] = ctimer
        if ctimer <= 0:
            combo_texts.remove(ct)

    # 绘制金币动画(怪物死亡时掉落金币显示)
    for ca in coin_animations[:]:
        cx, cy, ctext, ctimer = ca
        ctimer -= dt * game_speed
        cy -= 40 * dt * game_speed  # 上浮效果
        alpha = min(255, int(ctimer * 255 * 2))  # 渐隐
        
        font_ca = get_font(24)
        # 金色文字带描边
        ca_surf = font_ca.render(ctext, True, (255, 215, 0))
        ca_outline = font_ca.render(ctext, True, (139, 69, 19))
        # 模拟透明度(创建带alpha的表面)
        ca_surf.set_alpha(alpha)
        SCREEN.blit(ca_outline, (int(cx) - 18 + 1, int(cy) + 1))
        SCREEN.blit(ca_surf, (int(cx) - 18, int(cy)))
        
        ca[1] = cy
        ca[3] = ctimer
        if ctimer <= 0:
            coin_animations.remove(ca)

    # 绘制金币不足警告
    if no_money_timer > 0:
        font_warn = get_font( 36)
        warn_text = font_warn.render(no_money_warning, True, RED)
        # 闪烁效果
        if int(no_money_timer * 10) % 2 == 0:
            SCREEN.blit(warn_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2))

    # 绘制速度状态
    if game_speed != 1.0:
        font_speed = get_font( 32)
        speed_text = font_speed.render(speed_labels[game_speed], True, YELLOW)
        SCREEN.blit(speed_text, (SCREEN_WIDTH - 100, 10))

    # 塔放置预览增强(包含范围和放置状态)
    if hasattr(state, "mouse_preview") and state.mouse_preview:
        mx, my, tower_type = state.mouse_preview

        # 获取塔的信息
        tower_info = config.get("towers", {}).get(tower_type, {})
        preview_range = tower_info.get("range", 3) * 50
        tower_cost = tower_info.get("cost", 50)
        
        # 检测是否可放置(路径检测)
        can_place = not any(
            abs(mx - (100 + col * 60 + 30)) < 30 and abs(my - (300)) < 25
            for col in range(10)
        ) and not any(
            80 + col * 60 < mx < 80 + (col+1) * 60 and 180 + row * 60 < my < 180 + (row+1) * 60
            for col in range(8) for row in range(4)
            if not (100 < 80 + col * 60 + 30 < 100 + 600 and 300 - 20 < 180 + row * 60 + 30 < 300 + 20)
        )
        
        # 颜色: 绿色=可放置, 红色=不可放置/钱不够
        if state.money < tower_cost:
            place_color = (255, 100, 100)  # 钱不够 - 红色
        elif can_place:
            place_color = (100, 255, 100)  # 可放置 - 绿色
        else:
            place_color = (255, 100, 100)  # 不可放置 - 红色

        # 范围填充(半透明)
        range_surf = pygame.Surface((preview_range*2, preview_range*2), pygame.SRCALPHA)
        pygame.draw.circle(range_surf, (*place_color, 25), (preview_range, preview_range), preview_range)
        SCREEN.blit(range_surf, (mx - preview_range, my - preview_range))

        # 范围边框
        pygame.draw.circle(SCREEN, place_color, (mx, my), preview_range, 2)

        # 中心塔形状预览
        points = [(mx, my - 12), (mx - 10, my + 8), (mx + 10, my + 8)]
        pygame.draw.polygon(SCREEN, place_color, points)
        
        # 费用显示
        font_cost = get_font( 20)
        cost_text = f"${tower_cost}"
        cost_surf = font_cost.render(cost_text, True, place_color)
        SCREEN.blit(cost_surf, (mx - 15, my + 15))

    # 显示游戏时间(右上角)
    font_time = get_font( 32)
    time_text = font_time.render(time_str, True, WHITE)
    SCREEN.blit(time_text, (SCREEN_WIDTH - 80, 50))

    # 显示FPS
    font_fps = get_font( 24)
    fps_text = font_fps.render(f"FPS: {fps}", True, (100, 255, 100))
    SCREEN.blit(fps_text, (10, 10))

    # 绘制波次提示(最终波提示)
    if wave_tip and wave_tip_timer > 0:
        font_tip = get_font( 48)
        tip_surf = font_tip.render(wave_tip, True, (255, 50, 50))
        SCREEN.blit(tip_surf, (SCREEN_WIDTH//2 - 100, 100))

    # 显示下一波预览
    if not state.wave_manager.is_waving and state.wave_manager.has_more_waves():
        next_wave = state.wave_manager.get_next_wave_index()
        wave_data = state.wave_manager.waves[next_wave] if next_wave < len(state.wave_manager.waves) else None
        if wave_data:
            font_preview = get_font( 24)
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
        font_ach = get_font( 32)
        ach_text = font_ach.render(achievement_notify, True, YELLOW)
        SCREEN.blit(ach_text, (SCREEN_WIDTH//2 - 100, 180))
    
    # 绘制成就解锁动画
    draw_achievement_unlock()
    
    # 任务通知
    global quest_timer
    if quest_timer > 0:
        quest_timer -= dt * game_speed
        font_quest_notif = get_font( 28)
        quest_text = font_quest_notif.render(quest_notify, True, CYAN)
        SCREEN.blit(quest_text, (SCREEN_WIDTH//2 - 120, 210))

    # ==================== 随机事件UI显示 ====================
    event_y = 80
    for event_key, event_data in random_events.items():
        if event_data["active"]:
            font_event = get_font( 28)
            # 显示事件名称和剩余时间
            timer_text = f"{event_data['name']} ({event_data['timer']:.1f}s)"
            event_text = font_event.render(timer_text, True, event_data["color"])
            SCREEN.blit(event_text, (SCREEN_WIDTH - 200, event_y))
            event_y += 25

    # 生命值不足警告
    if low_life_warning and low_life_timer > 0:
        font_warn = get_font( 48)
        warn_text = font_warn.render("❤️ 生命值告急!", True, RED)
        # 闪烁效果
        if int(low_life_timer * 5) % 2 == 0:
            SCREEN.blit(warn_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 100))

    # 绘制胜利画面
    if game_complete_time is not None:
        # 绘制庆祝特效
        if state.celebration_effect:
            state.celebration_effect.update(dt)
            state.celebration_effect.draw(SCREEN)
        if state.stage_complete_effect:
            state.stage_complete_effect.update(dt)
            state.stage_complete_effect.draw(SCREEN)
        stats['waves_completed'] = state.wave
        draw_end_report(SCREEN, True, stats, game_complete_time)
    
    # 绘制失败画面
    if state.game_over:
        stats['waves_completed'] = state.wave - 1 if state.wave > 0 else 0
        draw_end_report(SCREEN, False, stats, display_time)

    # 底部技能按钮面板
    skill_bar_y = SCREEN_HEIGHT - 50

    # 技能按钮 (带冷却显示)
    skills = [
        ("Q", "减速技能", CYAN, 'slow'),
        ("W", "冰冻技能", BLUE, 'freeze'),
        ("E", "群攻技能", RED, 'aoe'),
    ]

    for i, (key, name, color, skill_id) in enumerate(skills):
        bx = 150 + i * 100
        by = skill_bar_y
        
        # 检测技能状态
        is_active = False
        cooldown = 0
        cooldown_max = 15 if skill_id == 'slow' else 20 if skill_id == 'freeze' else 25
        
        if skill_id == 'slow':
            is_active = getattr(state, 'slow_skill_active', False)
            cooldown = getattr(state, 'slow_skill_cooldown', 0)
        elif skill_id == 'freeze':
            is_active = getattr(state, 'freeze_skill_active', False)
            cooldown = getattr(state, 'freeze_skill_cooldown', 0)
        elif skill_id == 'aoe':
            is_active = getattr(state, 'aoe_skill_active', False)
            cooldown = getattr(state, 'aoe_skill_cooldown', 0)
        
        # 按钮背景 - 激活时高亮,冷却时变暗
        if is_active:
            bg_color = (80, 80, 120)  # 激活时更亮
            border_color = WHITE
        elif cooldown > 0:
            bg_color = (30, 30, 40)  # 冷却时变暗
            border_color = (80, 80, 80)
        else:
            bg_color = (40, 40, 60)
            border_color = color
        
        pygame.draw.rect(SCREEN, bg_color, (bx, by, 80, 35), border_radius=5)
        # 边框
        pygame.draw.rect(SCREEN, border_color, (bx, by, 80, 35), 2, border_radius=5)
        
        # 冷却进度条
        if cooldown > 0:
            cd_ratio = cooldown / cooldown_max
            cd_width = int(76 * cd_ratio)
            pygame.draw.rect(SCREEN, (100, 100, 100), (bx + 2, by + 30, 76, 3))
            pygame.draw.rect(SCREEN, color, (bx + 2, by + 30, cd_width, 3))
        
        # 文字
        font_skill = get_font( 24)
        key_surf = font_skill.render(f"{key}: {name}", True, color if cooldown <= 0 and not is_active else (150, 150, 150))
        SCREEN.blit(key_skill, (bx + 3, by + 5))
        
        # 激活/冷却提示
        if is_active:
            active_surf = font_skill.render("●", True, (0, 255, 0))
            SCREEN.blit(active_surf, (bx + 60, by + 5))
        elif cooldown > 0:
            cd_surf = font_skill.render(f"{int(cooldown)}", True, (200, 200, 200))
            SCREEN.blit(cd_surf, (bx + 58, by + 5))

    # 提示
    font_tip = get_font( 20)
    tip_surf = font_tip.render("快捷技能", True, GRAY)
    SCREEN.blit(tip_surf, (80, skill_bar_y + 10))

    # 底部操作提示
    font_hint = get_font( 22)
    # 修复：更清晰的提示，说明需要先按1-5选择塔，再点击地图放置
    hint_text = f"📌 1-5选择塔 | R范围 | S商店 | H血量 | T统计 | 波次: {state.wave} | 金币: {state.money} | 生命: {state.lives}"
    hint_surf = font_hint.render(hint_text, True, (180, 180, 180))
    SCREEN.blit(hint_surf, (10, SCREEN_HEIGHT - 30))

    # ==================== 精致UI边框和动画效果 ====================
    draw_ui_border()
    draw_skill_cooldown_panel()
    draw_button_hover()

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

    # 绘制升级光柱特效 (新)
    for effect in upgrade_beam_effects[:]:
        effect.update(dt)
        effect.draw(SCREEN)
        if not effect.active:
            upgrade_beam_effects.remove(effect)

    # 绘制塔选中脉冲特效 (新) - 选中塔时持续显示
    if state.selected_tower and state.selected_tower.alive:
        # 检查是否已有该塔的脉冲效果
        existing_pulse = None
        for pulse in tower_selection_pulses:
            if pulse.x == int(state.selected_tower.x) and pulse.y == int(state.selected_tower.y):
                existing_pulse = pulse
                break
        if existing_pulse:
            existing_pulse.update(dt)
            existing_pulse.draw(SCREEN)
        else:
            # 创建新的脉冲效果
            new_pulse = TowerSelectionPulse(int(state.selected_tower.x), int(state.selected_tower.y), 60)
            tower_selection_pulses.append(new_pulse)
            new_pulse.update(dt)
            new_pulse.draw(SCREEN)

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

        font_up = get_font( 24)
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

    # 绘制死亡爆炸特效
    for ef in death_effects[:]:
        ef[2] -= dt * game_speed
        x, y, timer, color = ef
        # 爆炸扩散圈
        progress = 0.5 - timer  # 0到0.5
        radius = int(30 * (1 - progress * 2))
        if radius > 0:
            # 外圈
            pygame.draw.circle(SCREEN, color, (x + shake_x, y + shake_y), radius, 3)
            # 内圈
            pygame.draw.circle(SCREEN, (255, 200, 150), (x + shake_x, y + shake_y), max(1, radius - 5), 2)
        if timer <= 0:
            death_effects.remove(ef)

    # 绘制暴击特效
    for ce in crit_effects[:]:
        ce[2] -= dt * game_speed
        cx, cy, timer = ce
        
        # 暴击文字
        font_crit = get_font( 40)
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
            font_big = get_font( 120)
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
            font_tip = get_font( 36)
            tip_surf = font_tip.render("下一波即将来临!", True, WHITE)
            tip_rect = tip_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            SCREEN.blit(tip_surf, tip_rect)

    # 显示统计面板
    if show_stats:
        stats_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 200)
        pygame.draw.rect(SCREEN, (0, 0, 180), stats_rect)
        pygame.draw.rect(SCREEN, YELLOW, stats_rect, 2)

        font_stats = get_font( 28)
        y = stats_rect.y + 20
        for key, label in [("kills", "击杀"), ("towers_built", "建造"), ("towers_upgraded", "升级"), ("gold_spent", "花费"), ("gold_earned", "获得")]:
            text = font_stats.render(f"{label}: {stats[key]}", True, WHITE)
            SCREEN.blit(text, (stats_rect.x + 20, y))
            y += 30

    # 绘制成就徽章（右上角）
    draw_achievement_badges()
    
    # 绘制每日任务面板
    draw_quest_panel()

    # 绘制塔图鉴
    if show_tower_book:
        draw_tower_book()
    
    # 绘制怪物图鉴
    if show_monster_book:
        draw_monster_book()

    # 绘制背包面板
    if show_inventory:
        draw_inventory_panel()
    
    # 绘制波次预览面板
    if show_wave_preview:
        draw_wave_preview_panel()
    
    # 绘制粒子特效
    draw_particles()
    # 绘制塔基特效
    global_base_effect_manager.draw(SCREEN)
    # 绘制伤害数字
    global_damage_number_manager.draw(SCREEN)
    # 绘制连击文字
    if combo_system:
        combo_system.render(SCREEN)
    
    # 绘制Boss警告特效
    for effect in boss_warning_effects:
        effect.draw(SCREEN)
    
    # 更新和绘制升级光晕特效
    global_particle_system.update_upgrade_aura()
    global_particle_system.draw_upgrade_aura(SCREEN)

# 波次预览系统
def draw_wave_preview_panel():
    """绘制波次预览面板 - 按Tab查看"""
    global show_wave_preview
    if not show_wave_preview:
        return
    
    panel_w, panel_h = 320, 280
    panel_x = SCREEN_WIDTH // 2 - panel_w // 2
    panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
    
    # 背景 - 渐变效果
    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    # 顶部渐变
    for y in range(panel_h):
        alpha = int(200 + 55 * (y / panel_h))
        pygame.draw.line(s, (15, 15, 35, min(alpha, 245)), (0, y), (panel_w, y))
    SCREEN.blit(s, (panel_x, panel_y))
    
    # 边框发光效果
    glow_rect = pygame.Rect(panel_x - 2, panel_y - 2, panel_w + 4, panel_h + 4)
    pygame.draw.rect(SCREEN, (80, 120, 200), glow_rect, 3, border_radius=12)
    pygame.draw.rect(SCREEN, (100, 150, 255), (panel_x, panel_y, panel_w, panel_h), 2, border_radius=8)
    
    # 标题
    font = get_font(28)
    title = font.render("📋 波次预览", True, (255, 215, 0))
    SCREEN.blit(title, (panel_x + 20, panel_y + 12))
    
    # 关闭提示
    font_small = get_font(16)
    close_hint = font_small.render("[Tab] 关闭", True, (120, 120, 140))
    SCREEN.blit(close_hint, (panel_x + panel_w - 100, panel_y + 18))
    
    # 波次信息
    current_wave = state.wave_manager.current_wave + 1 if hasattr(state, 'wave_manager') else 1
    total_waves = len(state.wave_manager.waves) if hasattr(state, 'wave_manager') else 8
    
    font2 = get_font(20)
    wave_progress = f"第 {current_wave} 波 / 共 {total_waves} 波"
    info = font2.render(wave_progress, True, (220, 220, 220))
    SCREEN.blit(info, (panel_x + 20, panel_y + 48))
    
    # 进度条
    progress_w = panel_w - 40
    progress_ratio = current_wave / max(total_waves, 1)
    pygame.draw.rect(SCREEN, (40, 40, 60), (panel_x + 20, panel_y + 72, progress_w, 8), border_radius=4)
    pygame.draw.rect(SCREEN, (100, 180, 100), (panel_x + 20, panel_y + 72, int(progress_w * progress_ratio), 8), border_radius=4)
    
    # 分割线
    pygame.draw.line(SCREEN, (60, 70, 90), (panel_x + 20, panel_y + 92), (panel_x + panel_w - 20, panel_y + 92), 1)
    
    # 接下来几波怪物预览 - 增强版
    preview_y = panel_y + 100
    wave_labels = ["下一波", "第+2波", "第+3波"]
    
    # 怪物类型颜色映射
    monster_colors = {
        'slime': (100, 200, 100),
        'bat': (150, 100, 200),
        'wolf': (180, 120, 80),
        'ghost': (150, 150, 200),
        'boss': (200, 50, 50),
    }
    
    for i, label in enumerate(wave_labels):
        wave_num = current_wave + i
        if wave_num <= total_waves and hasattr(state, 'wave_manager'):
            wave_data = state.wave_manager.waves[wave_num - 1]
            monster_list = wave_data.get('monsters', [])
            total_monsters = sum(count for _, count in monster_list)
            
            # 难度评估
            difficulty = wave_data.get('difficulty', 1.0 + i * 0.2)
            diff_color = (100, 255, 100) if difficulty < 1.5 else (255, 200, 100) if difficulty < 2.5 else (255, 100, 100)
            diff_stars = min(3, int(difficulty / 1.0))
            
            # 行背景
            row_bg = pygame.Rect(panel_x + 15, preview_y + i * 50 - 5, panel_w - 30, 45)
            pygame.draw.rect(SCREEN, (30, 35, 50), row_bg, border_radius=6)
            
            # 波次标签
            label_text = font2.render(f"{label}", True, (180, 180, 200))
            SCREEN.blit(label_text, (panel_x + 25, preview_y + i * 50))
            
            # 怪物图标和数量
            monster_text = f"👾 x{total_monsters}"
            monster_render = font_small.render(monster_text, True, (150, 220, 255))
            SCREEN.blit(monster_render, (panel_x + 25, preview_y + i * 50 + 22))
            
            # 难度星星
            stars_text = "★" * diff_stars + "☆" * (3 - diff_stars)
            stars_render = font_small.render(stars_text, True, diff_color)
            SCREEN.blit(stars_render, (panel_x + panel_w - 90, preview_y + i * 50 + 22))

# 塔图鉴
def draw_tower_book():
    """绘制塔图鉴界面"""
    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    SCREEN.blit(overlay, (0, 0))
    
    # 标题
    font_title = get_font( 50)
    title = font_title.render("📖 塔图鉴", True, GOLD)
    SCREEN.blit(title, (SCREEN_WIDTH//2 - 60, 50))
    
    # 塔类型信息
    towers_info = [
        ("箭塔", "远程单体", "蓝色三角形", "射速快"),
        ("炮塔", "范围伤害", "红色正方形", "伤害高"),
        ("魔法塔", "高伤害", "紫色菱形", "进阶塔"),
        ("减速塔", "减速敌人", "青色菱形", "辅助塔"),
    ]
    
    font_info = get_font( 28)
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
    font_tip = get_font( 24)
    tip = font_tip.render("按 I 键关闭图鉴", True, YELLOW)
    SCREEN.blit(tip, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT - 50))

# 怪物图鉴
def draw_monster_book():
    """绘制怪物图鉴界面"""
    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    SCREEN.blit(overlay, (0, 0))
    
    font_title = get_font( 50)
    title = font_title.render("🐛 怪物图鉴", True, GOLD)
    SCREEN.blit(title, (SCREEN_WIDTH//2 - 70, 30))
    
    monsters_info = [
        ("小怪物", "普通", "5", "1.0", "蓝色圆形"),
        ("中怪物", "普通", "15", "1.0", "蓝色圆形"),
        ("大怪物", "精英", "30", "1.2", "蓝色圆形"),
        ("快速怪", "特殊", "10", "2.0", "绿色三角"),
        ("装甲怪", "坦克", "50", "0.5", "灰色方形"),
        ("Boss", "首领", "100", "0.3", "大红圆+光环"),
        ("超级Boss", "终极", "200", "0.2", "大红圆+光环"),
    ]
    
    font_info = get_font( 26)
    for i, (name, type_, hp, speed, shape) in enumerate(monsters_info):
        y = 90 + i * 40
        
        # 怪物形状示例
        cx, cy = 100, y + 15
        
        if "Boss" in name:
            pygame.draw.circle(SCREEN, (180, 0, 0), (cx, cy), 16)
            pygame.draw.circle(SCREEN, (255, 50, 50), (cx, cy), 12)
            pygame.draw.circle(SCREEN, (255, 0, 0), (cx, cy), 20, 2)
        elif "装甲" in name:
            pygame.draw.rect(SCREEN, (100, 100, 100), (cx - 10, cy - 10, 20, 20))
        elif "快速" in name:
            points = [(cx, cy - 12), (cx - 8, cy + 8), (cx + 8, cy + 8)]
            pygame.draw.polygon(SCREEN, (50, 180, 50), points)
        else:
            pygame.draw.circle(SCREEN, (50, 100, 200), (cx, cy), 10)
        
        # 文字
        text = f"{name} | {type_} | 血量:{hp} | 速度:{speed}"
        surf = font_info.render(text, True, WHITE)
        SCREEN.blit(surf, (150, y))
    
    font_tip = get_font( 24)
    tip = font_tip.render("按 J 键关闭图鉴", True, YELLOW)
    SCREEN.blit(tip, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT - 50))

# 主循环
def main():
    """主循环"""
    global game_start_time, display_time, game_complete_time, game_speed
    global no_money_timer, wave_tip_timer, low_life_warning, low_life_timer
    global kill_streak, kill_streak_timer, game_difficulty
    global last_event_check, combo_text, combo_texts
    global show_health_detail, show_stats, show_tower_book, show_monster_book
    global show_wave_preview, wave_wait_timer, final_wave_announced
    global boss_bar_drawn, music_enabled, screen_shake
    global total_kills, achievement_timer, quest_timer
    global wave_no_damage, level_select_mode, selected_level, difficulty_selected
    global fps_counter, fps_timer, fps
    global kills_this_wave, wave_wait_duration
    global gold_rain_active, double_damage_active, slow_all_active
    global inventory, show_inventory
    global crit_effects, upgrade_info_display
    global place_effects, death_effects, upgrade_effects
    global coin_animations, quest_notify, achievement_unlock_anim
    global daily_quests, last_daily_key
    global wave_tip, egg_input_buffer, easter_egg_active
    global lights, particles, lines
    global screen_shake_offset, time_str, show_achievement_unlock
    global global_base_effect_manager, global_particle_system, global_damage_number_manager
    
    # 初始化游戏
    init_game()
    
    # 初始化粒子系统（等待难度选择完成后重新初始化）
    # 注意：这里不直接初始化，等难度选择完成后再初始化完整游戏对象
    
    clock = pygame.time.Clock()
    running = True

    # 初始化游戏开始时间
    game_start_time = time.time()
    
# 初始化每日挑战
    today_challenge = get_today_challenge()
    daily_challenge["active"] = True
    daily_challenge["type"] = today_challenge["type"]
    daily_challenge["description"] = today_challenge["name"] + "\n" + today_challenge["desc"]
    daily_challenge["bonus_gold"] = today_challenge["bonus"]
    # 检查并重置每日任务
    check_daily_reset()

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        effective_dt = dt * game_speed  # 应用游戏速度

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # 关卡选择(游戏开始前)
                if level_select_mode:
                    levels = config.get("levels", [])
                    if event.key == pygame.K_UP:
                        selected_level = (selected_level - 1) % len(levels)
                    elif event.key == pygame.K_DOWN:
                        selected_level = (selected_level + 1) % len(levels)
                    elif event.key == pygame.K_RETURN:
                        # 确认选择关卡，进入难度选择
                        level_select_mode = False
                        difficulty_selected = False  # 进入难度选择
                        selected_level_data = levels[selected_level]
                        print(f"已选择关卡: {selected_level_data['name']}, 请选择难度")
                    elif event.key == pygame.K_ESCAPE:
                        # 退出游戏
                        running = False
                
                # 难度选择(关卡选择后)
                if not difficulty_selected:
                    if event.key == pygame.K_1:
                        game_difficulty = DIFFICULTY_EASY
                        difficulty_selected = True
                        init_new_game()
                    elif event.key == pygame.K_2:
                        game_difficulty = DIFFICULTY_NORMAL
                        difficulty_selected = True
                        init_new_game()
                    elif event.key == pygame.K_3:
                        game_difficulty = DIFFICULTY_HARD
                        difficulty_selected = True
                        init_new_game()
                    elif event.key == pygame.K_RETURN:
                        # 按回车也确认当前难度
                        difficulty_selected = True
                        init_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        # 返回关卡选择
                        level_select_mode = True
                        difficulty_selected = False

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
                # D键出售选中塔
                elif event.key == pygame.K_d and state.selected_tower:
                    tower = state.selected_tower
                    sell_price = int(tower.get_upgrade_cost() * 0.5)
                    state.money += sell_price
                    # 出售特效
                    spawn_particles(int(tower.x), int(tower.y), (255, 200, 100), 20)
                    spawn_particles(int(tower.x), int(tower.y), (255, 150, 50), 15)
                    state.towers.remove(tower)
                    state.selected_tower = None
                    stats["gold_earned"] += sell_price
                    sound_manager.play('sell')
                    print(f"💰 出售塔，返还{sell_price}金币")
                    
                    # 成就: 首次出售
                    if not achievements["sell_tower"]["unlocked"]:
                        achievements["sell_tower"]["unlocked"] = True
                        achievement_notify = f"🏆 解锁: {achievements['sell_tower']['name']}"
                        achievement_timer = 3.0
                        show_achievement_unlock("首次出售", "💰")
                
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

                            # 播放升级音效
                            sound_manager.play('upgrade')

                            # 升级成功特效
                            upgrade_effects.append([int(tower.x), int(tower.y), 1.0])
                            particle_system.add_upgrade_aura(int(tower.x), int(tower.y), tower.level)
                            # 新增：升级光柱特效
                            upgrade_beam_effects.append(UpgradeBeamEffect(int(tower.x), int(tower.y), tower.level))
                            trigger_screen_shake(3, 0.1)
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
                                show_achievement_unlock("首次升级", "⬆️")
                        else:
                            # 金币不足警告
                            no_money_warning = "💰 金币不足!"
                            no_money_timer = 1.5
                # R键切换攻击范围显示
                elif event.key == pygame.K_r:
                    global show_attack_range
                    show_attack_range = not show_attack_range
                    print(f"🎯 攻击范围显示: {'开启' if show_attack_range else '关闭'}")
                # T键切换统计面板
                elif event.key == pygame.K_t:
                    global show_stats
                    show_stats = not show_stats
                # M键切换音效
                elif event.key == pygame.K_m:
                    enabled = sound_manager.toggle()
                    if enabled:
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
                elif event.key == pygame.K_4:
                    config['tower_selection'] = '冰霜塔'
                # Q/W/E技能按键 (带冷却)
                elif event.key == pygame.K_q:
                    # 减速技能 - 5秒内所有怪物减速50%
                    if not hasattr(state, 'slow_skill_active') or not state.slow_skill_active:
                        state.slow_skill_active = True
                        state.slow_skill_timer = 5.0
                        for monster in state.monsters:
                            monster.apply_slow(0.5, 5.0)
                        # 技能特效
                        trigger_screen_shake(5, 0.1)
                        spawn_particles(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, (100, 200, 255), 30)
                        print("❄️ 减速技能激活! 敌人减速50%")
                elif event.key == pygame.K_w:
                    # 冰冻技能 - 冻结所有怪物3秒
                    if not hasattr(state, 'freeze_skill_active') or not state.freeze_skill_active:
                        state.freeze_skill_active = True
                        state.freeze_skill_timer = 3.0
                        for monster in state.monsters:
                            monster.frozen = 180  # 3秒(60fps)
                        # 技能特效
                        trigger_screen_shake(8, 0.15)
                        spawn_particles(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, (150, 230, 255), 40)
                        print("🧊 冰冻技能激活! 敌人冻结3秒")
                elif event.key == pygame.K_e:
                    # 群攻技能 - 对所有怪物造成50点伤害
                    if not hasattr(state, 'aoe_skill_active') or not state.aoe_skill_active:
                        state.aoe_skill_active = True
                        state.aoe_skill_timer = 10.0
                        damage = 50
                        for monster in state.monsters[:]:
                            monster.health -= damage
                            if global_damage_number_manager:
                                mx = 100 + monster.position * 600
                                global_damage_number_manager.add_damage(int(mx), 280, damage, False)
                        # 技能特效
                        trigger_screen_shake(15, 0.2)
                        spawn_particles(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, (255, 100, 50), 50)
                        print(f"💥 群攻技能激活! 造成{damage}点伤害")
                # I键打开/关闭塔图鉴
                elif event.key == pygame.K_i:
                    global show_tower_book
                    show_tower_book = not show_tower_book
                # J键打开/关闭怪物图鉴
                elif event.key == pygame.K_j:
                    global show_monster_book
                    show_monster_book = not show_monster_book
                # B键打开/关闭背包
                elif event.key == pygame.K_b:
                    global show_inventory
                    show_inventory = not show_inventory
                # Tab键打开/关闭波次预览
                elif event.key == pygame.K_TAB:
                    global show_wave_preview
                    show_wave_preview = not show_wave_preview

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
                                    # 播放建造音效
                                    sound_manager.play('build')
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
                kills_this_wave = 0  # 重置波次击杀计数
                # 播放波次开始音效
                sound_manager.play('wave_start')
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
                show_achievement_unlock("无伤波次", "🛡️")
            wave_no_damage = True  # 重置下一波检测
            wave_wait_timer = wave_wait_duration
            
            # ===== 波次完成庆祝动画 =====
            if global_particle_system:
                global_particle_system.emit_explosion(SCREEN_WIDTH//2, 100, (255, 215, 0), count=30)
                global_particle_system.emit(SCREEN_WIDTH//2, 100, 20, (255, 255, 255), lifetime=1.5, size=8, speed=80, upward=True)
            
            # ===== 每日任务进度更新 =====
            update_quest("wave_5")

        # ==================== 技能系统更新 ====================
        if hasattr(state, 'slow_skill_active'):
            # 减速技能
            if state.slow_skill_active:
                state.slow_skill_timer -= effective_dt
                if state.slow_skill_timer <= 0:
                    state.slow_skill_active = False
                    state.slow_skill_cooldown = 15.0
            elif state.slow_skill_cooldown > 0:
                state.slow_skill_cooldown -= effective_dt
            
            # 冰冻技能
            if state.freeze_skill_active:
                state.freeze_skill_timer -= effective_dt
                if state.freeze_skill_timer <= 0:
                    state.freeze_skill_active = False
                    state.freeze_skill_cooldown = 20.0
            elif state.freeze_skill_cooldown > 0:
                state.freeze_skill_cooldown -= effective_dt
            
            # 群攻技能
            if state.aoe_skill_active:
                state.aoe_skill_timer -= effective_dt
                if state.aoe_skill_timer <= 0:
                    state.aoe_skill_active = False
                    state.aoe_skill_cooldown = 25.0
            elif state.aoe_skill_cooldown > 0:
                state.aoe_skill_cooldown -= effective_dt

        # 检查胜利条件(所有波次完成且无怪物)
        if not state.wave_manager.has_more_waves() and state.wave_manager.is_wave_complete() and not state.monsters and state.wave > 0:
            if game_complete_time is None:
                game_complete_time = display_time
                # 触发关卡完成庆祝特效
                stars = 3 if state.lives >= 7 else (2 if state.lives >= 4 else 1)
                score = int(display_time * 10 + state.lives * 100)
                state.stage_complete_effect = StageCompleteEffect(SCREEN_WIDTH, SCREEN_HEIGHT, score, stars)
                state.celebration_effect = CelebrationEffect(SCREEN_WIDTH, SCREEN_HEIGHT)
                state.celebration_effect.start()
                # 播放胜利音效
                sound_manager.play('victory')
                # 成就: 速通(3分钟内)
                if display_time < 180 and not achievements["fast_win"]["unlocked"]:
                    achievements["fast_win"]["unlocked"] = True
                    achievement_notify = f"🏆 解锁: {achievements['fast_win']['name']}"
                    achievement_timer = 3.0
                    show_achievement_unlock("速通", "⚡")

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

        # 更新粒子特效
        update_particles(effective_dt)
        # 更新塔基特效
        if global_base_effect_manager:
            global_base_effect_manager.update(effective_dt)
        # 更新伤害数字
        if global_damage_number_manager:
            global_damage_number_manager.update(effective_dt)
        # 更新连击系统
        if combo_system:
            combo_system.update(effective_dt)
        
        # 更新Boss警告特效
        for effect in boss_warning_effects[:]:
            effect.update(effective_dt)
            if not effect.active:
                boss_warning_effects.remove(effect)

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
                # 触发屏幕震动（怪物到达终点）
                trigger_screen_shake(10, 0.2)
                if state.lives <= 0:
                    state.game_over = True
        # 检查每日挑战完成情况
        check_challenge_completion(state, game_complete_time if 'game_complete_time' in dir() else None, show_achievement_unlock if 'show_achievement_unlock' in dir() else None)
        # 播放失败音效
        sound_manager.play('defeat')
        wave_no_damage = False  # 掉血了

        # 塔攻击逻辑 - 添加组合系统
        for tower in state.towers:
            old_projectile_count = len(state.projectiles)
            # 计算并应用协同加成
            synergy_manager = get_synergy_manager()
            synergy_manager.calculate_synergies(state.towers, pygame.time.get_ticks())
            
            # 保存原始属性
            original_damage = tower.damage
            original_speed = tower.attack_speed
            
            # 应用协同加成
            damage_mult = synergy_manager.get_synergy_bonus(tower, "damage")
            speed_mult = synergy_manager.get_synergy_bonus(tower, "attack_speed")
            tower.damage = int(tower.damage * damage_mult)
            tower.attack_speed = tower.attack_speed * speed_mult
            
            tower.attack(state.monsters, state.projectiles, state.towers)
            
            # 恢复原始属性
            tower.damage = original_damage
            tower.attack_speed = original_speed
            
            # 检测是否发射了新子弹，触发塔基特效
            if len(state.projectiles) > old_projectile_count:
                if global_base_effect_manager:
                    global_base_effect_manager.trigger_attack_effect(tower)
        
        # 清空Combo Strike计数（每帧重新计算）
        Tower._combo_targets.clear()

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
                    # 显示伤害数字
                    if global_damage_number_manager:
                        global_damage_number_manager.add_damage(int(mx_monster), 280, actual_damage, is_crit)
                    # 记录连击
                    if combo_system:
                        combo_system.add_kill(int(mx_monster), 280, is_crit)
                    # 记录击杀来源塔
                    source_tower = getattr(projectile, 'source_tower', None)
                    if monster.health <= 0:  # 怪物死亡
                        # 添加死亡爆炸特效
                        if len(death_effects) < MAX_DEATH_EFFECTS:
                            death_effects.append([int(mx), int(my), 0.5, (255, 100, 50)])
                        # 增加塔的击杀计数
                        if source_tower and hasattr(source_tower, 'kill_count'):
                            source_tower.kill_count += 1

                        reward = 10  # 金币奖励
                        
                        # 随机事件：金币雨 - 击杀额外金币
                        if random_events["gold_rain"]["active"]:
                            reward += 5
                        
                        # 暴击检测（10%几率）
                        is_crit = random.random() < 0.1
                        if is_crit:
                            crit_effects.append([int(mx), int(my), 1.0])
                            reward *= 2  # 暴击金币翻倍
                            trigger_screen_shake(5, 0.1)  # 暴击震动
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
                        kills_this_wave += 1  # 波次击杀计数
                        
                        # 大量击杀时触发屏幕震动
                        if kills_this_wave >= 10:
                            trigger_screen_shake(8, 0.2)
                            kills_this_wave = 0  # 重置计数
                        
                        stats["damage_dealt"] += projectile.damage
                        stats["gold_earned"] += reward + bonus
                        
                        # ===== 每日任务进度更新 =====
                        global total_gold_earned_session
                        total_gold_earned_session += reward + bonus
                        update_quest("earn_500", reward + bonus)
                        coin_animations.append([mx, 280, f"+{reward}", 1.0])
                        if bonus > 0:
                            coin_animations.append([mx + 30, 280, f"+{bonus}(连杀)", 1.5])
                        # 播放金币音效
                        if bonus > 0:
                            sound_manager.play('crit')  # 连杀时播放暴击音效
                        else:
                            sound_manager.play('coin')
                        if monster in state.monsters:
                            # 怪物死亡粒子特效
                            spawn_particles(mx, 300, (255, 200, 0), 15)  # 金色粒子
                            spawn_particles(mx, 300, (255, 100, 0), 10)  # 橙色粒子
                            
                            state.monsters.remove(monster)
                            # 成就: 击杀相关
                            total_kills += 1
                            
                            # ===== 每日任务进度更新 =====
                            update_quest("kill_30")
                            if not achievements["first_blood"]["unlocked"]:
                                achievements["first_blood"]["unlocked"] = True
                                achievement_notify = f"🏆 解锁: {achievements['first_blood']['name']}"
                                achievement_timer = 3.0
                                show_achievement_unlock("首次击杀", "🎯")
                            if total_kills >= 10 and not achievements["ten_kills"]["unlocked"]:
                                achievements["ten_kills"]["unlocked"] = True
                                achievement_notify = f"🏆 解锁: {achievements['ten_kills']['name']}"
                                achievement_timer = 3.0
                                show_achievement_unlock("击杀10只", "💀")
                            if total_kills >= 50 and not achievements["fifty_kills"]["unlocked"]:
                                achievements["fifty_kills"]["unlocked"] = True
                                achievement_notify = f"🏆 解锁: {achievements['fifty_kills']['name']}"
                                achievement_timer = 3.0
                                show_achievement_unlock("击杀50只", "💀")
                    break

        # 处理签到事件 (K键签到)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    success, reward = try_checkin()
                    if success:
                        state.money += reward
                        print(f"✅ 签到成功! 连续{checkin_data['streak']}天, 奖励{reward}金币")
                    else:
                        print("⚠️ 今日已签到")

        # 绘制游戏画面
        if level_select_mode:
            draw_level_select()
        elif not difficulty_selected:
            draw_difficulty_screen()
        else:
            draw_game()

        # 绘制签到面板
        draw_checkin_panel(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GOLD, YELLOW)
        fps_counter += 1
        fps_timer += dt
        if fps_timer >= 1.0:
            fps = int(fps_counter / fps_timer)
            fps_counter = 0
            fps_timer = 0

        # 绘制游戏画面
        if level_select_mode:
            draw_level_select()
        elif not difficulty_selected:
            draw_difficulty_screen()
        else:
            draw_game()

        # 暂停时显示详细信息
        if state.paused:
            # 半透明遮罩
            pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 150))
            SCREEN.blit(pause_overlay, (0, 0))

            font_title = get_font( 64)
            title = font_title.render("⏸️ 暂停", True, WHITE)
            SCREEN.blit(title, (SCREEN_WIDTH//2 - 80, 100))

            # 显示当前状态
            font_info = get_font( 28)
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
            font_hint = get_font( 24)
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
        
        # 每帧刷新显示
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
