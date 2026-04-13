# 每日挑战系统
import datetime
import pygame

daily_challenge = {
    "active": False,
    "type": None,  # "speed", "survival", "economy", "no_magic"
    "description": "",
    "bonus_gold": 0,
    "completed": False
}

CHALLENGES = [
    {"type": "speed", "name": "⚡ 速通挑战", "desc": "5分钟内通关", "bonus": 500},
    {"type": "survival", "name": "🛡️ 生存挑战", "desc": "生命不低于3通关", "bonus": 300},
    {"type": "economy", "name": "💰 理财挑战", "desc": "通关时金币≥500", "bonus": 400},
    {"type": "no_magic", "name": "🔮 禁用法术", "desc": "不使用法术塔通关", "bonus": 200},
]

def get_today_challenge():
    """获取今日挑战"""
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    return CHALLENGES[day_of_year % len(CHALLENGES)]

def check_challenge_completion(state, game_complete_time=None, show_achievement_unlock=None):
    """检查挑战是否完成
    
    Args:
        state: 游戏状态对象
        game_complete_time: 通关时间(秒),可选
        show_achievement_unlock: 成就解锁回调函数,可选
    """
    if not daily_challenge["active"] or daily_challenge["completed"]:
        return
    
    challenge_type = daily_challenge["type"]
    completed = False
    
    if challenge_type == "speed":
        if game_complete_time is not None and game_complete_time <= 300:  # 5分钟
            completed = True
    elif challenge_type == "survival":
        if hasattr(state, 'lives') and hasattr(state, 'game_over') and state.lives >= 3 and state.game_over:
            completed = True
    elif challenge_type == "economy":
        if hasattr(state, 'money') and hasattr(state, 'game_over') and state.money >= 500 and state.game_over:
            completed = True
    elif challenge_type == "no_magic":
        # 检查是否使用过法术塔
        if hasattr(state, 'towers'):
            # 使用name属性判断，因为Tower类没有type属性
            magic_used = any("魔法" in getattr(t, 'name', '') for t in state.towers)
            if not magic_used and hasattr(state, 'game_over') and state.game_over:
                completed = True
    
    if completed:
        daily_challenge["completed"] = True
        if hasattr(state, 'money'):
            state.money += daily_challenge["bonus_gold"]
        if show_achievement_unlock:
            show_achievement_unlock(f"🎯 今日挑战完成! +{daily_challenge['bonus_gold']}金币", "🏆")

def draw_daily_challenge_panel(SCREEN, SCREEN_WIDTH=800, SCREEN_HEIGHT=600):
    """绘制每日挑战面板"""
    if not daily_challenge["active"]:
        return
    
    panel_x, panel_y = SCREEN_WIDTH - 200, 100
    panel_w, panel_h = 180, 80
    
    # 背景
    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    SCREEN.blit(s, (panel_x, panel_y))
    
    # 边框
    color = (0, 255, 0) if daily_challenge["completed"] else (255, 200, 0)
    pygame.draw.rect(SCREEN, color, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=5)
    
    # 文字
    font = pygame.font.Font(None, 20)
    name = font.render(daily_challenge["description"], True, (255, 255, 255))
    bonus = font.render(f"+{daily_challenge['bonus_gold']}💰", True, (255, 215, 0))
    
    SCREEN.blit(name, (panel_x + 10, panel_y + 15))
    SCREEN.blit(bonus, (panel_x + 10, panel_y + 45))
    
    if daily_challenge["completed"]:
        check = font.render("✅ 完成!", True, (0, 255, 0))
        SCREEN.blit(check, (panel_x + 100, panel_y + 45))