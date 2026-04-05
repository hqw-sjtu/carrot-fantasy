import pygame
from src.config_loader import get_config

""" 
保卫萝卜 - 防御塔系统
""" 

# 全局音效播放器（可在 main.py 中设置）
sound_player = None

def set_sound_player(player):
    """设置全局音效播放器"""
    global sound_player
    sound_player = player

class Tower:
    """防御塔基类"""
    max_level = 3
    
    def __init__(self, name, damage, range, cost, attack_speed, x=0, y=0, slow_factor=1.0):
        self.name = name
        self.damage = damage
        self.range = range
        self.cost = cost
        self.attack_speed = attack_speed
        self.slow_factor = slow_factor  # 减速因子
        self.level = 1
        self.target = None
        self.x = x
        self.y = y
        self.cooldown = 0
        self.projectiles = []
        
    def get_upgrade_cost(self):
        """获取升级费用"""
        config = get_config()
        tower_config = config.get('towers', {}).get(self.name, {})
        return tower_config.get('upgrade_cost', self.cost // 2)
    
    def can_upgrade(self):
        """检查是否可以升级"""
        return self.level < self.max_level
    
    def upgrade(self):
        """升级防御塔"""
        if not self.can_upgrade():
            return None
        self.level += 1
        self.damage *= 1.3
        self.range *= 1.1
        self.attack_speed *= 1.1
        return self.level
    
    def find_target(self, monsters):
        """寻找范围内最接近终点的怪物"""
        best_target = None
        best_progress = -1
        for m in monsters:
            if not hasattr(m, 'alive') or not m.alive:
                continue
            # 怪物位置转换为屏幕坐标
            m_x = int(100 + m.position * 600)
            m_y = 300
            # 计算距离
            dx = m_x - self.x
            dy = m_y - self.y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist <= self.range * 50:  # range单位转换
                if m.position > best_progress:
                    best_progress = m.position
                    best_target = m
        return best_target
    
    def attack(self, monsters, projectiles):
        """攻击冷却更新和发射子弹"""
        self.cooldown -= 1/60  # 每帧减少冷却
        if self.cooldown <= 0:
            target = self.find_target(monsters)
            if target:
                # 创建子弹
                from src.projectiles import Projectile
                p = Projectile(self.x, self.y, target, self.damage, slow_factor=self.slow_factor)
                projectiles.append(p)
                # 播放音效
                if sound_player:
                    sound_player()
                self.cooldown = 1 / self.attack_speed
    
    def update_projectiles(self, dt):
        """更新所有子弹"""
        for p in self.projectiles[:]:
            p.update(dt)
            if not p.active:
                self.projectiles.remove(p)
    
    def __str__(self):
        return f"{self.name} Lv.{self.level} (伤害:{self.damage}, 射程:{self.range})"


class TowerFactory:
    """防御塔工厂"""
    
    TOWERS = {
        "箭塔": {"damage": 10, "range": 3, "cost": 50, "speed": 2},
        "炮塔": {"damage": 30, "range": 2, "cost": 100, "speed": 0.5},
        "魔法塔": {"damage": 20, "range": 4, "cost": 80, "speed": 1},
        "减速塔": {"damage": 5, "range": 3, "cost": 60, "speed": 1, "slow": 0.5},
    }
    
    @classmethod
    def create(cls, name):
        """创建防御塔"""
        if name not in cls.TOWERS:
            return None
        stats = cls.TOWERS[name]
        slow_factor = stats.get("slow", 1.0)  # 获取减速因子
        return Tower(name, stats["damage"], stats["range"], stats["cost"], stats["speed"], slow_factor=slow_factor)
    
    @classmethod
    def list_towers(cls):
        """列出所有防御塔"""
        return list(cls.TOWERS.keys())
    
    @classmethod
    def get_info(cls, name):
        """获取防御塔信息"""
        if name not in cls.TOWERS:
            return None
        return cls.TOWERS[name]