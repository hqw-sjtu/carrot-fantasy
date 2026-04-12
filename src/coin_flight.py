"""
保卫萝卜 - 金币飞行系统
Carrot Fantasy - Coin Flight Effect
怪物死亡后金币飞向UI的金币显示区域
"""
import pygame
import math
import random


class FlyingCoin:
    """飞行金币"""
    
    def __init__(self, start_x, start_y, target_x, target_y, value=1):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.value = value
        
        # 动画参数
        self.progress = 0  # 0-1
        self.speed = 2.5  # 飞行速度
        self.arc_height = 60  # 弧线高度
        self.rotation = 0  # 旋转角度
        self.rotation_speed = random.randint(300, 500)  # 旋转速度
        
        # 视觉效果
        self.scale = 1.0
        self.alpha = 255
        
        # 起始位置随机偏移
        self.offset_x = random.randint(-10, 10)
        self.offset_y = random.randint(-10, 10)
    
    def update(self, dt):
        """更新状态"""
        self.progress += self.speed * dt
        
        # 计算位置（抛物线弧）
        t = min(self.progress, 1.0)
        
        # 线性插值
        linear_x = self.x + (self.target_x - self.x) * t
        linear_y = self.y + (self.target_y - self.y) * t
        
        # 添加弧线
        arc = math.sin(t * math.pi) * self.arc_height
        self.y = linear_y - arc
        self.x = linear_x + self.offset_x * (1 - t)
        
        # 旋转
        self.rotation += self.rotation_speed * dt
        
        # 缩放效果
        if t < 0.1:
            self.scale = t / 0.1 * 1.0
        elif t > 0.8:
            self.scale = (1 - t) / 0.2 * 1.0
        else:
            self.scale = 1.0
        
        # 透明度
        if t > 0.9:
            self.alpha = int(255 * (1 - t) / 0.1)
        
        return self.progress < 1.0
    
    def render(self, surface):
        """渲染飞行金币"""
        if self.progress >= 1.0:
            return
        
        # 绘制金币
        size = int(20 * self.scale)
        
        # 创建金币表面
        coin_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 金币主体
        color = (255, 200, 0)
        pygame.draw.circle(coin_surface, color, (size//2, size//2), size//2)
        pygame.draw.circle(coin_surface, (255, 150, 0), (size//2, size//2), size//2, 2)
        
        # 金币符号
        symbol_font = pygame.font.Font(None, int(size * 0.7))
        text = symbol_font.render("$", True, (255, 255, 200))
        text_rect = text.get_rect(center=(size//2, size//2))
        coin_surface.blit(text, text_rect)
        
        # 旋转
        if self.rotation % 360 > 90 and self.rotation % 360 < 270:
            coin_surface = pygame.transform.flip(coin_surface, True, False)
        
        # 设置透明度
        coin_surface.set_alpha(self.alpha)
        
        # 绘制
        rect = coin_surface.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(coin_surface, rect)


class CoinFlightSystem:
    """金币飞行系统管理器"""
    
    def __init__(self):
        self.coins = []  # 飞行中的金币
        self.target_pos = (70, 30)  # 默认目标位置（金币UI）
        
    def set_target(self, x, y):
        """设置目标位置"""
        self.target_pos = (x, y)
    
    def spawn_coin(self, x, y, value=1):
        """生成飞行金币
        
        Args:
            x, y: 起始位置
            value: 金币价值
        """
        coin = FlyingCoin(x, y, self.target_pos[0], self.target_pos[1], value)
        self.coins.append(coin)
    
    def spawn_coins(self, x, y, count, value=1):
        """生成多个飞行金币
        
        Args:
            x, y: 起始位置
            count: 金币数量
            value: 每个金币的价值
        """
        # 分散生成
        for i in range(count):
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            delay = i * 0.05  # 略微延迟
            
            # 延迟添加到列表
            coin = FlyingCoin(
                x + offset_x, 
                y + offset_y, 
                self.target_pos[0], 
                self.target_pos[1], 
                value
            )
            self.coins.append(coin)
    
    def update(self, dt):
        """更新所有金币"""
        self.coins = [c for c in self.coins if c.update(dt)]
    
    def render(self, surface):
        """渲染所有金币"""
        for coin in self.coins:
            coin.render(surface)
    
    def is_active(self):
        """是否有活跃金币"""
        return len(self.coins) > 0
    
    def clear(self):
        """清除所有金币"""
        self.coins.clear()


# 全局实例
_coin_flight = None

def get_coin_flight():
    """获取金币飞行系统单例"""
    global _coin_flight
    if _coin_flight is None:
        _coin_flight = CoinFlightSystem()
    return _coin_flight