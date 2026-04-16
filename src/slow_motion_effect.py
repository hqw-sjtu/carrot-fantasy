"""
Slow Motion Effect System - 子弹时间系统
在关键时刻减缓游戏速度，让玩家更好部署防御塔
"""

import pygame
import math


class SlowMotionEffect:
    """子弹时间效果控制器"""
    
    def __init__(self):
        self.active = False
        self.duration = 3.0  # 持续时间(秒)
        self.elapsed = 0.0
        self.slow_factor = 0.3  # 时间减缓因子(30%速度)
        self.transition_speed = 2.0  # 切换速度
        self.current_time_scale = 1.0
        self.vignette_alpha = 0
        self.max_vignette_alpha = 180
        self.particles = []  # 时间流动粒子
        self.screen_shake = 0
        self.max_energy = 100
        self.energy = self.max_energy  # 能量条
        self.energy_cost = 25  # 每次消耗能量
        self.recharge_rate = 10  # 每秒恢复能量
        self.ready = True
        
    def activate(self):
        """激活子弹时间"""
        if self.energy >= self.energy_cost and not self.active:
            self.active = True
            self.elapsed = 0.0
            self.ready = False
            self.energy -= self.energy_cost
            return True
        return False
        
    def deactivate(self):
        """停止子弹时间"""
        self.active = False
        
    def update(self, dt):
        """更新子弹时间效果"""
        # 限制能量在有效范围内
        self.energy = max(0, min(self.max_energy, self.energy))
        
        # 更新能量
        if not self.active and self.energy < self.max_energy:
            self.energy = min(self.max_energy, self.energy + self.recharge_rate * dt)
            
        if self.energy >= self.energy_cost:
            self.ready = True
        else:
            self.ready = False
            
        if not self.active:
            # 时间缩放恢复到1
            self.current_time_scale = max(1.0, self.current_time_scale - self.transition_speed * dt)
            self.vignette_alpha = max(0, self.vignette_alpha - 150 * dt)
            self.screen_shake = max(0, self.screen_shake - 10 * dt)
            return 1.0
            
        self.elapsed += dt
        
        # 自动结束
        if self.elapsed >= self.duration:
            self.active = False
            
        # 平滑过渡时间缩放
        target_scale = self.slow_factor if self.active else 1.0
        self.current_time_scale += (target_scale - self.current_time_scale) * self.transition_speed * dt
        
        # 暗角效果
        if self.active:
            self.vignette_alpha = min(self.max_vignette_alpha, self.vignette_alpha + 200 * dt)
        else:
            self.vignette_alpha = max(0, self.vignette_alpha - 150 * dt)
            
        # 屏幕轻微震动
        if self.active:
            self.screen_shake = min(3.0, self.screen_shake + 5 * dt)
        else:
            self.screen_shake = max(0, self.screen_shake - 10 * dt)
            
        # 更新时间粒子
        self._update_particles(dt)
        
        return self.current_time_scale
        
    def _update_particles(self, dt):
        """更新时间流动粒子"""
        # 生成新粒子
        if self.active and len(self.particles) < 30 and random.random() < 0.3:
            self.particles.append({
                'x': random.randint(50, 750),
                'y': random.randint(50, 550),
                'size': random.randint(2, 4),
                'speed': random.uniform(20, 40),
                'alpha': random.randint(100, 200),
                'trail': []
            })
            
        # 更新现有粒子
        for p in self.particles[:]:
            p['y'] += p['speed'] * dt * self.current_time_scale
            p['alpha'] -= 50 * dt
            
            # 记录轨迹
            p['trail'].append((p['x'], p['y']))
            if len(p['trail']) > 5:
                p['trail'].pop(0)
                
            if p['y'] > 600 or p['alpha'] <= 0:
                self.particles.remove(p)
                
    def draw(self, surface):
        """绘制子弹时间效果"""
        # 绘制时间粒子
        for p in self.particles:
            if p['alpha'] > 0:
                color = (200, 220, 255, int(p['alpha']))
                pygame.draw.circle(
                    surface, color[:3],
                    (int(p['x']), int(p['y'])),
                    p['size']
                )
                # 绘制轨迹
                for i, (tx, ty) in enumerate(p['trail']):
                    trail_alpha = int(p['alpha'] * (i / len(p['trail'])))
                    trail_color = (200, 220, 255)
                    pygame.draw.circle(
                        surface, trail_color,
                        (int(tx), int(ty)),
                        max(1, p['size'] * i // len(p['trail']))
                    )
                    
        # 绘制暗角效果
        if self.vignette_alpha > 0:
            self._draw_vignette(surface)
            
        # 绘制能量条
        self._draw_energy_bar(surface)
        
    def _draw_vignette(self, surface):
        """绘制暗角效果"""
        w, h = surface.get_size()
        # 创建径向渐变
        center_rect = pygame.Rect(
            w // 4, h // 4, w // 2, h // 2
        )
        
        # 简单暗角覆盖
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # 四角加深
        corners = [
            (0, 0, w // 2, h // 2),
            (w // 2, 0, w // 2, h // 2),
            (0, h // 2, w // 2, h // 2),
            (w // 2, h // 2, w // 2, h // 2)
        ]
        
        for cx, cy, cw, ch in corners:
            pygame.draw.rect(
                overlay,
                (0, 0, 50, int(self.vignette_alpha * 0.5)),
                (cx, cy, cw, ch)
            )
            
        surface.blit(overlay, (0, 0))
        
    def _draw_energy_bar(self, surface):
        """绘制能量条"""
        bar_width = 150
        bar_height = 12
        bar_x = 20
        bar_y = 60
        
        # 背景
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (40, 40, 50), bg_rect)
        pygame.draw.rect(surface, (100, 100, 120), bg_rect, 2)
        
        # 能量填充
        energy_width = int(bar_width * (self.energy / self.max_energy))
        energy_color = (0, 200, 255) if self.ready else (100, 100, 100)
        energy_rect = pygame.Rect(bar_x, bar_y, energy_width, bar_height)
        pygame.draw.rect(surface, energy_color, energy_rect)
        
        # 文字标签
        font = pygame.font.Font(None, 18)
        text = font.render("SLOW-MO", True, (200, 220, 255))
        surface.blit(text, (bar_x, bar_y - 16))
        
        # 状态指示
        if self.active:
            status = "ACTIVE"
            status_color = (255, 100, 100)
        elif self.ready:
            status = "READY [Z]"
            status_color = (100, 255, 100)
        else:
            status = "CHARGING"
            status_color = (200, 200, 100)
            
        status_text = font.render(status, True, status_color)
        surface.blit(status_text, (bar_x + bar_width + 10, bar_y - 2))
        
    def get_time_scale(self):
        """获取当前时间缩放因子"""
        return self.current_time_scale
        
    def is_active(self):
        """是否处于子弹时间"""
        return self.active


# 随机数需要导入
import random