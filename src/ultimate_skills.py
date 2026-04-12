"""
保卫萝卜 - 防御塔终极技能系统
包含：全屏攻击、能量爆发、召唤支援等终极技能
"""
import pygame
import math
import random


class UltimateSkill:
    """终极技能基类"""
    
    def __init__(self, name, cooldown, damage, duration):
        self.name = name
        self.cooldown = cooldown  # 冷却时间(秒)
        self.damage = damage      # 技能伤害
        self.duration = duration  # 持续时间(秒)
        self.current_cooldown = 0
        self.active = False
        self.life = 0
        
    def update(self, dt):
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
        if self.active:
            self.life += dt
            if self.life >= self.duration:
                self.active = False
                
    def activate(self):
        if self.current_cooldown <= 0:
            self.active = True
            self.life = 0
            self.current_cooldown = self.cooldown
            return True
        return False
    
    def draw(self, screen):
        pass
    
    def is_ready(self):
        return self.current_cooldown <= 0


class MeteorStrike(UltimateSkill):
    """陨石打击 - 全屏随机陨石降落"""
    
    def __init__(self):
        super().__init__("陨石打击", 30, 100, 3.0)
        self.meteors = []
        
    def activate(self):
        if super().activate():
            # 生成陨石
            self.meteors = []
            for _ in range(20):
                self.meteors.append({
                    'x': random.randint(50, 750),
                    'y': random.randint(-400, -50),
                    'speed': random.uniform(300, 500),
                    'size': random.randint(15, 30),
                    'trail': []
                })
            return True
        return False
    
    def update(self, dt):
        super().update(dt)
        for meteor in self.meteors:
            meteor['y'] += meteor['speed'] * dt
            meteor['trail'].append((meteor['x'], meteor['y']))
            if len(meteor['trail']) > 10:
                meteor['trail'].pop(0)
                
    def draw(self, screen):
        if not self.active:
            return
        for meteor in self.meteors:
            # 拖尾
            for i, pos in enumerate(meteor['trail']):
                alpha = int(255 * (i / len(meteor['trail'])))
                color = (255, 150, 50, alpha)
                size = int(meteor['size'] * (i / len(meteor['trail'])))
                if size > 0:
                    pygame.draw.circle(screen, color[:3], pos, size)
            # 陨石主体
            pygame.draw.circle(screen, (255, 100, 20), 
                             (int(meteor['x']), int(meteor['y'])), meteor['size'])
            pygame.draw.circle(screen, (255, 200, 100), 
                             (int(meteor['x']), int(meteor['y'])), meteor['size'] // 2)


class LightningStorm(UltimateSkill):
    """闪电风暴 - 全屏随机闪电劈下"""
    
    def __init__(self):
        super().__init__("闪电风暴", 25, 80, 4.0)
        self.lightnings = []
        
    def activate(self):
        if super().activate():
            self.lightnings = []
            return True
        return False
    
    def update(self, dt):
        super().update(dt)
        # 定期生成新闪电
        if random.random() < 0.3:
            self.lightnings.append({
                'x': random.randint(50, 750),
                'segments': self._generate_lightning_segment(100, 600, 8),
                'life': 0.2
            })
        # 更新现有闪电
        for lt in self.lightnings:
            lt['life'] -= dt
        self.lightnings = [l for l in self.lightnings if l['life'] > 0]
        
    def _generate_lightning_segment(self, x, y, segments):
        """生成闪电分支"""
        points = [(x, 0)]
        current_x, current_y = x, 0
        for _ in range(segments):
            current_x += random.randint(-30, 30)
            current_y += (y - 0) // segments
            points.append((current_x, min(current_y, y)))
        return points
        
    def draw(self, screen):
        if not self.active:
            return
        for lt in self.lightnings:
            # 闪电主干
            color = (200, 220, 255)
            pygame.draw.lines(screen, color, False, lt['segments'], 3)
            # 发光效果
            glow_color = (150, 180, 255)
            pygame.draw.lines(screen, glow_color, False, lt['segments'], 6)


class IceAge(UltimateSkill):
    """冰河时代 - 全屏冰冻并持续伤害"""
    
    def __init__(self):
        super().__init__("冰河时代", 40, 150, 5.0)
        self.freeze_particles = []
        
    def activate(self):
        if super().activate():
            # 生成冰晶粒子
            self.freeze_particles = []
            for _ in range(100):
                self.freeze_particles.append({
                    'x': random.randint(0, 800),
                    'y': random.randint(0, 600),
                    'size': random.randint(2, 8),
                    'speed': random.uniform(20, 50),
                    'angle': random.uniform(0, 2 * math.pi)
                })
            return True
        return False
    
    def update(self, dt):
        super().update(dt)
        for p in self.freeze_particles:
            p['y'] += p['speed'] * dt
            p['x'] += math.sin(p['angle']) * 20 * dt
            if p['y'] > 600:
                p['y'] = -10
                
    def draw(self, screen):
        if not self.active:
            return
        # 屏幕冰蓝滤镜
        s = pygame.Surface((800, 600), pygame.SRCALPHA)
        alpha = int(50 * (1 - self.life / self.duration))
        s.fill((150, 200, 255, alpha))
        screen.blit(s, (0, 0))
        # 冰晶粒子
        for p in self.freeze_particles:
            color = (200, 240, 255)
            pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), p['size'])


