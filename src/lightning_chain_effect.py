"""
闪电链特效系统 (Lightning Chain Effect)
工艺品级别 - 链式闪电攻击视觉效果

功能:
- 链式闪电在多个目标间跳跃
- 动态分叉闪电效果
- 电弧闪烁动画
- 伤害数字联动
"""

import pygame
import random
import math
import time


class LightningSegment:
    """闪电线段"""
    
    def __init__(self, start_pos, end_pos, color=(200, 220, 255), width=2):
        self.start = start_pos
        self.end = end_pos
        self.color = color
        self.width = width
        self.lifetime = 0.15  # 闪电持续时间
        self.age = 0
        
    def update(self, dt):
        self.age += dt
        return self.age < self.lifetime
    
    def draw(self, surface):
        # 闪烁效果
        alpha = max(0, 1 - self.age / self.lifetime)
        if random.random() > 0.3:  # 闪烁
            pygame.draw.line(surface, self.color, self.start, self.end, self.width)


class LightningBolt:
    """单道闪电"""
    
    def __init__(self, start_pos, end_pos, intensity=1.0):
        self.start = start_pos
        self.end = end_pos
        self.intensity = intensity
        self.segments = []
        self.generate_bolt()
        self.lifetime = 0.2 + random.random() * 0.1
        self.age = 0
        
    def generate_bolt(self):
        """生成闪电路径(带分叉)"""
        self.segments = []
        
        # 主闪电路径
        points = [self.start]
        num_segments = 8
        
        for i in range(1, num_segments):
            t = i / num_segments
            x = self.start[0] + (self.end[0] - self.start[0]) * t
            y = self.start[1] + (self.end[1] - self.start[1]) * t
            
            # 添加随机偏移(闪电锯齿效果)
            offset_range = 30 * self.intensity
            x += random.uniform(-offset_range, offset_range)
            y += random.uniform(-offset_range, offset_range)
            points.append((x, y))
        
        points.append(self.end)
        
        # 创建线段
        for i in range(len(points) - 1):
            color = self._get_bolt_color(i, len(points))
            width = max(1, 4 - i // 2)
            self.segments.append(LightningSegment(
                points[i], points[i + 1], color, width
            ))
        
        # 随机分叉
        if self.intensity > 0.5 and random.random() > 0.5:
            branch_start = random.randint(1, len(points) - 2)
            branch_angle = random.uniform(-math.pi / 3, math.pi / 3)
            branch_length = random.uniform(50, 100) * self.intensity
            
            branch_end = (
                points[branch_start][0] + math.cos(branch_angle) * branch_length,
                points[branch_start][1] + math.sin(branch_angle) * branch_length
            )
            
            color = (180, 200, 255)
            self.segments.append(LightningSegment(
                points[branch_start], branch_end, color, 1
            ))
    
    def _get_bolt_color(self, index, total):
        """闪电渐变色"""
        colors = [
            (255, 255, 255),  # 白色核心
            (200, 220, 255),  # 浅蓝
            (150, 180, 255),  # 蓝色
            (100, 150, 255),  # 深蓝
        ]
        t = index / max(1, total - 1)
        idx = min(int(t * len(colors)), len(colors) - 1)
        return colors[idx]
    
    def update(self, dt):
        self.age += dt
        alive = []
        for seg in self.segments:
            if seg.update(dt):
                alive.append(seg)
        self.segments = alive
        return self.age < self.lifetime
    
    def draw(self, surface):
        for seg in self.segments:
            seg.draw(surface)


class LightningChainEffect:
    """闪电链特效管理器"""
    
    def __init__(self):
        self.bolts = []
        self.particles = []  # 电弧粒子
        self.last_target = None
        
    def create_chain(self, start_pos, targets, intensity=1.0):
        """创建闪电链
        
        Args:
            start_pos: 起始位置
            targets: 目标位置列表
            intensity: 闪电强度 (0-1)
        """
        if not targets:
            return
        
        # 起始点 -> 第一个目标
        self.bolts.append(LightningBolt(start_pos, targets[0], intensity))
        self._spawn_sparks(start_pos)
        
        # 目标间链式跳跃
        for i in range(len(targets) - 1):
            self.bolts.append(LightningBolt(targets[i], targets[i + 1], intensity * 0.8))
            self._spawn_sparks(targets[i])
        
        self.last_target = targets[-1] if targets else None
        
    def _spawn_sparks(self, pos):
        """生成电弧粒子"""
        for _ in range(5):
            self.particles.append({
                'pos': list(pos),
                'vel': [random.uniform(-100, 100), random.uniform(-100, 100)],
                'life': random.uniform(0.2, 0.4),
                'max_life': 0.4,
                'color': (random.randint(150, 255), random.randint(200, 255), 255)
            })
    
    def update(self, dt):
        """更新特效"""
        # 更新闪电
        alive_bolts = []
        for bolt in self.bolts:
            if bolt.update(dt):
                alive_bolts.append(bolt)
        self.bolts = alive_bolts
        
        # 更新粒子
        alive_particles = []
        for p in self.particles:
            p['life'] -= dt
            p['pos'][0] += p['vel'][0] * dt
            p['pos'][1] += p['vel'][1] * dt
            p['vel'][0] *= 0.95  # 阻尼
            p['vel'][1] *= 0.95
            
            if p['life'] > 0:
                alive_particles.append(p)
        self.particles = alive_particles
        
        return len(self.bolts) > 0 or len(self.particles) > 0
    
    def draw(self, surface):
        """绘制特效"""
        # 绘制闪电
        for bolt in self.bolts:
            bolt.draw(surface)
        
        # 绘制粒子
        for p in self.particles:
            alpha = p['life'] / p['max_life']
            size = max(1, int(3 * alpha))
            color = p['color']
            
            # 绘制发光效果
            for r in range(size, 0, -1):
                a = int(255 * alpha * (1 - r / size))
                surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*color, a), (r, r), r)
                surface.blit(surf, (p['pos'][0] - r, p['pos'][1] - r))


# 单例
_instance = None

def get_instance():
    global _instance
    if _instance is None:
        _instance = LightningChainEffect()
    return _instance

def reset():
    global _instance
    _instance = None


if __name__ == '__main__':
    # 测试
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    effect = LightningChainEffect()
    
    # 模拟目标
    targets = [(400, 300), (450, 250), (500, 350)]
    
    running = True
    while running:
        dt = clock.tick(60) / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 点击生成新闪电
                targets = [
                    (random.randint(200, 600), random.randint(150, 450)),
                    (random.randint(200, 600), random.randint(150, 450)),
                    (random.randint(200, 600), random.randint(150, 450))
                ]
                effect.create_chain((400, 100), targets)
        
        screen.fill((20, 20, 40))
        
        # 绘制目标点
        for t in targets:
            pygame.draw.circle(screen, (255, 50, 50), t, 10)
        
        # 更新和绘制
        effect.update(dt)
        effect.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()