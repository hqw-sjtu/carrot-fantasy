import datetime

# 签到系统
checkin_data = {
    "last_date": None,
    "streak": 0,
    "total_days": 0,
}

# 签到奖励
checkin_rewards = [50, 100, 150, 200, 300, 400, 500]  # 第1-7天

def try_checkin():
    today = datetime.date.today()
    
    if checkin_data["last_date"] is None:
        # 第一次签到
        checkin_data["streak"] = 1
        checkin_data["total_days"] = 1
        checkin_data["last_date"] = str(today)
        return True, checkin_rewards[0]
    
    last_date = datetime.date.fromisoformat(checkin_data["last_date"])
    days_diff = (today - last_date).days
    
    if days_diff == 0:
        return False, 0  # 已签到
    elif days_diff == 1:
        # 连续签到
        checkin_data["streak"] = min(7, checkin_data["streak"] + 1)
    else:
        # 断开，重新开始
        checkin_data["streak"] = 1
    
    checkin_data["total_days"] += 1
    checkin_data["last_date"] = str(today)
    
    reward = checkin_rewards[checkin_data["streak"] - 1]
    return True, reward

# 签到面板
def draw_checkin_panel(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GOLD, YELLOW):
    panel_x = SCREEN_WIDTH - 180
    panel_y = 200
    
    # 背景
    pygame.draw.rect(SCREEN, (40, 40, 60), (panel_x, panel_y, 170, 120), border_radius=8)
    pygame.draw.rect(SCREEN, GOLD, (panel_x, panel_y, 170, 120), 2, border_radius=8)
    
    font_title = pygame.font.Font(None, 22)
    title = font_title.render("📅 签到", True, GOLD)
    SCREEN.blit(title, (panel_x + 10, panel_y + 8))
    
    font_info = pygame.font.Font(None, 20)
    streak_text = f"连续: {checkin_data['streak']}天"
    total_text = f"总签到: {checkin_data['total_days']}天"
    
    SCREEN.blit(font_info.render(streak_text, True, WHITE), (panel_x + 10, panel_y + 35))
    SCREEN.blit(font_info.render(total_text, True, WHITE), (panel_x + 10, panel_y + 55))
    
    # 签到按钮提示
    tip = font_info.render("按 K 签到", True, YELLOW)
    SCREEN.blit(tip, (panel_x + 10, panel_y + 90))