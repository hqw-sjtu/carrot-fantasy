"""
保卫萝卜 - 连击计时器条形组件
Carrot Fantasy - Combo Timer Bar Component
显示连击剩余时间，让玩家更直观把握连击节奏
"""
import pygame
import math


class ComboTimerBar:
    """连击计时器条形显示"""
    
    def __init__(self, x, y, width=200, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.current_time = 0  # 当前剩余时间
        self.max_time = 3.0    # 最大连击时间
        self.active = False
        self.combo_count = 0
        self.glow_phase = 0
        
        # 颜色配置
        self.colors = {
            'bg': (30, 30, 40),
            'fill_low': (200, 60, 60),      # 红色 - 时间紧迫
            'fill_mid': (220, 180, 50),     # 黄色 - 中等
            'fill_high': (60, 200, 100),    # 绿色 - 充裕
            'border': (100, 100, 120),
            'text': (255, 255, 255),
            'glow': (255, 200, 100)
        }
        
    def trigger(self, combo_count, duration=3.0):
        """触发连击计时器"""
        self.active = True
        self.combo_count = combo_count
        self.max_time = duration
        self.current_time = duration
        
    def update(self, dt):
        """更新计时器"""
        if not self.active:
            return
            
        self.current_time -= dt
        self.glow_phase += dt * 5  # 光晕动画速度
        
        if self.current_time <= 0:
            self.current_time = 0
            self.active = False
            self.combo_count = 0
            
    def get_fill_color(self):
        """获取填充颜色（基于剩余时间百分比）"""
        ratio = self.current_time / self.max_time if self.max_time > 0 else 0
        
        if ratio > 0.5:
            return self.colors['fill_high']
        elif ratio > 0.25:
            return self.colors['fill_mid']
        else:
            return self.colors['fill_low']
            
    def draw(self, screen):
        """绘制计时器条"""
        if not self.active and self.current_time <= 0:
            return
            
        # 计算填充宽度
        ratio = self.current_time / self.max_time if self.max_time > 0 else 0
        fill_width = int(self.width * ratio)
        
        # 背景
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.colors['bg'], bg_rect, border_radius=4)
        
        # 填充条
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            
            # 添加渐变效果
            fill_color = self.get_fill_color()
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=4)
            
            # 光晕效果
            if ratio > 0:
                glow_alpha = int(100 + 50 * math.sin(self.glow_phase))
                # 这里可以添加更复杂的光晕渲染
                
        # 边框
        pygame.draw.rect(screen, self.colors['border'], bg_rect, 2, border_radius=4)
        
        # 连击数显示
        if self.combo_count > 1:
            font = pygame.font.Font(None, 24)
            combo_text = f"x{self.combo_count}"
            text_surf = font.render(combo_text, True, self.colors['text'])
            
            # 位置：条右侧
            text_x = self.x + self.width + 10
            text_y = self.y + (self.height - text_surf.get_height()) // 2
            screen.blit(text_surf, (text_x, text_y))
            
        # 剩余时间数字
        font_small = pygame.font.Font(None, 18)
        time_text = f"{self.current_time:.1f}s"
        time_surf = font_small.render(time_text, True, self.colors['text'])
        
        # 位置：条内部居中
        time_x = self.x + (self.width - time_surf.get_width()) // 2
        time_y = self.y + (self.height - time_surf.get_height()) // 2
        
        # 如果填充条覆盖了文字，添加阴影
        if fill_width > 10:
            shadow_surf = font_small.render(time_text, True, (0, 0, 0))
            screen.blit(shadow_surf, (time_x + 1, time_y + 1))
            
        screen.blit(time_surf, (time_x, time_y))


class ComboTimerBarManager:
    """连击计时器管理器（单例）"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ComboTimerBar(100, 80)  # 默认位置：顶部中央
        return cls._instance
    
    @classmethod
    def trigger(cls, combo_count, duration=3.0):
        cls.get_instance().trigger(combo_count, duration)
    
    @classmethod
    def update(cls, dt):
        cls.get_instance().update(dt)
    
    @classmethod
    def draw(cls, screen):
        cls.get_instance().draw(screen)
    
    @classmethod
    def set_position(cls, x, y):
        """设置显示位置"""
        instance = cls.get_instance()
        instance.x = x
        instance.y = y
        
    @classmethod
    def set_size(cls, width, height):
        """设置尺寸"""
        instance = cls.get_instance()
        instance.width = width
        instance.height = height