"""
保卫萝卜 - 连击系统
Carrot Fantasy - Combo System
连续击杀显示连击数和奖励
"""
import pygame
import random
import math


class ComboText:
    """连击文字效果"""
    
    def __init__(self, x, y, combo_count, is_critical=False):
        self.x = x
        self.y = y
        self.combo_count = combo_count
        self.is_critical = is_critical
        
        # 动画参数
        self.life = 1.2  # 存活时间
        self.max_life = 1.2
        self.vy = -80  # 向上漂浮速度
        self.scale = 1.0
        
        # 颜色
        if is_critical:
            self.base_color = (255, 100, 0)  # 橙色
            self.glow_color = (255, 200, 0)  # 金色光晕
        else:
            self.base_color = (255, 220, 100)  # 金色
            self.glow_color = (255, 255, 200)
    
    def update(self, dt):
        """更新状态"""
        self.life -= dt
        self.y += self.vy * dt
        self.vy *= 0.98  # 减速
        
        # 缩放动画
        progress = 1 - self.life / self.max_life
        if progress < 0.2:
            self.scale = 1 + progress * 2  # 放大
        else:
            self.scale = 1.4 - (progress - 0.2) * 0.5  # 慢慢缩小
        
        return self.life > 0
    
    def render(self, surface, font):
        """渲染连击文字"""
        if self.life <= 0:
            return
        
        alpha = min(255, int(255 * (self.life / self.max_life)))
        
        # 连击文字
        text = f"{self.combo_count} COMBO!"
        
        # 根据连击数选择字体大小
        if self.combo_count >= 10:
            size = 32
        elif self.combo_count >= 5:
            size = 26
        else:
            size = 22
        
        combo_font = pygame.font.Font(None, size)
        
        # 渲染文字
        text_surface = combo_font.render(text, True, self.base_color)
        text_surface = pygame.transform.scale(
            text_surface, 
            (int(text_surface.get_width() * self.scale),
             int(text_surface.get_height() * self.scale))
        )
        
        # 添加光晕
        glow_surface = combo_font.render(text, True, self.glow_color)
        glow_surface = pygame.transform.scale(
            glow_surface,
            (int(glow_surface.get_width() * self.scale * 1.2),
             int(glow_surface.get_height() * self.scale * 1.2))
        )
        
        # 设置透明度
        glow_surface.set_alpha(int(alpha * 0.5))
        text_surface.set_alpha(alpha)
        
        # 居中
        rect = text_surface.get_rect(center=(self.x, self.y))
        glow_rect = glow_surface.get_rect(center=(self.x, self.y))
        
        surface.blit(glow_surface, glow_rect)
        surface.blit(text_surface, rect)


class ComboSystem:
    """连击系统管理器"""
    
    def __init__(self):
        self.combos = []  # 活跃的连击文字
        self.combo_count = 0  # 当前连击数
        self.last_kill_time = 0  # 上次击杀时间
        self.combo_timeout = 2.0  # 连击超时时间(秒)
        
        # 连击奖励
        self.coin_bonus = 0  # 金币奖励
        
    def add_kill(self, x, y, is_critical=False):
        """添加击杀
        
        Args:
            x, y: 击杀位置
            is_critical: 是否暴击
        """
        import time
        current_time = time.time()
        
        # 检查是否在连击时间内
        if current_time - self.last_kill_time > self.combo_timeout:
            self.combo_count = 1
        else:
            self.combo_count += 1
        
        self.last_kill_time = current_time
        
        # 创建连击文字
        if self.combo_count >= 2:  # 至少2连击才显示
            combo_text = ComboText(x, y, self.combo_count, is_critical)
            self.combos.append(combo_text)
            
            # 计算金币奖励
            self.coin_bonus = self._calculate_bonus()
    
    def _calculate_bonus(self):
        """计算连击金币奖励"""
        if self.combo_count < 3:
            return 0
        elif self.combo_count < 5:
            return 5
        elif self.combo_count < 10:
            return 10 + (self.combo_count - 5) * 3
        else:
            return 25 + (self.combo_count - 10) * 5
    
    def get_bonus(self):
        """获取并清除金币奖励"""
        bonus = self.coin_bonus
        self.coin_bonus = 0
        return bonus
    
    def update(self, dt):
        """更新连击系统"""
        import time
        current_time = time.time()
        
        # 检查连击是否过期
        if current_time - self.last_kill_time > self.combo_timeout:
            if self.combo_count > 0:
                pass  # 连击结束，可添加特效
            self.combo_count = 0
        
        # 更新所有连击文字
        self.combos = [c for c in self.combos if c.update(dt)]
    
    def render(self, surface):
        """渲染所有连击文字"""
        # 使用默认字体
        font = pygame.font.Font(None, 36)
        for combo in self.combos:
            combo.render(surface, font)
    
    def get_combo_count(self):
        """获取当前连击数"""
        return self.combo_count
    
    def reset(self):
        """重置连击"""
        self.combo_count = 0
        self.combos.clear()
        self.coin_bonus = 0


# 全局实例
_combo_system = None

def get_combo_system():
    """获取连击系统单例"""
    global _combo_system
    if _combo_system is None:
        _combo_system = ComboSystem()
    return _combo_system