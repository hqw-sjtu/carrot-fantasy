"""
保卫萝卜 - Boss血条系统
Boss出现时显示专用血条
"""
import math
import pygame


class BossHPBar:
    """Boss血条显示"""
    
    def __init__(self, monster):
        self.monster = monster
        self.max_width = 200
        self.height = 20
        self.y_offset = -40  # 在怪物上方
        self.show_timer = 3.0  # 首次出现显示3秒
        self.pulse_timer = 0
        # 入场动画
        self.entrance_progress = 0.0  # 0-1入场动画进度
        self.entrance_duration = 1.5  # 入场动画1.5秒
        self.entrance_started = False
        self.slide_offset = 0
        
    def update(self, dt):
        """更新血条"""
        if self.monster.alive:
            self.show_timer = 2.0  # 持续显示
            self.pulse_timer += dt
            # 入场动画
            if not self.entrance_started:
                self.entrance_started = True
            if self.entrance_progress < 1.0:
                self.entrance_progress = min(1.0, self.entrance_progress + dt / self.entrance_duration)
                # 缓动函数: ease-out-back
                c1 = 1.70158
                c3 = c1 + 1
                progress = self.entrance_progress
                self.slide_offset = (1 + c3 * (progress - 1) ** 3 + c1 * (progress - 1) ** 2) * 60
            
    def draw(self, screen):
        """绘制血条"""
        if not self.monster.alive:
            return
            
        # 血条位置（加入场动画偏移）
        x = self.monster.x - self.max_width // 2
        y = self.monster.y + self.y_offset - self.slide_offset
        
        # 血量比例
        health_ratio = max(0, self.monster.health / self.monster.max_health)
        current_width = int(self.max_width * health_ratio)
        
        if current_width <= 0:
            return
            
        # 背景框
        bg_rect = pygame.Rect(x - 2, y - 2, self.max_width + 4, self.height + 4)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 2)
        
        # 血条底色
        bar_bg = pygame.Rect(x, y, self.max_width, self.height)
        pygame.draw.rect(screen, (80, 20, 20), bar_bg)
        
        # 血条（渐变色：红->黄->绿）
        if health_ratio > 0.6:
            bar_color = (50, 200, 50)  # 绿色
        elif health_ratio > 0.3:
            bar_color = (255, 200, 0)  # 黄色
        else:
            # 低血量脉动效果
            pulse = int(50 + 30 * math.sin(self.pulse_timer * 10))
            bar_color = (255, pulse, 50)
        
        bar = pygame.Rect(x, y, current_width, self.height)
        pygame.draw.rect(screen, bar_color, bar)
        
        # Boss名称
        font = pygame.font.SysFont('SimHei', 14)
        name = self.monster.name if hasattr(self.monster, 'name') else 'BOSS'
        text = font.render(name, True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + self.max_width // 2, y - 12))
        screen.blit(text, text_rect)
        
        # 血量数值
        hp_text = font.render(f"{int(self.monster.health)}/{int(self.monster.max_health)}", True, (255, 255, 255))
        hp_rect = hp_text.get_rect(center=(x + self.max_width // 2, y + self.height + 10))
        screen.blit(hp_text, hp_rect)


class BossWarningEffect:
    """Boss来袭警告特效"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.active = False
        self.timer = 0
        self.duration = 2.0
        self.flash_interval = 0.3
        self.flash_timer = 0
        self.is_red = False
        
    def activate(self):
        """激活警告"""
        self.active = True
        self.timer = 0
        
    def update(self, dt):
        """更新"""
        if not self.active:
            return
        self.timer += dt
        self.flash_timer += dt
        
        if self.flash_timer >= self.flash_interval:
            self.flash_timer = 0
            self.is_red = not self.is_red
            
        if self.timer >= self.duration:
            self.active = False
            
    def draw(self, screen):
        """绘制警告"""
        if not self.active:
            return
            
        if self.is_red:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 30))
            screen.blit(overlay, (0, 0))
            
            # 警告文字
            font = pygame.font.SysFont('SimHei', 48)
            text = font.render("⚠️ BOSS来袭 ⚠️", True, (255, 50, 50))
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
            
            # 发光背景
            glow = font.render("⚠️ BOSS来袭 ⚠️", True, (255, 150, 50))
            glow_rect = glow.get_rect(center=(self.width // 2 + 2, self.height // 2 + 2))
            screen.blit(glow, glow_rect)
            screen.blit(text, text_rect)
