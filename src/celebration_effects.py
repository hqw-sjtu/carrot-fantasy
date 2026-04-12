"""
保卫萝卜 - 关卡完成庆祝特效系统
Carrot Fantasy - Stage Complete Celebration Effects
"""
import pygame
import random
import math


class ConfettiParticle:
    """彩色纸屑粒子"""
    
    CONFETTI_COLORS = [
        (255, 70, 70),    # 红
        (70, 255, 70),    # 绿
        (70, 130, 255),   # 蓝
        (255, 255, 70),   # 黄
        (255, 70, 255),   # 紫
        (70, 255, 255),   # 青
        (255, 150, 70),   # 橙
        (255, 255, 255),  # 白
    ]
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-150, 150)
        self.vy = random.uniform(-400, -200)
        self.color = random.choice(self.CONFETTI_COLORS)
        self.size = random.randint(4, 10)
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-5, 5)
        self.gravity = 300
        self.lifetime = 3.0
        self.max_lifetime = 3.0
        
    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.rotation_speed * dt
        self.lifetime -= dt
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.lifetime <= 0:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 255:
            alpha = 255
        
        # 创建带旋转的矩形
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # 绘制纸屑
        color_with_alpha = (*self.color, alpha)
        pygame.draw.rect(surf, color_with_alpha, (0, 0, self.size, self.size))
        
        # 旋转并绘制
        rotated = pygame.transform.rotate(surf, math.degrees(self.rotation))
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated, rect)


class FireworkParticle:
    """烟花粒子"""
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(100, 300)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.gravity = 100
        self.lifetime = 1.5
        self.max_lifetime = 1.5
        self.trail = []
        
    def update(self, dt):
        # 记录轨迹
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.lifetime <= 0:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # 绘制轨迹
        for i, (tx, ty) in enumerate(self.trail):
            trail_alpha = int(alpha * (i / len(self.trail)) * 0.5)
            trail_color = (*self.color, trail_alpha)
            pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), 2)
        
        # 绘制粒子
        pygame.draw.circle(screen, (*self.color, alpha), (int(self.x), int(self.y)), 4)


class CelebrationEffect:
    """庆祝特效管理器"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.confetti = []
        self.fireworks = []
        self.active = False
        self.lifetime = 0
        self.max_lifetime = 4.0  # 4秒庆祝
        
    def start(self):
        """开始庆祝特效"""
        self.active = True
        self.lifetime = 0
        
        # 生成纸屑
        for _ in range(100):
            x = random.randint(100, self.width - 100)
            y = random.randint(-50, 100)
            self.confetti.append(ConfettiParticle(x, y))
        
        # 生成烟花
        firework_colors = [
            (255, 70, 70), (70, 255, 70), (70, 130, 255),
            (255, 255, 70), (255, 70, 255), (70, 255, 255)
        ]
        for _ in range(5):
            fx = random.randint(200, self.width - 200)
            fy = random.randint(100, self.height // 2)
            color = random.choice(firework_colors)
            self.fireworks.append(FireworkParticle(fx, fy, color))
    
    def update(self, dt):
        if not self.active:
            return
        
        self.lifetime += dt
        
        # 更新纸屑
        for c in self.confetti[:]:
            if not c.update(dt):
                self.confetti.remove(c)
        
        # 更新烟花
        for f in self.fireworks[:]:
            if not f.update(dt):
                self.fireworks.remove(f)
        
        # 添加新烟花
        if self.lifetime < self.max_lifetime and random.random() < 0.05:
            fx = random.randint(200, self.width - 200)
            fy = random.randint(100, self.height // 2)
            color = random.choice([
                (255, 70, 70), (70, 255, 70), (70, 130, 255),
                (255, 255, 70), (255, 70, 255), (70, 255, 255)
            ])
            self.fireworks.append(FireworkParticle(fx, fy, color))
        
        if self.lifetime >= self.max_lifetime and not self.confetti and not self.fireworks:
            self.active = False
    
    def draw(self, screen):
        if not self.active:
            return
        
        # 绘制纸屑
        for c in self.confetti:
            c.draw(screen)
        
        # 绘制烟花
        for f in self.fireworks:
            f.draw(screen)


class StageCompleteEffect:
    """关卡完成公告效果"""
    
    def __init__(self, screen_width, screen_height, score=0, stars=0):
        self.width = screen_width
        self.height = screen_height
        self.score = score
        self.stars = stars
        self.lifetime = 0
        self.max_lifetime = 3.0
        self.active = True
        self.scale = 0.0
        
    def update(self, dt):
        self.lifetime += dt
        
        # 缩放动画：0-0.5秒放大，0.5-2.5秒保持，2.5-3秒淡出
        if self.lifetime < 0.5:
            self.scale = self.lifetime / 0.5
        elif self.lifetime > 2.5:
            self.scale = 1.0 - (self.lifetime - 2.5) / 0.5
        else:
            self.scale = 1.0
        
        if self.lifetime >= self.max_lifetime:
            self.active = False
        
        return self.active
    
    def draw(self, screen):
        if not self.active:
            return
        
        # 半透明黑色背景
        bg_alpha = int(80 * self.scale)
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, bg_alpha))
        screen.blit(bg_surface, (0, 0))
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # 标题 "关卡完成!"
        title_font = pygame.font.SysFont('SimHei', int(72 * self.scale))
        title_color = (255, 215, 0)  # 金色
        title_shadow = pygame.font.SysFont('SimHei', int(74 * self.scale))
        
        title_surf = title_shadow.render("关卡完成!", True, (200, 150, 0))
        title_rect = title_surf.get_rect(center=(center_x, center_y - 80))
        screen.blit(title_surf, title_rect)
        
        title_text = title_font.render("关卡完成!", True, title_color)
        title_text_rect = title_text.get_rect(center=(center_x, center_y - 80))
        screen.blit(title_text, title_text_rect)
        
        # 星级显示
        star_font = pygame.font.SysFont('SimHei', int(48 * self.scale))
        star_text = "⭐" * self.stars + "☆" * (3 - self.stars)
        star_surf = star_font.render(star_text, True, (255, 255, 200))
        star_rect = star_surf.get_rect(center=(center_x, center_y))
        screen.blit(star_surf, star_rect)
        
        # 分数显示
        score_font = pygame.font.SysFont('SimHei', int(36 * self.scale))
        score_text = f"得分: {self.score}"
        score_surf = score_font.render(score_text, True, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(center_x, center_y + 60))
        screen.blit(score_surf, score_rect)
        
        # 外圈光芒动画
        pulse = 1.0 + 0.1 * math.sin(self.lifetime * 5)
        glow_radius = int(200 * pulse * self.scale)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 215, 0, 50), (glow_radius, glow_radius), glow_radius, 5)
        screen.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius))