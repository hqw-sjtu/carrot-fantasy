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


class LightningChainEffect:
    """闪电链式攻击特效 - 电塔链式攻击视觉效果"""
    
    def __init__(self, start_pos, target_positions, color=(150, 150, 255)):
        self.start_pos = start_pos  # 起始点（塔位置）
        self.target_positions = target_positions  # 目标点列表（多个敌人）
        self.color = color
        self.max_life = 0.4  # 400ms闪电持续
        self.life = 0
        self.active = True
        self.segments = []  # 闪电线段
        self._generate_lightning()
        
    def _generate_lightning(self):
        """生成闪电路径"""
        for target in self.target_positions:
            segments = []
            points = [self.start_pos, target]
            # 在两点之间插入随机偏移点形成闪电效果
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                mid_x = (start[0] + end[0]) / 2
                mid_y = (start[1] + end[1]) / 2
                # 添加随机偏移
                offset = random.uniform(-30, 30)
                if abs(start[0] - end[0]) > abs(start[1] - end[1]):
                    mid_y += offset
                else:
                    mid_x += offset
                segments.append((start, (mid_x, mid_y)))
                segments.append(((mid_x, mid_y), end))
            self.segments.append(segments)
            
    def update(self, dt):
        self.life += dt
        if self.life >= self.max_life:
            self.active = False
            # 重新生成闪电产生闪烁效果
            if self.life < self.max_life * 1.5:
                self._generate_lightning()
                self.active = True
                
    def draw(self, screen):
        if not self.active:
            return
        alpha = int(255 * (1 - self.life / self.max_life))
        # 绘制闪电
        for segments in self.segments:
            for i, (start, end) in enumerate(segments):
                width = 3 if i % 2 == 0 else 1
                color = (*self.color, alpha)
                pygame.draw.line(screen, color, start, end, width)
                # 发光效果
                glow_color = (*self.color, alpha // 4)
                pygame.draw.line(screen, glow_color, start, end, width * 4)


class ShockwaveEffect:
    """冲击波特效 - 强力攻击时的环形扩散效果"""
    
    def __init__(self, x, y, color=(255, 100, 100), max_radius=150):
        self.x = x
        self.y = y
        self.color = color
        self.max_radius = max_radius
        self.max_life = 0.8
        self.life = 0
        self.active = True
        
    def update(self, dt):
        self.life += dt
        if self.life >= self.max_life:
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
        progress = self.life / self.max_life
        # 多层冲击波
        for i in range(3):
            ring_progress = max(0, progress - i * 0.1)
            if ring_progress > 1:
                continue
            radius = self.max_radius * ring_progress
            alpha = int(255 * (1 - ring_progress) * 0.5)
            color = (*self.color, alpha)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(radius), 3)


class EffectManager:
    """特效管理器 - 统一管理所有游戏特效"""
    
    _instance = None
    
    def __init__(self):
        self.lightning_chains = []
        self.shockwaves = []
        self.trails = []
        self.gold_rains = []
        self.poison_clouds = []  # 新增毒云列表
        self.experience_manager = ExperienceManager.get_instance()
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def spawn_poison_cloud(self, x, y, duration=3.0, radius=80, damage=10, slow=0.4):
        """生成毒云特效"""
        cloud = PoisonCloudEffect(x, y, duration, radius, damage, slow)
        self.poison_clouds.append(cloud)
        return cloud
    
    def spawn_lightning_chain(self, start_pos, target_positions, color=(150, 150, 255)):
        """生成闪电链特效"""
        effect = LightningChainEffect(start_pos, target_positions, color)
        self.lightning_chains.append(effect)
        
    def spawn_shockwave(self, x, y, color=(255, 100, 100), max_radius=150):
        """生成冲击波特效"""
        effect = ShockwaveEffect(x, y, color, max_radius)
        self.shockwaves.append(effect)
        
    def spawn_attack_trail(self, start_pos, end_pos, color=(255, 200, 100), width=4):
        """生成攻击拖尾特效"""
        effect = TowerAttackTrailEffect(start_pos, end_pos, color, width)
        self.trails.append(effect)
        
    def spawn_gold_rain(self, screen_width, screen_height, count=50):
        """生成金币雨特效"""
        effect = GoldRainEffect(screen_width, screen_height, count)
        self.gold_rains.append(effect)
        
    def update(self, dt):
        """更新所有特效"""
        # 闪电链
        for effect in self.lightning_chains[:]:
            effect.update(dt)
            if not effect.active:
                self.lightning_chains.remove(effect)
        # 冲击波
        for effect in self.shockwaves[:]:
            effect.update(dt)
            if not effect.active:
                self.shockwaves.remove(effect)
        # 拖尾
        for effect in self.trails[:]:
            effect.update(dt)
            if not effect.active:
                self.trails.remove(effect)
        # 金币雨
        for effect in self.gold_rains[:]:
            effect.update(dt)
            if not effect.active:
                self.gold_rains.remove(effect)
        # 经验球
        self.experience_manager.update(dt)
        
    def draw(self, screen):
        """绘制所有特效"""
        for effect in self.lightning_chains:
            effect.draw(screen)
        for effect in self.shockwaves:
            effect.draw(screen)
        for effect in self.trails:
            effect.draw(screen)
        for effect in self.gold_rains:
            effect.draw(screen)
        self.experience_manager.draw(screen)


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


