"""
保卫萝卜 - 粒子特效系统
Carrot Fantasy - Particle Effects System
"""
import pygame
import random
import math


class ShatterParticle:
    """怪物死亡时的破碎碎片"""
    
    def __init__(self, x, y, color, count=8):
        self.x = x
        self.y = y
        self.color = color
        self.max_life = 40
        self.life = self.max_life
        self.shards = []
        for i in range(count):
            angle = (360 / count) * i + random.uniform(-15, 15)
            speed = random.uniform(2, 5)
            rad = math.radians(angle)
            self.shards.append({
                'x': x, 'y': y,
                'vx': math.cos(rad) * speed,
                'vy': math.sin(rad) * speed,
                'size': random.uniform(3, 7),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-10, 10)
            })
            
    def update(self, dt):
        self.life -= dt
        for shard in self.shards:
            shard['x'] += shard['vx'] * dt
            shard['y'] += shard['vy'] * dt
            shard['vy'] += 0.2 * dt
            shard['rotation'] += shard['rot_speed'] * dt
        return self.life > 0
    
    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        for shard in self.shards:
            points = []
            size = shard['size'] * (self.life / self.max_life)
            for a in [0, 90, 180, 270]:
                rad = math.radians(a + shard['rotation'])
                px = shard['x'] + math.cos(rad) * size
                py = shard['y'] + math.sin(rad) * size
                points.append((px, py))
            color = (*self.color, alpha)
            pygame.draw.polygon(screen, color, points)


