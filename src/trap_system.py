"""
保卫萝卜 - 陷阱系统
在路径上放置陷阱对怪物造成持续伤害和特殊效果
"""
import pygame
import math
import random


class Trap:
    """陷阱基类"""
    TRAP_TYPES = {
        'spike': {'name': '尖刺陷阱', 'damage': 5, 'range': 30, 'cost': 50, 'color': (180, 180, 180)},
        'poison': {'name': '毒陷阱', 'damage': 2, 'range': 35, 'cost': 80, 'color': (128, 0, 128)},
        'freeze': {'name': '冰霜陷阱', 'damage': 1, 'range': 40, 'cost': 100, 'color': (100, 200, 255)},
    }
    
    def __init__(self, trap_type, x, y):
        self.trap_type = trap_type
        self.x = x
        self.y = y
        config = self.TRAP_TYPES[trap_type]
        self.name = config['name']
        self.damage = config['damage']
        self.range = config['range']
        self.cost = config['cost']
        self.color = config['color']
        
        self.level = 1
        self.active = True
        self.last_trigger_time = 0
        self.trigger_interval = 500  # 触发间隔(ms)
        self.affected_monsters = {}  # 当前影响的怪物 {monster: effect_time}
        self.animation_phase = 0
        
    def upgrade(self):
        """升级陷阱"""
        if self.level < 3:
            self.level += 1
            self.damage *= 1.5
            self.range *= 1.2
            return True
        return False
        
    def update(self, current_time, monsters):
        """更新陷阱状态"""
        if not self.active:
            return
            
        self.animation_phase = (self.animation_phase + 0.1) % (2 * math.pi)
        
        # 检查范围内的怪物
        affected = []
        for monster in monsters:
            if not monster.alive:
                continue
            dist = math.sqrt((monster.x - self.x)**2 + (monster.y - self.y)**2)
            if dist <= self.range:
                affected.append(monster)
                # 应用效果
                if monster not in self.affected_monsters:
                    self.affected_monsters[monster] = current_time
                self._apply_effect(monster, current_time)
        
        # 清理不再范围内的怪物
        to_remove = []
        for monster in self.affected_monsters:
            if monster not in affected:
                self._remove_effect(monster)
                to_remove.append(monster)
        for monster in to_remove:
            del self.affected_monsters[monster]
    
    def _apply_effect(self, monster, current_time):
        """对怪物应用效果"""
        # 在子类中实现
        pass
        
    def _remove_effect(self, monster):
        """移除怪物身上的效果"""
        # 在子类中实现
        pass
        
    def draw(self, screen):
        """绘制陷阱"""
        if not self.active:
            return
            
        # 绘制范围指示器
        alpha = int(30 + 20 * math.sin(self.animation_phase))
        s = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        color = (*self.color, alpha)
        pygame.draw.circle(s, color, (self.range, self.range), self.range)
        screen.blit(s, (self.x - self.range, self.y - self.range))
        
        # 绘制陷阱主体
        size = 20 + self.level * 3
        rect = pygame.Rect(self.x - size//2, self.y - size//2, size, size)
        pygame.draw.rect(screen, self.color, rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=5)
        
        # 绘制等级标识
        font = pygame.font.Font(None, 16)
        text = font.render(f"Lv{self.level}", True, (255, 255, 255))
        screen.blit(text, (self.x - 10, self.y - size//2 - 14))
    
    def get_info(self):
        """获取陷阱信息"""
        return {
            'type': self.trap_type,
            'name': self.name,
            'level': self.level,
            'damage': self.damage,
            'range': self.range,
            'cost': self.cost,
        }


class SpikeTrap(Trap):
    """尖刺陷阱 - 持续物理伤害"""
    def __init__(self, x, y):
        super().__init__('spike', x, y)
        self.damage_interval = 200  # 伤害间隔(ms)
        
    def _apply_effect(self, monster, current_time):
        if current_time - self.last_trigger_time >= self.trigger_interval:
            monster.take_damage(self.damage * self.level)
            self.last_trigger_time = current_time
            
    def _remove_effect(self, monster):
        pass


class PoisonTrap(Trap):
    """毒陷阱 - 持续毒伤害+减速"""
    def __init__(self, x, y):
        super().__init__('poison', x, y)
        
    def _apply_effect(self, monster, current_time):
        if current_time - self.last_trigger_time >= self.trigger_interval:
            monster.take_damage(self.damage * self.level)
            monster.apply_status('poisoned', 2000, 0.5)  # 中毒减速50%
            self.last_trigger_time = current_time
            
    def _remove_effect(self, monster):
        monster.remove_status('poisoned')


class FreezeTrap(Trap):
    """冰霜陷阱 - 持续减速"""
    def __init__(self, x, y):
        super().__init__('freeze', x, y)
        
    def _apply_effect(self, monster, current_time):
        if current_time - self.last_trigger_time >= self.trigger_interval:
            monster.apply_status('frozen', 1500, 0.3)  # 冰冻减速70%
            self.last_trigger_time = current_time
            
    def _remove_effect(self, monster):
        monster.remove_status('frozen')


class TrapSystem:
    """陷阱管理系统"""
    def __init__(self):
        self.traps = []
        self.selected_type = 'spike'
        self.placement_mode = False
        
    def add_trap(self, trap_type, x, y):
        """添加陷阱"""
        trap_classes = {
            'spike': SpikeTrap,
            'poison': PoisonTrap,
            'freeze': FreezeTrap,
        }
        trap = trap_classes[trap_type](x, y)
        self.traps.append(trap)
        return trap
        
    def update(self, current_time, monsters):
        """更新所有陷阱"""
        for trap in self.traps:
            trap.update(current_time, monsters)
            
    def draw(self, screen):
        """绘制所有陷阱"""
        for trap in self.traps:
            trap.draw(screen)
            
    def get_trap_at(self, x, y):
        """获取指定位置的陷阱"""
        for trap in self.traps:
            dist = math.sqrt((trap.x - x)**2 + (trap.y - y)**2)
            if dist <= 20:
                return trap
        return None
        
    def remove_trap(self, trap):
        """移除陷阱"""
        if trap in self.traps:
            self.traps.remove(trap)
            
    def get_total_cost(self):
        """获取所有陷阱总价值"""
        return sum(trap.cost for trap in self.traps)
        
    def save(self):
        """保存陷阱数据"""
        return [{
            'type': trap.trap_type,
            'x': trap.x,
            'y': trap.y,
            'level': trap.level,
        } for trap in self.traps]
        
    def load(self, data):
        """加载陷阱数据"""
        self.traps = []
        for trap_data in data:
            trap = self.add_trap(trap_data['type'], trap_data['x'], trap_data['y'])
            trap.level = trap_data.get('level', 1)


# 全局实例
_trap_system = None

def get_trap_system():
    """获取全局陷阱系统实例"""
    global _trap_system
    if _trap_system is None:
        _trap_system = TrapSystem()
    return _trap_system