class PoisonCloudEffect:
    """毒云减速特效 - 范围内敌人持续受到减速和伤害"""
    
    def __init__(self, x, y, duration=3.0, radius=80, damage_per_second=10, slow_factor=0.4):
        self.x = x
        self.y = y
        self.duration = duration  # 持续时间
        self.radius = radius      # 毒云半径
        self.damage_per_second = damage_per_second
        self.slow_factor = slow_factor
        self.elapsed = 0
        self.active = True
        self.particles = []
        # 初始化毒气粒子
        for _ in range(20):
            self.particles.append({
                'x': x + random.uniform(-radius/2, radius/2),
                'y': y + random.uniform(-radius/2, radius/2),
                'vx': random.uniform(-15, 15),
                'vy': random.uniform(-15, 15),
                'size': random.uniform(8, 20),
                'alpha': random.uniform(100, 200),
                'life': random.uniform(0, 1)
            })
    
    def update(self, dt):
        """更新毒云状态"""
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False
            return
        
        # 更新粒子
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] += dt * 0.5
            p['alpha'] = int(200 * (1 - self.elapsed / self.duration) * (1 - p['life'] % 1))
            # 边界约束
            if abs(p['x'] - self.x) > self.radius:
                p['vx'] *= -0.5
            if abs(p['y'] - self.y) > self.radius:
                p['vy'] *= -0.5
    
    def draw(self, screen):
        """绘制毒云特效"""
        if not self.active:
            return
        
        # 绘制毒云底色
        progress = self.elapsed / self.duration
        alpha = int(80 * (1 - progress))
        
        # 外圈
        pygame.draw.circle(screen, (80, 40, 20, alpha), 
                          (int(self.x), int(self.y)), int(self.radius), 2)
        # 内圈
        pygame.draw.circle(screen, (100, 60, 30, alpha), 
                          (int(self.x), int(self.y)), int(self.radius * 0.6), 2)
        
        # 绘制毒气粒子
        for p in self.particles:
            if p['alpha'] > 10:
                color = (80 + int(p['life'] * 30), 50, 20, p['alpha'])
                rect = pygame.Rect(int(p['x'] - p['size']/2), 
                                   int(p['y'] - p['size']/2),
                                   int(p['size']), int(p['size']))
                pygame.draw.ellipse(screen, color, rect)
    
    def get_affected_area(self):
        """获取影响区域"""
        return {'x': self.x, 'y': self.y, 'radius': self.radius}