class DivineShield(UltimateSkill):
    """神圣护盾 - 保护所有防御塔免疫伤害"""
    
    def __init__(self):
        super().__init__("神圣护盾", 35, 0, 4.0)
        
    def activate(self):
        if super().activate():
            return True
        return False
    
    def draw(self, screen):
        if not self.active:
            return
        # 屏幕金色滤镜
        s = pygame.Surface((800, 600), pygame.SRCALPHA)
        alpha = int(30 * (1 - self.life / self.duration))
        s.fill((255, 215, 0, alpha))
        screen.blit(s, (0, 0))
        # 边缘光芒
        center = (400, 300)
        pulse = math.sin(self.life * 10) * 20 + 350
        color = (255, 200, 50, 100)
        pygame.draw.circle(screen, color[:3], center, int(pulse), 3)


class TowerSummon(UltimateSkill):
    """塔召唤 - 随机召唤一座防御塔"""
    
    def __init__(self):
        super().__init__("塔召唤", 20, 0, 1.0)
        self.summoned_tower = None
        
    def activate(self):
        if super().activate():
            # 随机位置
            self.summoned_tower = {
                'x': random.randint(100, 700),
                'y': random.randint(100, 500),
                'type': random.choice(['箭塔', '炮塔', '魔法塔']),
                'scale': 0
            }
            return True
        return False
    
    def update(self, dt):
        super().update(dt)
        if self.summoned_tower:
            self.summoned_tower['scale'] = min(1.0, self.summoned_tower['scale'] + dt * 2)
            
    def draw(self, screen):
        if not self.active or not self.summoned_tower:
            return
        t = self.summoned_tower
        center = (int(t['x']), int(t['y']))
        size = int(20 * t['scale'])
        # 光晕
        pygame.draw.circle(screen, (255, 200, 100), center, size + 10)
        # 塔
        color = {'箭塔': (100, 200, 255), '炮塔': (255, 100, 50), '魔法塔': (200, 100, 255)}
        pygame.draw.circle(screen, color.get(t['type'], (255, 255, 255)), center, size)


# 终极技能管理器
class UltimateSkillManager:
    """终极技能管理器"""
    
    def __init__(self):
        self.skills = {
            'meteor': MeteorStrike(),
            'lightning': LightningStorm(),
            'ice_age': IceAge(),
            'shield': DivineShield(),
            'summon': TowerSummon()
        }
        
    def update(self, dt):
        for skill in self.skills.values():
            skill.update(dt)
            
    def draw(self, screen):
        for skill in self.skills.values():
            if skill.active:
                skill.draw(screen)
                
    def activate_skill(self, skill_key):
        if skill_key in self.skills:
            return self.skills[skill_key].activate()
        return False
    
    def get_cooldown(self, skill_key):
        if skill_key in self.skills:
            return self.skills[skill_key].current_cooldown
        return 0
    
    def is_ready(self, skill_key):
        if skill_key in self.skills:
            return self.skills[skill_key].is_ready()
        return False