"""
保卫萝卜 - 屏幕震动系统
Carrot Fantasy - Screen Shake System
"""
import pygame
import random
import math


class ScreenShake:
    """屏幕震动管理器"""
    
    def __init__(self):
        self.intensity = 0  # 震动强度
        self.duration = 0   # 持续时间
        self.elapsed = 0    # 已过时间
        self.frequency = 30 # 震动频率
        self.decay = 0.9    # 衰减系数
        self.offset_x = 0   # X偏移
        self.offset_y = 0   # Y偏移
        self.enabled = True
        
    def trigger(self, intensity, duration):
        """触发屏幕震动
        
        Args:
            intensity: 震动强度 (像素)
            duration: 持续时间 (秒)
        """
        if not self.enabled:
            return
        self.intensity = intensity
        self.duration = duration
        self.elapsed = 0
        
    def update(self, dt):
        """更新震动状态"""
        if self.duration <= 0:
            self.offset_x = 0
            self.offset_y = 0
            return False
            
        self.elapsed += dt
        
        # 计算当前强度（线性衰减）
        progress = self.elapsed / self.duration
        current_intensity = self.intensity * (1 - progress) * self.decay
        
        # 生成随机偏移
        self.offset_x = random.uniform(-current_intensity, current_intensity)
        self.offset_y = random.uniform(-current_intensity, current_intensity)
        
        # 震动结束
        if self.elapsed >= self.duration:
            self.duration = 0
            self.offset_x = 0
            self.offset_y = 0
            return False
            
        return True
    
    def get_offset(self):
        """获取当前偏移量"""
        return (int(self.offset_x), int(self.offset_y))
    
    def apply(self, surface):
        """应用震动到表面（绘制前调用）"""
        if self.duration > 0:
            offset = self.get_offset()
            surface.scroll(offset[0], offset[1])
    
    def reset(self):
        """重置震动"""
        self.intensity = 0
        self.duration = 0
        self.elapsed = 0
        self.offset_x = 0
        self.offset_y = 0


class ScreenShakeManager:
    """屏幕震动管理器（兼容旧API）"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ScreenShake()
        return cls._instance
    
    @classmethod
    def trigger(cls, intensity, duration):
        cls.get_instance().trigger(intensity, duration)
    
    @classmethod
    def update(cls, dt):
        return cls.get_instance().update(dt)
    
    @classmethod
    def get_offset(cls):
        return cls.get_instance().get_offset()
    
    @classmethod
    def reset(cls):
        cls.get_instance().reset()


# 预设震动效果
class ShakePresets:
    """预设震动效果"""
    
    @staticmethod
    def light():
        """轻微震动 - 小伤害"""
        ScreenShakeManager.trigger(3, 0.1)
    
    @staticmethod
    def medium():
        """中等震动 - 中等伤害/暴击"""
        ScreenShakeManager.trigger(8, 0.2)
    
    @staticmethod
    def heavy():
        """强烈震动 - 大范围伤害"""
        ScreenShakeManager.trigger(15, 0.3)
    
    @staticmethod
    def extreme():
        """极致震动 - BOSS攻击/大爆炸"""
        ScreenShakeManager.trigger(25, 0.5)
    
    @staticmethod
    def wave_complete():
        """波次完成 - 轻微庆祝"""
        ScreenShakeManager.trigger(5, 0.15)
    
    @staticmethod
    def tower_sell():
        """出售防御塔"""
        ScreenShakeManager.trigger(2, 0.08)
    
    @staticmethod
    def tower_upgrade():
        """升级防御塔"""
        ScreenShakeManager.trigger(4, 0.12)