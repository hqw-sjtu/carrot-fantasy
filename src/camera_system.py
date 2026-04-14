"""
保卫萝卜 - 屏幕震动系统
统一管理所有屏幕震动效果
"""
import pygame
import random
import math

class ScreenShakeManager:
    """屏幕震动管理器"""
    
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.decay = 5.0
        self.offset_x = 0
        self.offset_y = 0
        self.bounded = True
        self.bounds = (800, 600)
        
    def add_shake(self, intensity, duration, decay=None):
        """添加屏幕震动
        
        Args:
            intensity: 震动强度(像素)
            duration: 持续时间(秒)
            decay: 衰减速度(可选)
        """
        # 如果当前震动更强，不覆盖
        if self.intensity > intensity:
            return
            
        self.intensity = intensity
        self.duration = duration
        if decay:
            self.decay = decay
            
    def add_explosion_shake(self, x, y, screen_center, max_intensity=15):
        """添加基于爆炸的屏幕震动
        
        Args:
            x, y: 爆炸位置
            screen_center: 屏幕中心
            max_intensity: 最大强度
        """
        # 计算距离
        dist = math.hypot(x - screen_center[0], y - screen_center[1])
        max_dist = math.hypot(screen_center[0], screen_center[1])
        
        # 距离越近，震动越强
        factor = 1 - min(1, dist / max_dist)
        intensity = max_intensity * factor
        
        if intensity > 0:
            self.add_shake(intensity, 0.5, 10)
            
    def add_critical_shake(self):
        """暴击时的轻微震动"""
        self.add_shake(3, 0.15, 20)
        
    def add_boss_shake(self):
        """Boss攻击时的强烈震动"""
        self.add_shake(10, 0.4, 8)
        
    def add_earthquake_shake(self):
        """地震效果的持续震动"""
        self.add_shake(20, 2.0, 3)
        
    def update(self, dt):
        """更新震动状态"""
        if self.duration > 0:
            self.duration -= dt
            
            # 计算当前强度
            if self.duration <= 0:
                self.intensity = 0
            else:
                # 线性衰减
                progress = 1 - (self.duration * self.decay / self.intensity) if self.intensity > 0 else 0
                self.intensity = max(0, self.intensity * (1 - dt * self.decay / 10))
                
        # 计算偏移
        if self.intensity > 0:
            self.offset_x = random.uniform(-self.intensity, self.intensity)
            self.offset_y = random.uniform(-self.intensity, self.intensity)
            
            # 边界限制
            if self.bounded:
                self.offset_x = max(-self.bounds[0]//4, min(self.bounds[0]//4, self.offset_x))
                self.offset_y = max(-self.bounds[1]//4, min(self.bounds[1]//4, self.offset_y))
        else:
            self.offset_x = 0
            self.offset_y = 0
            
    def apply(self, screen):
        """应用震动到屏幕"""
        if self.offset_x != 0 or self.offset_y != 0:
            return (int(self.offset_x), int(self.offset_y))
        return (0, 0)
        
    def reset(self):
        """重置震动"""
        self.intensity = 0
        self.duration = 0
        self.offset_x = 0
        self.offset_y = 0
        
    def get_intensity_factor(self):
        """获取当前强度因子(0-1)"""
        return min(1, self.intensity / 20)


# 全局单例
_screen_shake_manager = None

def get_screen_shake_manager():
    """获取屏幕震动管理器单例"""
    global _screen_shake_manager
    if _screen_shake_manager is None:
        _screen_shake_manager = ScreenShakeManager()
    return _screen_shake_manager


class Camera:
    """游戏相机 - 支持缩放和移动"""
    
    def __init__(self, width=800, height=600):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        self.smoothness = 5.0
        
    def set_position(self, x, y):
        """设置相机位置"""
        self.x = x
        self.y = y
        
    def move(self, dx, dy):
        """移动相机"""
        self.x += dx
        self.y += dy
        
    def set_zoom(self, zoom):
        """设置缩放"""
        self.target_zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        
    def zoom_in(self, factor=0.1):
        """放大"""
        self.set_zoom(self.target_zoom + factor)
        
    def zoom_out(self, factor=0.1):
        """缩小"""
        self.set_zoom(self.target_zoom - factor)
        
    def update(self, dt):
        """更新相机"""
        # 平滑缩放
        if abs(self.zoom - self.target_zoom) > 0.01:
            self.zoom += (self.target_zoom - self.zoom) * dt * self.smoothness
            
    def world_to_screen(self, x, y):
        """世界坐标转屏幕坐标"""
        sx = (x - self.x) * self.zoom + self.width / 2
        sy = (y - self.y) * self.zoom + self.height / 2
        return int(sx), int(sy)
        
    def screen_to_world(self, sx, sy):
        """屏幕坐标转世界坐标"""
        x = (sx - self.width / 2) / self.zoom + self.x
        y = (sy - self.height / 2) / self.zoom + self.y
        return x, y
        
    def apply(self, screen):
        """应用相机变换"""
        if self.zoom != 1.0:
            # 缩放中心
            return pygame.transform.scale(screen, 
                (int(self.width * self.zoom), int(self.height * self.zoom)))
        return screen


# 全局相机
_camera = None

def get_camera():
    """获取全局相机"""
    global _camera
    if _camera is None:
        _camera = Camera()
    return _camera