class ShieldEffect:
    """护盾保护特效 - 能量护盾环绕保护"""
    
    def __init__(self, x, y, color=(100, 200, 255), radius=40):
        self.x = x
        self.y = y
        self.color = color  # 护盾颜色
        self.radius = radius
        self.max_life = 3.0  # 3秒持续时间
        self.life = 0
        self.active = True
        self.rotation = 0
        self.rings = [
            {'angle': 0, 'speed': 30, 'size': 0.8},
            {'angle': 120, 'speed': -20, 'size': 0.6},
            {'angle': 240, 'speed': 40, 'size': 0.4},
        ]
        self.particles = []
        # 初始化粒子
        for _ in range(12):
            self.particles.append({
                'angle': random.uniform(0, 360),
                'dist': random.uniform(0.7, 1.0),
                'size': random.uniform(2, 5),
                'speed': random.uniform(0.5, 1.5),
                'alpha': random.uniform(150, 255),
            })
    
    def update(self, dt):
        self.life += dt
        self.rotation += 60 * dt  # 旋转速度
        if self.life >= self.max_life:
            self.active = False
            return
        # 更新环形
        for ring in self.rings:
            ring['angle'] += ring['speed'] * dt
        # 更新粒子
        for p in self.particles:
            p['angle'] += p['speed'] * 30 * dt
    
    def draw(self, screen):
        if not self.active:
            return
        
        progress = self.life / self.max_life
        base_alpha = int(255 * (1 - progress * 0.3))  # 慢慢淡出
        
        # 绘制外圈护盾
        pygame.draw.circle(screen, (*self.color, base_alpha // 4),
                          (int(self.x), int(self.y)), int(self.radius), 3)
        
        # 绘制能量环
        for ring in self.rings:
            ring_radius = self.radius * ring['size']
            start_angle = math.radians(ring['angle'] - 30)
            end_angle = math.radians(ring['angle'] + 30)
            pygame.draw.arc(screen, (*self.color, base_alpha // 2),
                           (self.x - ring_radius, self.y - ring_radius,
                            ring_radius * 2, ring_radius * 2),
                           start_angle, end_angle, 2)
        
        # 绘制旋转粒子
        for p in self.particles:
            angle_rad = math.radians(p['angle'])
            px = self.x + math.cos(angle_rad) * self.radius * p['dist']
            py = self.y + math.sin(angle_rad) * self.radius * p['dist']
            alpha = int(p['alpha'] * (1 - progress))
            color = (*self.color, alpha)
            pygame.draw.circle(screen, color, (int(px), int(py)), int(p['size']))
        
        # 绘制核心高亮
        center_alpha = int(base_alpha * 0.5)
        pygame.draw.circle(screen, (*self.color, center_alpha),
                          (int(self.x), int(self.y)), 5)


class RippleEffect:
    """波纹扩散特效 - 攻击命中时的水波扩散效果"""
    
    def __init__(self, x, y, color=(255, 255, 255), max_radius=60):
        self.x = x
        self.y = y
        self.color = color
        self.max_radius = max_radius
        self.max_life = 0.5  # 500ms
        self.life = 0
        self.active = True
        self.rings = [0, 0.2, 0.4]  # 三个波纹的时间偏移
    
    def update(self, dt):
        self.life += dt
        if self.life >= self.max_life:
            self.active = False
    
    def draw(self, screen):
        if not self.active:
            return
        
        for offset in self.rings:
            ring_time = self.life - offset
            if ring_time < 0 or ring_time > 0.15:
                continue
            progress = ring_time / 0.15
            radius = self.max_radius * progress
            alpha = int(255 * (1 - progress))
            pygame.draw.circle(screen, (*self.color, alpha),
                              (int(self.x), int(self.y)), int(radius), 2)


class ShatterEffect:
    """破碎特效 - 敌人被击杀时的碎片飞散效果"""
    
    def __init__(self, x, y, color=(255, 100, 100), count=12):
        self.x = x
        self.y = y
        self.color = color
        self.max_life = 0.8  # 800ms
        self.life = 0
        self.active = True
        self.count = count
        # 生成碎片
        self.fragments = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 200)
            self.fragments.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(3, 8),
                'rotation': random.uniform(0, 2 * math.pi),
                'rot_speed': random.uniform(-10, 10),
                'alpha': 255,
            })
        # 初始爆发速度
        for f in self.fragments:
            f['vx'] *= random.uniform(1.5, 3.0)
            f['vy'] *= random.uniform(1.5, 3.0)
    
    def update(self, dt):
        self.life += dt
        if self.life >= self.max_life:
            self.active = False
            return
        # 更新碎片位置和旋转
        for f in self.fragments:
            f['x'] += f['vx'] * dt
            f['y'] += f['vy'] * dt
            f['rotation'] += f['rot_speed'] * dt
            # 重力效果
            f['vy'] += 300 * dt  # 重力加速度
            # 淡出
            f['alpha'] = int(255 * (1 - self.life / self.max_life))
    
    def draw(self, screen):
        if not self.active:
            return
        for f in self.fragments:
            if f['alpha'] <= 0:
                continue
            color = (*self.color, f['alpha'])
            # 绘制菱形碎片
            size = f['size']
            points = []
            for angle_offset in [0, math.pi/2, math.pi, 3*math.pi/2]:
                angle = f['rotation'] + angle_offset
                px = f['x'] + math.cos(angle) * size
                py = f['y'] + math.sin(angle) * size
                points.append((int(px), int(py)))
            if len(points) >= 3:
                pygame.draw.polygon(screen, color, points)


class FreezeBlastEffect:
    """冰冻爆炸特效 - 冰塔技能命中时的冰晶爆发"""
    
    def __init__(self, x, y, color=(100, 200, 255), count=20):
        self.x = x
        self.y = y
        self.color = color
        self.max_life = 1.0  # 1秒
        self.life = 0
        self.active = True
        self.count = count
        # 生成冰晶
        self.crystals = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            self.crystals.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(2, 6),
                'alpha': 255,
                'type': random.choice(['crystal', 'snowflake']),
            })
    
    def update(self, dt):
        self.life += dt
        if self.life >= self.max_life:
            self.active = False
            return
        # 更新冰晶
        progress = self.life / self.max_life
        for c in self.crystals:
            c['x'] += c['vx'] * dt * (1 - progress * 0.5)
            c['y'] += c['vy'] * dt * (1 - progress * 0.5)
            # 减速
            c['vx'] *= 0.98
            c['vy'] *= 0.98
            c['alpha'] = int(255 * (1 - progress))
    
    def draw(self, screen):
        if not self.active:
            return
        for c in self.crystals:
            if c['alpha'] <= 0:
                continue
            color = (*self.color, c['alpha'])
            if c['type'] == 'crystal':
                # 绘制六边形冰晶
                size = c['size']
                points = []
                for i in range(6):
                    angle = i * math.pi / 3
                    px = c['x'] + math.cos(angle) * size
                    py = c['y'] + math.sin(angle) * size
                    points.append((int(px), int(py)))
                pygame.draw.polygon(screen, color, points)
            else:
                # 绘制雪花
                pygame.draw.circle(screen, color, (int(c['x']), int(c['y'])), int(c['size']))