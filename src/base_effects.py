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


class CritFlashEffect(BaseEffect):
    """暴击闪光特效"""
    
    def __init__(self, x, y, color=(255, 215, 0), is_crit=True):
        super().__init__(x, y)
        self.color = color
        self.is_crit = is_crit
        self.max_life = 30 if is_crit else 20
        self.flash_count = 3 if is_crit else 2
        self.current_flash = 0
        self.flash_interval = self.max_life / self.flash_count
        
    def update(self, dt):
        self.life += dt
        # 计算当前闪光状态
        self.current_flash = int(self.life / self.flash_interval)
        if self.life >= self.max_life:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
        # 闪光效果
        flash_phase = self.life % self.flash_interval
        if flash_phase < self.flash_interval * 0.3:  # 亮期
            alpha = 200 if self.is_crit else 150
            # 十字闪光
            length = 40 if self.is_crit else 25
            width = 4 if self.is_crit else 2
            # 水平线
            pygame.draw.line(screen, (*self.color, alpha), 
                           (self.x - length, self.y), (self.x + length, self.y), width)
            # 垂直线
            pygame.draw.line(screen, (*self.color, alpha), 
                           (self.x, self.y - length), (self.x, self.y + length), width)
            # 中心圆
            pygame.draw.circle(screen, (*self.color, alpha), 
                             (int(self.x), int(self.y)), 8, 0)


class UpgradeBeamEffect(BaseEffect):
    """升级光柱特效 - 金色光柱直冲云霄"""
    
    def __init__(self, x, y, color=(255, 215, 0)):
        super().__init__(x, y)
        self.color = color
        self.max_life = 45
        self.beam_width = 8
        self.max_height = 120
        self.particles = []
        # 初始化光柱粒子
        for _ in range(12):
            self.particles.append({
                'offset_x': random.uniform(-15, 15),
                'offset_y': random.uniform(-100, 0),
                'size': random.randint(2, 5),
                'speed': random.uniform(2, 4),
                'alpha': random.randint(150, 255)
            })
        
    def update(self, dt):
        self.life += dt
        # 粒子向上流动
        for p in self.particles:
            p['offset_y'] -= p['speed']
            if p['offset_y'] < -self.max_height:
                p['offset_y'] = 0
                p['offset_x'] = random.uniform(-15, 15)
        if self.life >= self.max_life:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
        # 透明度渐变
        progress = self.life / self.max_life
        fade_alpha = int(255 * (1 - progress * 0.5))
        # 绘制光柱
        center_x = int(self.x)
        bottom_y = int(self.y)
        # 光柱主体
        for i in range(3):
            width = self.beam_width - i * 2
            alpha = fade_alpha - i * 40
            if alpha > 0:
                beam_surface = pygame.Surface((width * 2, self.max_height), pygame.SRCALPHA)
                pygame.draw.rect(beam_surface, (*self.color, alpha), 
                               (width - i, 0, width + i, self.max_height))
                screen.blit(beam_surface, (center_x - width, bottom_y - self.max_height))
        # 绘制粒子
        for p in self.particles:
            px = int(self.x + p['offset_x'])
            py = int(self.y + p['offset_y'])
            pygame.draw.circle(screen, (*self.color, int(p['alpha'] * (1 - progress * 0.5))), (px, py), p['size'])
        # 底部光环
        pygame.draw.circle(screen, (*self.color, fade_alpha), (center_x, bottom_y), 20, 2)
        pygame.draw.circle(screen, (*self.color, fade_alpha // 2), (center_x, bottom_y), 15, 0)


class ChainLightningEffect(BaseEffect):
    """连锁闪电特效"""
    
    def __init__(self, x, y, target_x, target_y, color=(180, 140, 255)):
        super().__init__(x, y)
        self.start_x = x
        self.start_y = y
        self.target_x = target_x
        self.target_y = target_y
        self.color = color
        self.max_life = 15
        self.generate_lightning_points()
        
    def generate_lightning_points(self):
        """生成闪电路径点"""
        self.points = []
        segments = 6
        for i in range(segments + 1):
            t = i / segments
            px = self.start_x + (self.target_x - self.start_x) * t
            py = self.start_y + (self.target_y - self.start_y) * t
            # 添加随机偏移
            if i > 0 and i < segments:
                offset = random.randint(-15, 15)
                px += offset
                py += offset * 0.5
            self.points.append((px, py))
            
    def update(self, dt):
        self.life += dt
        if self.life >= self.max_life:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
        alpha = int(255 * (1 - self.life / self.max_life))
        # 绘制闪电
        for i in range(len(self.points) - 1):
            pygame.draw.line(screen, (*self.color, alpha), 
                           self.points[i], self.points[i + 1], 2)


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
        
    def add_crit_flash(self, x, y, is_crit=True):
        """添加暴击闪光特效"""
        color = (255, 215, 0) if is_crit else (255, 255, 255)
        effect = CritFlashEffect(x, y, color, is_crit)
        self.effects.append(effect)
        
    def add_chain_lightning(self, x, y, target_x, target_y):
        """添加连锁闪电特效"""
        effect = ChainLightningEffect(x, y, target_x, target_y)
        self.effects.append(effect)
        
    def add_shield_effect(self, x, y, color=None):
        """添加护盾环绕特效"""
        if color is None:
            color = (100, 150, 255)
        effect = ShieldEffect(x, y, color)
        self.effects.append(effect)
        
    def add_idle_particles(self, x, y, color=None):
        """添加塔空闲粒子特效"""
        if color is None:
            color = (255, 255, 200)
        effect = TowerIdleParticles(x, y, color)
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
        elif "冰霜" in tower_name:
            self.add_glow_ring(tower.x, tower.y, (180, 220, 255))
            self.add_particle_ring(tower.x, tower.y, (200, 240, 255))
        else:
            self.add_glow_ring(tower.x, tower.y, (255, 255, 200))
            
    def trigger_crit_effect(self, tower, is_crit=True):
        """触发暴击特效"""
        self.add_crit_flash(tower.x, tower.y, is_crit)
        
    def trigger_upgrade_effect(self, tower):
        """触发升级光柱特效"""
        self.add_upgrade_beam(tower.x, tower.y)
        
    def add_upgrade_beam(self, x, y, color=(255, 215, 0)):
        """添加升级光柱特效"""
        self.effects.append(UpgradeBeamEffect(x, y, color))
        
    def trigger_chain_lightning(self, tower, target):
        """触发连锁闪电特效"""
        if hasattr(target, 'x') and hasattr(target, 'y'):
            self.add_chain_lightning(tower.x, tower.y, target.x, target.y)


class ShieldEffect(BaseEffect):
    """护盾环绕特效 - 防御塔被攻击时显示保护罩"""
    
    def __init__(self, x, y, color=(100, 150, 255), duration=30):
        super().__init__(x, y)
        self.color = color
        self.max_life = duration
        self.angle = 0
        self.rings = [
            {'radius': 30, 'alpha': 40, 'width': 2},
            {'radius': 35, 'alpha': 25, 'width': 1},
            {'radius': 40, 'alpha': 15, 'width': 1},
        ]
        
    def update(self, dt):
        self.life += dt
        self.angle += dt * 2  # 旋转效果
        if self.life >= self.max_life:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
        fade_factor = 1 - (self.life / self.max_life)
        center = (int(self.x), int(self.y))
        
        for ring in self.rings:
            # 旋转的椭圆效果
            alpha = int(ring['alpha'] * fade_factor)
            pygame.draw.circle(screen, (*self.color, alpha), 
                             center, int(ring['radius']), ring['width'])
        
        # 绘制六边形护盾符文
        points = []
        for i in range(6):
            angle = self.angle + (60 * i)
            rad = math.radians(angle)
            px = self.x + math.cos(rad) * 32
            py = self.y + math.sin(rad) * 32
            points.append((int(px), int(py)))
        pygame.draw.polygon(screen, (*self.color, int(80 * fade_factor)), points, 2)


class TowerIdleParticles(BaseEffect):
    """防御塔空闲时漂浮粒子特效"""
    
    def __init__(self, x, y, color=(255, 255, 200), count=5):
        super().__init__(x, y)
        self.color = color
        self.particles = []
        self.max_life = 120  # 2秒
        # 初始化粒子
        for _ in range(count):
            self.particles.append({
                'x': x + random.uniform(-15, 15),
                'y': y + random.uniform(-15, 15),
                'vy': random.uniform(-0.5, -1.5),  # 向上漂浮
                'life': random.uniform(0, 60),
                'max_life': random.uniform(40, 80),
                'size': random.uniform(1, 3)
            })
            
    def update(self, dt):
        self.life += dt
        for p in self.particles:
            p['y'] += p['vy'] * dt
            p['life'] += dt
            p['x'] += math.sin(self.life * 0.1 + p['y'] * 0.1) * 0.3
        if self.life >= self.max_life:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
        for p in self.particles:
            if p['life'] > p['max_life']:
                continue
            alpha = int(150 * (1 - p['life'] / p['max_life']))
            size = p['size'] * (1 - p['life'] / p['max_life'] * 0.5)
            pygame.draw.circle(screen, (*self.color, alpha), 
                             (int(p['x']), int(p['y'])), int(size))


# 单例实例
_base_effect_manager = None

def get_base_effect_manager() -> BaseEffectManager:
    """获取塔基特效管理器单例"""
    global _base_effect_manager
    if _base_effect_manager is None:
        _base_effect_manager = BaseEffectManager()
    return _base_effect_manager