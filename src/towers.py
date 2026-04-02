""" 
保卫萝卜 - 防御塔系统
""" 

class Tower:
    """防御塔基类"""
    
    def __init__(self, name, damage, range, cost, attack_speed):
        self.name = name
        self.damage = damage
        self.range = range
        self.cost = cost
        self.attack_speed = attack_speed  # 每秒攻击次数
        self.level = 1
        self.target = None
        
    def upgrade(self):
        """升级防御塔"""
        self.level += 1
        self.damage *= 1.3
        self.range *= 1.1
        return self.level
    
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
        return Tower(name, stats["damage"], stats["range"], stats["cost"], stats["speed"])
    
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