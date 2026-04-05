"""
保卫萝卜 - 怪物系统
"""

class Monster:
    """怪物基类"""
    
    def __init__(self, name, health, speed, reward, monster_type="normal"):
        self.name = name
        self.health = health
        self.max_health = health
        self.speed = speed
        self.original_speed = speed  # 原始速度，用于减速后恢复
        self.reward = reward
        self.monster_type = monster_type
        self.position = 0  # 0-1 表示在路径上的位置
        self.frozen = 0  # 冰冻时间(帧)
        self.slow_timer = 0  # 减速持续时间(秒)
        self.slow_factor = 1.0  # 当前减速因子(1.0=无减速)
        self.alive = True
        self.x = 100  # 屏幕坐标
        self.y = 300
        self.is_boss = (monster_type == "Boss" or monster_type == "超级Boss")
        
    def take_damage(self, damage):
        """受到伤害"""
        self.health -= damage
        if self.health <= 0:
            self.alive = False
        return self.health <= 0
    
    def apply_slow(self, slow_factor, duration):
        """应用减速效果 - 多个减速效果叠加时取最大值"""
        if slow_factor < self.slow_factor:  # 取最大减速效果
            self.slow_factor = slow_factor
            self.speed = self.original_speed * slow_factor
        self.slow_timer = max(self.slow_timer, duration)  # 延长的减速持续时间

    def slow(self, duration):
        """减速效果（兼容旧接口）"""
        self.frozen = duration
        
    def update(self, dt):
        """更新减速计时器"""
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                # 减速结束，恢复原始速度
                self.slow_timer = 0
                self.slow_factor = 1.0
                self.speed = self.original_speed

    def move(self, dt):
        """移动"""
        self.update(dt)  # 更新减速状态
        if self.frozen > 0:
            self.frozen -= 1
            return False  # 被冰冻，无法移动
        self.position += self.speed * dt
        return self.position >= 1  # 到达终点
    
    def __str__(self):
        return f"{self.name} 💜{self.health}/{self.max_health} ⚡{self.speed}"


class MonsterFactory:
    """怪物工厂"""
    
    MONSTERS = {
        "小怪物": {"health": 50, "speed": 0.01, "reward": 10, "color": "green"},
        "中怪物": {"health": 100, "speed": 0.008, "reward": 20, "color": "yellow"},
        "大怪物": {"health": 200, "speed": 0.006, "reward": 40, "color": "orange"},
        "Boss": {"health": 500, "speed": 0.004, "reward": 100, "color": "red"},
        "超级Boss": {"health": 1000, "speed": 0.003, "reward": 300, "color": "purple"},
    }
    
    @classmethod
    def create(cls, name):
        """创建怪物"""
        if name not in cls.MONSTERS:
            return None
        stats = cls.MONSTERS[name]
        return Monster(name, stats["health"], stats["speed"], stats["reward"], name)
    
    @classmethod
    def list_monsters(cls):
        """列出所有怪物类型"""
        return list(cls.MONSTERS.keys())