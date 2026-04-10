"""
保卫萝卜 - 塔基特效系统
防御塔底座动态光效与粒子效果
"""
import pygame
import math
import random


class BaseEffect:
    """塔基特效基类"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.life = 0
        self.max_life = 60
        
    def update(self, dt):
        """更新特效"""
        self.life += dt
        if self.life >= self.max_life:
            self.active = False
            
    def draw(self, screen):
        """绘制特效（子类实现）"""
        pass


class GlowRing(BaseEffect):
    """发光圆环特效"""
    
    def __init__(self, x, y, color=(100, 200, 255), radius=25):
        super().__init__(x, y)
        self.color = color
        self.base_radius = radius
        self.max_life = 90
        
    def update(self, dt):
        self.life += dt
        # 脉动效果
        self.current_radius = self.base_radius + math.sin(self.life * 0.1) * 5
        if self.life >= self.max_life:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
        # 渐变透明度
        alpha = int(255 * (1 - self.life / self.max_life))
        # 外圈
        pygame.draw.circle(screen, (*self.color, alpha), 
                          (int(self.x), int(self.y)), 
                          int(self.current_radius), 2)
        # 内圈
        inner_alpha = alpha // 2
        pygame.draw.circle(screen, (*self.color, inner_alpha), 
                          (int(self.x), int(self.y)), 
                          int(self.current_radius * 0.6), 1)


class ParticleRing(BaseEffect):
    """粒子环特效"""
    
    def __init__(self, x, y, color=(255, 200, 100), count=12):
        super().__init__(x, y)
        self.color = color
        self.count = count
        self.particles = []
        self.max_life = 60
        # 初始化粒子
        for i in range(count):
            angle = (360 / count) * i
            rad = math.radians(angle)
            self.particles.append({
                'angle': angle,
                'speed': 0.5 + random.random() * 0.5,
                'offset': random.random() * 10
            })
            
    def update(self, dt):
        self.life += dt
        # 更新粒子位置
        for p in self.particles:
            p['angle'] += p['speed'] * dt
        if self.life >= self.max_life:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
        alpha = int(255 * (1 - self.life / self.max_life))
        base_radius = 20 + self.life * 0.3
        
        for p in self.particles:
            rad = math.radians(p['angle'])
            px = self.x + math.cos(rad) * base_radius
            py = self.y + math.sin(rad) * base_radius
            pygame.draw.circle(screen, (*self.color, alpha), 
                             (int(px), int(py)), 3)


class BaseEffectManager:
    """塔基特效管理器"""
    
    def __init__(self):
        self.effects = []
        self.tower_base_glows = {}  # 塔基持续发光 {tower_id: glow_color}
        
    def add_glow_ring(self, x, y, color=None):
        """添加发光圆环"""
        if color is None:
            color = (100, 200, 255)
        effect = GlowRing(x, y, color)
        self.effects.append(effect)
        
    def add_particle_ring(self, x, y, color=None):
        """添加粒子环"""
        if color is None:
            color = (255, 200, 100)
        effect = ParticleRing(x, y, color)
        self.effects.append(effect)
        
    def set_tower_base_glow(self, tower_id, color):
        """设置塔基持续发光"""
        self.tower_base_glows[tower_id] = color
        
    def remove_tower_base_glow(self, tower_id):
        """移除塔基发光"""
        if tower_id in self.tower_base_glows:
            del self.tower_base_glows[tower_id]
            
    def draw_tower_base_glows(self, screen, towers):
        """绘制所有塔基发光效果"""
        for tower in towers:
            tower_id = id(tower)
            if tower_id in self.tower_base_glows:
                color = self.tower_base_glows[tower_id]
                # 绘制塔基发光
                glow_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
                # 多层发光
                for i in range(3):
                    radius = 25 - i * 5
                    alpha = 30 - i * 10
                    pygame.draw.circle(glow_surface, (*color, alpha), (30, 30), radius)
                screen.blit(glow_surface, (tower.x - 30, tower.y - 30))
                
    def update(self, dt):
        """更新所有特效"""
        # 更新粒子特效
        for effect in self.effects:
            effect.update(dt)
        # 移除失效特效
        self.effects = [e for e in self.effects if e.active]
        
    def draw(self, screen):
        """绘制所有特效"""
        for effect in self.effects:
            effect.draw(screen)
            
    def trigger_attack_effect(self, tower):
        """触发攻击特效（塔攻击时调用）"""
        # 根据塔类型选择特效颜色
        tower_name = getattr(tower, 'name', '') or ''
        
        if "箭" in tower_name:
            self.add_glow_ring(tower.x, tower.y, (200, 200, 255))
        elif "炮" in tower_name:
            self.add_particle_ring(tower.x, tower.y, (255, 150, 50))
        elif "魔法" in tower_name:
            self.add_glow_ring(tower.x, tower.y, (180, 80, 255))
            self.add_particle_ring(tower.x, tower.y, (200, 100, 255))
        elif "减速" in tower_name:
            self.add_glow_ring(tower.x, tower.y, (100, 200, 255))
        else:
            self.add_glow_ring(tower.x, tower.y, (255, 255, 200))


# 单例实例
_base_effect_manager = None

def get_base_effect_manager() -> BaseEffectManager:
    """获取塔基特效管理器单例"""
    global _base_effect_manager
    if _base_effect_manager is None:
        _base_effect_manager = BaseEffectManager()
    return _base_effect_manager