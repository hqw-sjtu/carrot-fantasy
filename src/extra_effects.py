"""
保卫萝卜 - 额外特效系统
包含：攻击拖尾、金币雨等高级特效
"""

import random
import math
import pygame


class TowerAttackTrailEffect:
    """防御塔攻击拖尾特效 - 子弹轨迹拖尾效果"""
    
    def __init__(self, start_pos, end_pos, color=(255, 200, 100), width=4):
        self.start_pos = start_pos  # (x, y)
        self.end_pos = end_pos      # (x, y)
        self.color = color
        self.width = width
        self.max_life = 0.3  # 300ms拖尾
        self.life = 0
        self.active = True
        
    def update(self, dt):
        self.life += dt
        if self.life >= self.max_life:
            self.active = False
            return
        # 计算当前位置（从起点向终点延伸）
        progress = self.life / self.max_life
        self.current_end = (
            self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress,
            self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        )
        
    def draw(self, screen):
        if not self.active or self.life <= 0:
            return
        alpha = int(255 * (1 - self.life / self.max_life))
        # 绘制拖尾线条
        color = (*self.color, alpha)
        # 主线条
        pygame.draw.line(screen, color, self.start_pos, self.current_end, self.width)
        # 发光效果（更宽的半透明线条）
        glow_color = (*self.color, alpha // 3)
        pygame.draw.line(screen, glow_color, self.start_pos, self.current_end, self.width * 3)


class GoldRainEffect:
    """金币雨特效 - 大量金币从天而降"""
    
    def __init__(self, screen_width, screen_height, count=50):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_life = 3.0  # 3秒金币雨
        self.life = 0
        self.active = True
        self.coins = []
        # 生成金币
        for _ in range(count):
            self.coins.append({
                'x': random.uniform(0, screen_width),
                'y': random.uniform(-screen_height, 0),
                'speed': random.uniform(100, 300),
                'size': random.randint(3, 6),
                'angle': random.uniform(0, 2 * math.pi),
                'rotation_speed': random.uniform(-5, 5)
            })
        
    def update(self, dt):
        self.life += dt
        if self.life >= self.max_life:
            self.active = False
            return
        # 更新金币位置
        for coin in self.coins:
            coin['y'] += coin['speed'] * dt
            coin['angle'] += coin['rotation_speed'] * dt
            # 超出屏幕底部重置到顶部
            if coin['y'] > self.screen_height:
                coin['y'] = random.uniform(-50, -10)
                coin['x'] = random.uniform(0, self.screen_width)
                
    def draw(self, screen):
        if not self.active:
            return
        alpha = int(255 * min(1, (self.max_life - self.life) / 0.5))
        for coin in self.coins:
            # 绘制旋转金币
            color = (255, 215, 0, alpha)
            center = (int(coin['x']), int(coin['y']))
            # 外圈金光
            pygame.draw.circle(screen, (*color[:3], alpha // 2), center, coin['size'] + 2)
            # 内圈
            pygame.draw.circle(screen, color, center, coin['size'])


class ExperienceOrb:
    """经验球特效 - 怪物死亡后飞向玩家的光球"""
    
    def __init__(self, x, y, value=10, target_pos=None):
        self.x = x
        self.y = y
        self.value = value  # 经验值
        self.target_pos = target_pos  # 目标位置（玩家/面板）
        self.max_life = 2.0  # 最大存活2秒
        self.life = 0
        self.active = True
        self.collected = False
        
        # 飞行参数
        self.speed = 400  # 像素/秒
        self.vx = random.uniform(-50, 50)
        self.vy = random.uniform(-100, -50)
        self.gravity = 200  # 重力
        self.trail = []  # 拖尾
        
    def update(self, dt):
        """更新经验球"""
        self.life += dt
        
        # 记录拖尾
        self.trail.append((self.x, self.y, self.life))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        if self.target_pos and not self.collected:
            # 飞向目标
            dx = self.target_pos[0] - self.x
            dy = self.target_pos[1] - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < 30:
                # 收集成功
                self.collected = True
                self.active = False
                return True  # 返回True表示被收集
            
            # 追踪飞行
            self.vx += (dx / dist) * self.speed * dt * 3
            self.vy += (dy / dist) * self.speed * dt * 3
        
        # 应用重力和阻尼
        self.vy += self.gravity * dt
        self.vx *= 0.98
        self.vy *= 0.98
        
        # 更新位置
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 边界检查
        if self.y > 700:
            self.y = 700
            self.vy *= -0.5
        
        if self.life >= self.max_life:
            self.active = False
            
        return False
    
    def draw(self, screen):
        """绘制经验球"""
        if not self.active:
            return
        
        # 拖尾效果
        for tx, ty, tlife in self.trail:
            alpha = int(100 * (1 - (self.life - tlife) / 0.5))
            if alpha > 0:
                size = 4 * (1 - (self.life - tlife) / 0.5)
                pygame.draw.circle(screen, (100, 200, 255, alpha), (int(tx), int(ty)), max(1, int(size)))
        
        # 主体发光
        base_size = 8 + self.value // 10
        glow_size = base_size + 6
        
        # 外圈发光
        glow_color = (100, 200, 255, 150)
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), glow_size)
        
        # 内圈主体
        main_color = (150, 220, 255)
        pygame.draw.circle(screen, main_color, (int(self.x), int(self.y)), base_size)
        
        # 高光
        highlight_color = (255, 255, 255)
        pygame.draw.circle(screen, highlight_color, (int(self.x - 2), int(self.y - 2)), base_size // 3)


class ExperienceManager:
    """经验球管理器 - 管理所有经验球的生成和更新"""
    
    _instance = None
    
    def __init__(self):
        self.orbs = []
        self.total_experience = 0
        self.level = 1
        self.exp_to_level = 100  # 升级所需经验
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def spawn_orb(self, x, y, value=10, target_pos=None):
        """生成经验球"""
        orb = ExperienceOrb(x, y, value, target_pos)
        self.orbs.append(orb)
        
    def update(self, dt):
        """更新所有经验球"""
        for orb in self.orbs[:]:
            collected = orb.update(dt)
            if collected:
                self.add_experience(orb.value)
                self.orbs.remove(orb)
            elif not orb.active:
                self.orbs.remove(orb)
                
    def add_experience(self, amount):
        """增加经验值"""
        self.total_experience += amount
        # 检查升级
        while self.total_experience >= self.exp_to_level:
            self.total_experience -= self.exp_to_level
            self.level += 1
            self.exp_to_level = int(self.exp_to_level * 1.2)  # 升级所需经验递增
            
    def draw(self, screen):
        """绘制所有经验球"""
        for orb in self.orbs:
            orb.draw(screen)
            
    def get_level_info(self):
        """获取等级信息"""
        return {
            'level': self.level,
            'current_exp': self.total_experience,
            'exp_to_level': self.exp_to_level,
            'progress': self.total_experience / self.exp_to_level if self.exp_to_level > 0 else 0
        }