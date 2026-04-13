"""
保卫萝卜 - 暴击与连击增强系统
Carrot Fantasy - Critical Hit & Combo Enhancement System
增强暴击伤害显示和连击特效
"""
import pygame
import random
import math


class CriticalHit:
    """暴击效果"""
    
    def __init__(self, x, y, damage, is_crit=False):
        self.x = x
        self.y = y
        self.damage = damage
        self.is_crit = is_crit
        
        # 动画
        self.life = 1.0  # 生命周期
        self.max_life = 1.2  # 1.2秒
        self.vy = -80  # 向上飘动速度
        
        # 颜色
        if is_crit:
            self.color = (255, 50, 50)  # 红色
            self.glow_color = (255, 200, 0)  # 金色光晕
            self.scale = 1.8  # 暴击放大
            self.font_size = 36
        else:
            self.color = (255, 220, 100)
            self.glow_color = None
            self.scale = 1.0
            self.font_size = 24
        
        # 震动效果
        self.shake = 0
        self.shake_intensity = 3 if is_crit else 0
        
        # 星星爆发（暴击时）
        self.stars = []
        if is_crit:
            for _ in range(8):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(50, 120)
                self.stars.append({
                    'x': 0, 'y': 0,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'life': 1.0,
                    'size': random.randint(2, 5)
                })
    
    def update(self, dt):
        """更新状态"""
        self.life -= dt
        self.y += self.vy * dt
        self.vy *= 0.98  # 减速
        
        # 震动
        if self.shake_intensity > 0:
            self.shake = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity *= 0.9
        
        # 更新星星
        for star in self.stars:
            star['x'] += star['vx'] * dt
            star['y'] += star['vy'] * dt
            star['life'] -= dt * 2
        
        return self.life > 0
    
    def draw(self, SCREEN, font):
        """绘制"""
        if self.life <= 0:
            return
        
        # 淡出
        alpha = min(255, int(255 * (self.life / self.max_life) * 255))
        
        # 绘制星星（暴击）
        for star in self.stars:
            if star['life'] > 0:
                star_alpha = int(255 * star['life'])
                star_color = (*self.glow_color, star_alpha) if self.glow_color else (*self.color, star_alpha)
                pygame.draw.circle(
                    SCREEN, 
                    self.glow_color or self.color,
                    (int(self.x + star['x']), int(self.y + star['y'])),
                    star['size']
                )
        
        # 绘制文字
        text = f"{int(self.damage)}"
        if self.is_crit:
            text = f"暴击! {text}"
        
        # 放大效果
        current_scale = self.scale * (1 + 0.1 * (1 - self.life / self.max_life))
        
        # 渲染
        try:
            actual_size = int(self.font_size * current_scale)
            if actual_size > 0:
                temp_font = pygame.font.Font(None, actual_size)
                text_surface = temp_font.render(text, True, self.color)
                
                # 光晕
                if self.is_crit and self.glow_color:
                    glow_surface = temp_font.render(text, True, self.glow_color)
                    for ox, oy in [(-2,-2), (2,-2), (-2,2), (2,2)]:
                        SCREEN.blit(glow_surface, 
                            (int(self.x + ox + self.shake - glow_surface.get_width()//2),
                             int(self.y + oy + self.shake - glow_surface.get_height()//2)))
                
                # 主文字
                text_surface.set_alpha(alpha)
                SCREEN.blit(text_surface, 
                    (int(self.x + self.shake - text_surface.get_width()//2),
                     int(self.y + self.shake - text_surface.get_height()//2)))
        except:
            pass


class ComboText:
    """连击文字显示"""
    
    def __init__(self, x, y, combo_count):
        self.x = x
        self.y = y
        self.combo_count = combo_count
        
        self.life = 1.0
        self.max_life = 0.8
        
        # 颜色渐变
        if combo_count >= 10:
            self.color = (255, 50, 255)  # 紫色-超级连击
            self.glow = (255, 200, 255)
        elif combo_count >= 5:
            self.color = (255, 150, 0)  # 橙色-高级连击
            self.glow = (255, 255, 100)
        else:
            self.color = (100, 200, 255)  # 蓝色-普通连击
        
        self.scale = 1.0 + min(combo_count * 0.1, 1.0)
        self.vy = -60
    
    def update(self, dt):
        self.life -= dt
        self.y += self.vy * dt
        self.scale *= 1.01  # 逐渐变大
        return self.life > 0
    
    def draw(self, SCREEN, font):
        if self.life <= 0:
            return
        
        text = f"COMBO x{self.combo_count}!"
        alpha = int(255 * (self.life / self.max_life))
        
        size = int(32 * self.scale)
        try:
            temp_font = pygame.font.Font(None, size)
            text_surface = temp_font.render(text, True, self.color)
            text_surface.set_alpha(alpha)
            
            # 描边效果
            outline = temp_font.render(text, True, (0, 0, 0))
            outline.set_alpha(alpha // 2)
            SCREEN.blit(outline, (self.x - 1, self.y))
            SCREEN.blit(outline, (self.x + 1, self.y))
            SCREEN.blit(outline, (self.x, self.y - 1))
            SCREEN.blit(outline, (self.x, self.y + 1))
            
            SCREEN.blit(text_surface, (self.x, self.y))
        except:
            pass


class UpgradeBurst:
    """升级爆发特效"""
    
    def __init__(self, x, y, level):
        self.x = x
        self.y = y
        self.level = level
        
        self.life = 1.0
        self.max_life = 0.6
        
        # 光圈
        self.rings = []
        for i in range(3):
            self.rings.append({
                'radius': 10,
                'max_radius': 40 + level * 10,
                'alpha': 255
            })
        
        # 粒子
        self.particles = []
        for _ in range(12):
            angle = i * (math.pi * 2 / 12)
            self.particles.append({
                'x': 0, 'y': 0,
                'vx': math.cos(angle) * 100,
                'vy': math.sin(angle) * 100,
                'life': 1.0
            })
    
    def update(self, dt):
        self.life -= dt
        
        for ring in self.rings:
            ring['radius'] += 80 * dt
            ring['alpha'] = int(255 * (1 - ring['radius'] / ring['max_radius']))
        
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt * 2
        
        return self.life > 0
    
    def draw(self, SCREEN):
        if self.life <= 0:
            return
        
        center = (int(self.x), int(self.y))
        
        # 绘制光圈
        for ring in self.rings:
            if ring['alpha'] > 0:
                try:
                    pygame.draw.circle(SCREEN, (255, 200, 50), center, int(ring['radius']), 2)
                except:
                    pass
        
        # 绘制粒子
        for p in self.particles:
            if p['life'] > 0:
                alpha = int(255 * p['life'])
                color = (255, 220, 100)
                px = int(self.x + p['x'])
                py = int(self.y + p['y'])
                pygame.draw.circle(SCREEN, color, (px, py), 3)


# 全局效果列表
critical_hits = []
combo_texts = []
upgrade_bursts = []


def add_critical_hit(x, y, damage, is_crit=False):
    """添加暴击效果"""
    critical_hits.append(CriticalHit(x, y, damage, is_crit))


def add_combo_text(x, y, combo_count):
    """添加连击文字"""
    combo_texts.append(ComboText(x, y, combo_count))


def add_upgrade_burst(x, y, level):
    """添加升级爆发"""
    upgrade_bursts.append(UpgradeBurst(x, y, level))


def update_effects(dt):
    """更新所有效果"""
    global critical_hits, combo_texts, upgrade_bursts
    
    critical_hits = [c for c in critical_hits if c.update(dt)]
    combo_texts = [c for c in combo_texts if c.update(dt)]
    upgrade_bursts = [b for b in upgrade_bursts if b.update(dt)]


def draw_effects(SCREEN, font=None):
    """绘制所有效果"""
    for hit in critical_hits:
        hit.draw(SCREEN, font)
    for combo in combo_texts:
        combo.draw(SCREEN, font)
    for burst in upgrade_bursts:
        burst.draw(SCREEN)