class Particle:
    """单个粒子"""
    
    def __init__(self, x, y, vx, vy, color, lifetime, size, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.fade = fade
        
    def update(self, dt):
        """更新粒子"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        
        # 减速
        self.vx *= 0.98
        self.vy *= 0.98
        
        return self.lifetime > 0
    
    def draw(self, screen):
        """绘制粒子"""
        if self.lifetime <= 0:
            return
            
        # 计算透明度
        alpha = int(255 * (self.lifetime / self.max_lifetime)) if self.fade else 255
        
        # 绘制发光圆点
        radius = self.size * (self.lifetime / self.max_lifetime)
        if radius < 0.5:
            radius = 0.5
            
        # 外发光
        if radius > 2:
            glow_surf = pygame.Surface((int(radius * 4), int(radius * 4)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha // 3), 
                             (int(radius * 2), int(radius * 2)), int(radius * 2))
            screen.blit(glow_surf, (self.x - radius * 2, self.y - radius * 2))
        
        # 核心
        pygame.draw.circle(screen, (*self.color, alpha), 
                          (int(self.x), int(self.y)), int(radius))


class ParticleSystem:
    """粒子系统管理器 - 带对象池优化"""
    
    def __init__(self):
        self.particles = []
        self.upgrade_aura = []
        self._hit_rings = []  # 命中特效圆环列表
        # 对象池：预分配粒子对象减少GC
        self._particle_pool = []
        self._pool_size = 200
        self._init_pool()
    
    def _init_pool(self):
        """初始化对象池"""
        for _ in range(self._pool_size):
            self._particle_pool.append({
                'active': False,
                'x': 0, 'y': 0, 'vx': 0, 'vy': 0,
                'color': (255, 255, 255), 'lifetime': 0,
                'max_lifetime': 1, 'size': 5, 'fade': True
            })
    
    def _get_particle(self):
        """从池中获取粒子"""
        for p in self._particle_pool:
            if not p['active']:
                p['active'] = True
                return p
        # 池满了，创建新的
        new_p = {'active': True, 'x': 0, 'y': 0, 'vx': 0, 'vy': 0,
                 'color': (255, 255, 255), 'lifetime': 0, 
                 'max_lifetime': 1, 'size': 5, 'fade': True}
        self._particle_pool.append(new_p)
        return new_p
    
    def _release_particle(self, p):
        """归还粒子到池"""
        p['active'] = False
    
    def add_hit_effect(self, x, y, tower_type=''):
        """塔攻击命中特效 - 工艺品级别新增"""
        # 根据塔类型选择不同颜色
        colors = {
            'arrow': (50, 200, 50),      # 箭塔-绿色
            'cannon': (255, 140, 0),     # 炮塔-橙色
            'magic': (180, 100, 255),    # 魔法塔-紫色
            'ice': (150, 230, 255),      # 冰霜塔-浅蓝
            'freeze': (200, 240, 255),   # 减速塔-白色
        }
        color = colors.get(tower_type, (255, 220, 100))
        
        # 小型爆发
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(30, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particle = Particle(x, y, vx, vy, color, 0.3, random.uniform(2, 5))
            self.particles.append(particle)
        
        # 命中中心圆环
        self._hit_rings.append({
            'x': x, 'y': y,
            'radius': 5,
            'max_radius': 25,
            'alpha': 180,
            'color': color,
            'start_time': pygame.time.get_ticks()
        })

    def add_critical_effect(self, x, y):
        """添加暴击特效 - 红色爆炸效果"""
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([
                (255, 100, 100),   # 红色
                (255, 200, 50),    # 金色
                (255, 255, 100),   # 亮黄
            ])
            particle = Particle(x, y, vx, vy, color, 0.5, random.uniform(3, 8))
            self.particles.append(particle)
    
    def add_upgrade_aura(self, x, y, tower_level=1):
        """添加升级光晕效果 - 工艺品级别增强"""
        # 主光环
        self.upgrade_aura.append({
            'x': x, 'y': y,
            'radius': 10,
            'alpha': 200,
            'start_time': pygame.time.get_ticks(),
            'type': 'main',
            'level': tower_level
        })
        # 额外脉冲环 (等级≥2时)
        if tower_level >= 2:
            self.upgrade_aura.append({
                'x': x, 'y': y,
                'radius': 5,
                'alpha': 150,
                'start_time': pygame.time.get_ticks(),
                'type': 'pulse',
                'level': tower_level
            })
        # 星级粒子 (等级=3时)
        if tower_level >= 3:
            for i in range(8):
                angle = i * 45
                self.emit(
                    x + math.cos(math.radians(angle)) * 30,
                    y + math.sin(math.radians(angle)) * 30,
                    3, (255, 215, 0), lifetime=0.8, size=4,
                    speed=20, spread=30, fade=True
                )
    
    def update_upgrade_aura(self):
        """更新升级光晕 - 工艺品级别"""
        import pygame
        current_time = pygame.time.get_ticks()
        to_remove = []
        for aura in self.upgrade_aura:
            elapsed = current_time - aura['start_time']
            duration = 1200 if aura.get('type') == 'pulse' else 1000
            if elapsed > duration:
                to_remove.append(aura)
                continue
            # 不同类型不同动画
            if aura.get('type') == 'pulse':
                aura['radius'] += 3
                aura['alpha'] = max(0, 150 - elapsed * 0.15)
            else:
                aura['radius'] += 2
                aura['alpha'] = max(0, 200 - elapsed * 0.2)
        for aura in to_remove:
            self.upgrade_aura.remove(aura)
    
    def draw_upgrade_aura(self, screen):
        """绘制升级光晕 - 工艺品级别"""
        import pygame
        for aura in self.upgrade_aura:
            if aura['alpha'] <= 0:
                continue
            size = aura['radius'] * 2 + 30
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            cx, cy = aura['radius'] + 15, aura['radius'] + 15
            # 外发光
            glow_color = (255, 215, 0, int(aura['alpha'] * 0.3))
            pygame.draw.circle(surf, glow_color, (cx, cy), aura['radius'] + 5)
            # 主环
            if aura.get('type') == 'pulse':
                color = (100, 200, 255, int(aura['alpha']))
                pygame.draw.circle(surf, color, (cx, cy), aura['radius'], 3)
            else:
                color = (255, 215, 0, int(aura['alpha']))
                pygame.draw.circle(surf, color, (cx, cy), aura['radius'], 4)
            # 等级3金色闪烁
            if aura.get('level', 1) >= 3 and aura['alpha'] > 100:
                spark_color = (255, 255, 200, int(aura['alpha'] * 0.5))
                pygame.draw.circle(surf, spark_color, (cx, cy), aura['radius'] - 3, 2)
            screen.blit(surf, (aura['x'] - aura['radius'] - 15, aura['y'] - aura['radius'] - 15))
        
    def emit(self, x, y, count, color, lifetime=1.0, size=5, 
             speed=50, spread=360, fade=True, upward=False):
        """发射粒子"""
        for _ in range(count):
            # 随机角度
            if upward:
                angle = random.uniform(-180, 0)  # 向上
            else:
                angle = random.uniform(0, 360)
                
            angle_rad = math.radians(angle)
            velocity = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle_rad) * velocity
            vy = math.sin(angle_rad) * velocity
            
            self.particles.append(Particle(
                x, y, vx, vy, color, lifetime, size, fade
            ))
    
    def emit_explosion(self, x, y, color, count=20):
        """发射爆炸特效"""
        self.emit(x, y, count, color, lifetime=0.5, size=8, 
                 speed=100, spread=360, fade=True)
    
    def emit_hit(self, x, y, color):
        """命中特效"""
        self.emit(x, y, 10, color, lifetime=0.3, size=6, 
                 speed=30, spread=180, fade=True)
    
    def emit_trail(self, x, y, color):
        """拖尾特效"""
        self.emit(x, y, 2, color, lifetime=0.2, size=3, 
                 speed=10, spread=30, fade=True)
    
    def emit_level_up(self, x, y):
        """升级特效"""
        # 金色粒子
        for _ in range(30):
            self.particles.append(Particle(
                x, y,
                random.uniform(-80, 80),
                random.uniform(-150, -50),  # 向上
                (255, 215, 0),  # 金色
                lifetime=random.uniform(0.8, 1.5),
                size=random.uniform(4, 8),
                fade=True
            ))
        # 白色闪烁
        for _ in range(10):
            self.particles.append(Particle(
                x, y,
                random.uniform(-50, 50),
                random.uniform(-100, -30),
                (255, 255, 255),
                lifetime=0.5,
                size=random.uniform(3, 6),
                fade=True
            ))
    
    def emit_money(self, x, y):
        """金币特效"""
        self.emit(x, y, 8, (255, 215, 0), lifetime=0.8, size=5, 
                 speed=60, spread=90, fade=True, upward=True)
    
    def emit_death(self, x, y, is_boss=False):
        """击杀特效 - 怪物死亡时触发"""
        if is_boss:
            # Boss死亡：大型爆炸
            self.emit_explosion(x, y, (255, 100, 50), count=40)
            self.emit_explosion(x, y, (255, 215, 0), count=30)
            self.emit(x, y, 20, (255, 255, 255), lifetime=1.0, size=10, 
                     speed=150, spread=360, fade=True)
        else:
            # 普通怪物：小型爆炸
            self.emit_explosion(x, y, (200, 100, 150), count=15)
            self.emit(x, y, 5, (255, 200, 100), lifetime=0.4, size=4, 
                     speed=40, spread=180, fade=True)
    
    def emit_armor_break(self, x, y):
        """装甲破碎特效 - 装甲怪物护甲被击碎时触发"""
        # 蓝色碎片飞散
        for _ in range(20):
            self.particles.append(Particle(
                x, y,
                random.uniform(-100, 100),
                random.uniform(-120, 80),
                (100, 150, 255),  # 蓝色装甲色
                lifetime=random.uniform(0.5, 1.0),
                size=random.uniform(3, 6),
                fade=True
            ))
        # 白色火花
        for _ in range(10):
            self.particles.append(Particle(
                x, y,
                random.uniform(-80, 80),
                random.uniform(-100, 60),
                (255, 255, 255),
                lifetime=0.3,
                size=random.uniform(2, 4),
                fade=True
            ))
    
    def emit_freeze(self, x, y):
        """冰冻特效 - 冰霜攻击命中时"""
        # 冰晶粒子
        for _ in range(12):
            angle = random.uniform(0, 360)
            speed = random.uniform(30, 80)
            self.particles.append(Particle(
                x, y,
                math.cos(math.radians(angle)) * speed,
                math.sin(math.radians(angle)) * speed,
                (150, 220, 255),  # 冰蓝色
                lifetime=random.uniform(0.4, 0.8),
                size=random.uniform(2, 5),
                fade=True
            ))
    
    def emit_shield(self, x, y):
        """护盾特效 - 护盾塔或护盾技能触发时"""
        # 蓝色光环
        for _ in range(20):
            angle = random.uniform(0, 360)
            speed = random.uniform(20, 50)
            self.particles.append(Particle(
                x, y,
                math.cos(math.radians(angle)) * speed,
                math.sin(math.radians(angle)) * speed,
                (100, 200, 255),  # 护盾蓝
                lifetime=random.uniform(0.6, 1.0),
                size=random.uniform(3, 6),
                fade=True
            ))
        # 中心亮点
        for _ in range(8):
            self.particles.append(Particle(
                x, y,
                random.uniform(-30, 30),
                random.uniform(-30, 30),
                (200, 240, 255),
                lifetime=0.5,
                size=4,
                fade=True
            ))
    
    def emit_critical(self, x, y):
        """暴击特效 - 暴击伤害时触发"""
        # 金色闪电粒子
        for _ in range(25):
            angle = random.uniform(0, 360)
            speed = random.uniform(80, 180)
            self.particles.append(Particle(
                x, y,
                math.cos(math.radians(angle)) * speed,
                math.sin(math.radians(angle)) * speed,
                (255, 215, 0),  # 金色
                lifetime=random.uniform(0.3, 0.7),
                size=random.uniform(4, 8),
                fade=True
            ))

    def emit_wave_complete(self, x, y, wave_num):
        """波次完成庆祝特效 - 大规模烟花效果"""
        # 多色烟花绽放
        colors = [
            (255, 80, 80),   # 红
            (80, 255, 80),   # 绿
            (80, 80, 255),   # 蓝
            (255, 255, 80),  # 黄
            (255, 80, 255),  # 粉
            (80, 255, 255),  # 青
            (255, 180, 80),  # 橙
        ]
        
        # 每种颜色放一组
        for color in colors:
            for _ in range(15):
                angle = random.uniform(0, 360)
                speed = random.uniform(100, 250)
                self.particles.append(Particle(
                    x, y,
                    math.cos(math.radians(angle)) * speed,
                    math.sin(math.radians(angle)) * speed - 50,  # 向上偏移
                    color,
                    lifetime=random.uniform(0.8, 1.5),
                    size=random.uniform(5, 12),
                    fade=True
                ))
        
        # 金色星星闪烁
        for _ in range(30):
            angle = random.uniform(0, 360)
            speed = random.uniform(50, 150)
            self.particles.append(Particle(
                x, y,
                math.cos(math.radians(angle)) * speed,
                math.sin(math.radians(angle)) * speed - 80,
                (255, 215, 0),  # 金色
                lifetime=random.uniform(1.0, 2.0),
                size=random.uniform(3, 6),
                fade=True
            ))
        # 白色火花
        for _ in range(15):
            self.particles.append(Particle(
                x, y,
                random.uniform(-120, 120),
                random.uniform(-150, 50),
                (255, 255, 255),
                lifetime=random.uniform(0.2, 0.5),
                size=random.uniform(2, 5),
                fade=True
            ))
        # 红色火花（伤害）
        for _ in range(10):
            self.particles.append(Particle(
                x, y,
                random.uniform(-80, 80),
                random.uniform(-100, 80),
                (255, 80, 80),
                lifetime=0.3,
                size=3,
                fade=True
            ))
    
    def update(self, dt):
        """更新所有粒子"""
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # 更新命中特效圆环
        current_time = pygame.time.get_ticks()
        self._hit_rings = [r for r in self._hit_rings 
                          if current_time - r['start_time'] < 300]
        for r in self._hit_rings:
            elapsed = (current_time - r['start_time']) / 300.0
            r['radius'] = r['radius'] + (r['max_radius'] - r['radius']) * 0.2
            r['alpha'] = int(180 * (1 - elapsed))
        
    def draw(self, screen):
        """绘制所有粒子"""
        for p in self.particles:
            p.draw(screen)
        
        # 绘制命中圆环
        for r in self._hit_rings:
            if r['alpha'] > 5:
                ring_surf = pygame.Surface((int(r['radius'] * 2), int(r['radius'] * 2)), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*r['color'], r['alpha']), 
                                  (int(r['radius']), int(r['radius'])), 
                                  int(r['radius']), 3)
                screen.blit(ring_surf, (r['x'] - r['radius'], r['y'] - r['radius']))
    
    def clear(self):
        """清除所有粒子"""
        self.particles = []


class ScreenShake:
    """屏幕震动效果"""
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.current_time = 0
        self._offset_x = 0
        self._offset_y = 0
    
    def trigger(self, intensity=10, duration=0.3):
        """触发屏幕震动"""
        self.intensity = intensity
        self.duration = duration
        self.current_time = 0
    
    def update(self, dt):
        """更新震动"""
        if self.duration > 0:
            self.current_time += dt
            progress = self.current_time / self.duration
            if progress >= 1:
                self.intensity = 0
                self._offset_x = 0
                self._offset_y = 0
                return False
            # 衰减曲线
            decay = 1 - progress
            current_intensity = self.intensity * decay
            import random
            self._offset_x = random.uniform(-current_intensity, current_intensity)
            self._offset_y = random.uniform(-current_intensity, current_intensity)
            return True
        return False
    
    def get_offset(self):
        """获取当前偏移量"""
        return self._offset_x, self._offset_y
    
    def apply(self, screen):
        """应用震动到屏幕"""
        if self.intensity > 0:
            return screen.copy()
        return screen

# 全局屏幕震动实例
_global_screen_shake = None

def get_screen_shake():
    """获取全局屏幕震动"""
    global _global_screen_shake
    if _global_screen_shake is None:
        _global_screen_shake = ScreenShake()
    return _global_screen_shake


# 全局粒子系统实例
_global_particle_system = None

def get_particle_system():
    """获取全局粒子系统"""
    global _global_particle_system
    if _global_particle_system is None:
        _global_particle_system = ParticleSystem()
    return _global_particle_system


def create_hit_particles(x, y, tower_type):
    """根据塔类型创建命中特效"""
    ps = get_particle_system()
    
    # 不同塔类型不同颜色
    colors = {
        '箭塔': (100, 200, 100),    # 绿色
        '炮塔': (255, 100, 50),     # 橙红色
        '魔法塔': (150, 100, 255),  # 紫色
    }
    
    color = colors.get(tower_type, (200, 200, 200))
    ps.emit_hit(x, y, color)


def create_trail_particles(x, y, tower_type):
    """创建拖尾粒子"""
    ps = get_particle_system()
    
    colors = {
        '箭塔': (150, 220, 150),
        '炮塔': (255, 150, 100),
        '魔法塔': (180, 140, 255),
    }
    
    color = colors.get(tower_type, (200, 200, 200))
    ps.emit_trail(x, y, color)