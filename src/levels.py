"""
保卫萝卜 - 关卡系统
定义不同的游戏关卡
"""

class Level:
    """游戏关卡"""
    
    def __init__(self, level_number, wave_count, monster_types, reward):
        self.level_number = level_number
        self.wave_count = wave_count
        self.monster_types = monster_types
        self.reward = reward
        self.completed = False
    
    def __str__(self):
        return f"关卡 {self.level_number}: {self.wave_count} 波敌人，奖励 {self.reward}"

# 关卡定义
LEVELS = [
    Level(1, 3, ["小怪物"], 100),
    Level(2, 5, ["小怪物", "中怪物"], 200),
    Level(3, 8, ["小怪物", "中怪物", "大怪物"], 400),
    Level(4, 10, ["中怪物", "大怪物", "Boss"], 800),
    Level(5, 12, ["大怪物", "Boss", "超级Boss"], 1500),
]

def get_level(level_number):
    """获取指定关卡"""
    for level in LEVELS:
        if level.level_number == level_number:
            return level
    return None

def unlock_next_level(current_level):
    """解锁下一关"""
    if current_level >= len(LEVELS):
        return None
    return LEVELS[current_level]