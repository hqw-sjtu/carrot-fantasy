"""
屏幕震动效果 - Screen Shake Effect
为游戏添加打击感
"""
import pygame
import random
import math


class ScreenShake:
    """屏幕震动管理器"""
    
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.start_time = 0
        self.decay = 0.9
        self.current_offset = (0, 0)
        self.enabled = True
        
    def trigger(self, intensity: float, duration: float = 0.15):
        """触发屏幕震动
        
        Args:
            intensity: 震动强度 (0-1)
            duration: 持续时间(秒)
        """
        if not self.enabled:
            return
        self.intensity = intensity
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        
    def update(self) -> tuple:
        """更新震动效果
        
        Returns:
            (x, y) 偏移量
        """
        if self.intensity <= 0:
            return (0, 0)
            
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        
        if elapsed >= self.duration:
            self.intensity = 0
            self.current_offset = (0, 0)
            return (0, 0)
            
        # 衰减曲线
        progress = elapsed / self.duration
        decay = 1 - progress ** 2
        current_intensity = self.intensity * decay * 10
        
        # 随机偏移
        angle = random.uniform(0, math.pi * 2)
        magnitude = random.uniform(0.5, 1.0) * current_intensity
        
        x = int(math.cos(angle) * magnitude * 20)
        y = int(math.sin(angle) * magnitude * 20)
        
        self.current_offset = (x, y)
        return (x, y)
        
    def reset(self):
        """重置震动"""
        self.intensity = 0
        self.current_offset = (0, 0)


# 全局实例
_screen_shake = None

def get_screen_shake() -> ScreenShake:
    """获取全局屏幕震动实例"""
    global _screen_shake
    if _screen_shake is None:
        _screen_shake = ScreenShake()
    return _screen_shake


def trigger_screen_shake(intensity: float, duration: float = 0.15):
    """快捷函数: 触发屏幕震动"""
    get_screen_shake().trigger(intensity, duration)


# 预设震动效果
class ShakePresets:
    """预设震动参数"""
    LIGHT = (0.2, 0.1)      # 轻微震动
    MEDIUM = (0.5, 0.2)     # 中等震动
    HEAVY = (0.8, 0.3)      # 强烈震动
    CRITICAL = (1.0, 0.4)   # 暴击震动
    BOSS_HIT = (0.7, 0.25)  # Boss受击
    WAVE_START = (0.3, 0.15) # 波次开始