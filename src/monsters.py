"""
保卫萝卜 - 怪物系统
"""

class Monster:
    """怪物基类"""
    
    # 怪物类型定义
    TYPE_NORMAL = "normal"
    TYPE_FAST = "fast"
    TYPE_ARMOR = "armor"
    TYPE_BOSS = "boss"
    
    def __init__(self, name, health, speed, reward, monster_type="normal"):
        self.name = name
        self.health = health
        self.max_health = health
        self.speed = speed
        self.original_speed = speed  # 原始速度，用于减速后恢复
        self.reward = reward
        self.monster_type = monster_type
        self.type = self._get_monster_type(monster_type)  # 用于绘制判断
        self.position = 0  # 0-1 表示在路径上的位置
        self.spawn_scale = 0.0  # 生成动画（从0缩放到1）
        self.frozen = 0  # 冰冻时间(帧)
        self.slow_timer = 0  # 减速持续时间(秒)
        self.slow_factor = 1.0  # 当前减速因子(1.0=无减速)
        # DOT (持续伤害) 状态
        self.burn_damage = 0  # 燃烧伤害/秒
        self.burn_timer = 0  # 燃烧持续时间
        self.poison_damage = 0  # 中毒伤害/秒
        self.poison_timer = 0  # 中毒持续时间
        self.alive = True
        self.x = 100  # 屏幕坐标
        self.y = 300
        name_str = str(name) if name else ""
        self.is_boss = (monster_type == "boss" or "boss" in str(monster_type).lower() or "超级" in name_str)
    
    def _get_monster_type(self, monster_type):
        """根据怪物名称判断类型"""
        lower_name = monster_type.lower()
        if "boss" in lower_name or "超级" in monster_type:
            return self.TYPE_BOSS
        elif "fast" in lower_name or "快速" in monster_type:
            return self.TYPE_FAST
        elif "armor" in lower_name or "装甲" in monster_type:
            return self.TYPE_ARMOR
        else:
            return self.TYPE_NORMAL
        
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

    def apply_burn(self, damage_per_sec, duration):
        """应用燃烧效果 (DOT)"""
        self.burn_damage = max(self.burn_damage, damage_per_sec)
        self.burn_timer = max(self.burn_timer, duration)
    
    def apply_poison(self, damage_per_sec, duration):
        """应用中毒效果 (DOT)"""
        self.poison_damage = max(self.poison_damage, damage_per_sec)
        self.poison_timer = max(self.poison_timer, duration)
    
    def has_status_effect(self):
        """检查是否有任何状态效果"""
        return self.slow_timer > 0 or self.burn_timer > 0 or self.poison_timer > 0
    
    def slow(self, duration):
        """减速效果（兼容旧接口）"""
        self.frozen = duration
        
    def update(self, dt):
        """更新减速计时器和生成动画"""
        # 更新生成动画
        if self.spawn_scale < 1.0:
            self.spawn_scale = min(1.0, self.spawn_scale + dt * 2)
        
        # 更新减速计时器
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                # 减速结束，恢复原始速度
                self.slow_timer = 0
                self.slow_factor = 1.0
                self.speed = self.original_speed
        
        # 更新燃烧DOT
        if self.burn_timer > 0:
            self.burn_timer -= dt
            if self.burn_timer > 0 and self.burn_damage > 0:
                burn_tick = self.burn_damage * dt
                self.health -= burn_tick
                if self.health <= 0:
                    self.alive = False
        else:
            self.burn_damage = 0
        
        # 更新中毒DOT
        if self.poison_timer > 0:
            self.poison_timer -= dt
            if self.poison_timer > 0 and self.poison_damage > 0:
                poison_tick = self.poison_damage * dt
                self.health -= poison_tick
                if self.health <= 0:
                    self.alive = False
        else:
            self.poison_damage = 0

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
    
    def get_health_ratio(self):
        """获取生命值百分比"""
        return max(0, self.health / self.max_health)
    
    def draw_health_bar(self, screen, x, y, width=40, height=6):
        """绘制血条 - 升级版:低血量闪烁+渐变效果"""
        import pygame
        ratio = self.get_health_ratio()
        if ratio >= 1.0:
            return  # 满血不显示
        
        # 低血量闪烁效果
        if ratio <= 0.25:
            blink = math.sin(pygame.time.get_ticks() * 0.015) * 0.5 + 0.5
            if blink < 0.3:
                return  # 闪烁时短暂隐藏
        
        # 血条背景（带阴影）
        bg_rect = pygame.Rect(x - width//2, y - 20, width, height)
        shadow_rect = bg_rect.move(1, 1)
        pygame.draw.rect(screen, (20, 20, 20), shadow_rect)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)
        
        # 血条前景渐变效果（根据血量变色）
        if ratio > 0.5:
            # 绿色到黄色渐变
            color = (int(255 * (1 - ratio) * 2), 200, 50)
        elif ratio > 0.25:
            # 黄色到橙色渐变
            color = (255, int(200 * ratio * 2), 0)
        else:
            # 红色闪烁效果
            pulse = int(math.sin(pygame.time.get_ticks() * 0.01) * 30 + 225)
            color = (pulse, 30, 30)
        
        fill_width = int(width * ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(x - width//2, y - 20, fill_width, height)
            pygame.draw.rect(screen, color, fill_rect)
            # 高光效果
            highlight_rect = pygame.Rect(x - width//2, y - 19, fill_width, 2)
            pygame.draw.rect(screen, (min(255, color[0]+80), min(255, color[1]+80), min(255, color[2]+80)), highlight_rect)
        
        # 边框（根据血量变色）
        border_color = (100, 100, 100) if ratio > 0.25 else (255, 100, 100)
        pygame.draw.rect(screen, border_color, bg_rect, 1)


class MonsterFactory:
    """怪物工厂"""
    
    MONSTERS = {
        "小怪物": {"health": 50, "speed": 0.01, "reward": 10, "color": "green", "type": "normal"},
        "中怪物": {"health": 100, "speed": 0.008, "reward": 20, "color": "yellow", "type": "normal"},
        "大怪物": {"health": 200, "speed": 0.006, "reward": 40, "color": "orange", "type": "normal"},
        "Boss": {"health": 500, "speed": 0.004, "reward": 100, "color": "red", "type": "boss"},
        "超级Boss": {"health": 1000, "speed": 0.003, "reward": 300, "color": "purple", "type": "boss"},
        "快速怪": {"health": 40, "speed": 0.02, "reward": 15, "color": "cyan", "type": "fast"},
        "装甲怪": {"health": 300, "speed": 0.005, "reward": 50, "color": "gray", "type": "armor"},
    }
    
    @classmethod
    def create(cls, name):
        """创建怪物"""
        if name not in cls.MONSTERS:
            return None
        stats = cls.MONSTERS[name]
        # 使用stats中的type或默认为normal
        monster_type = stats.get("type", "normal")
        return Monster(name, stats["health"], stats["speed"], stats["reward"], monster_type)
    
    @classmethod
    def list_monsters(cls):
        """列出所有怪物类型"""
        return list(cls.MONSTERS.keys())