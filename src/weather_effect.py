"""
Weather Effect System - 天气粒子特效系统
工艺品级别动态天气效果,增强游戏氛围
"""

import pygame
import random
import math
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class WeatherParticle:
    """单个天气粒子"""
    x: float
    y: float
    vx: float
    vy: float
    size: float
    alpha: int
    lifetime: float
    max_lifetime: float
    particle_type: str  # 'rain', 'snow', 'leaf', 'sakura'


class WeatherEffect:
    """天气效果管理器"""
    
    # 天气类型枚举
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    SAKURA = "sakura"
    AUTUMN = "autumn"
    
    def __init__(self):
        self.particles: List[WeatherParticle] = []
        self.weather_type = self.CLEAR
        self.intensity = 0  # 0-1, 天气强度
        self.wind_x = 0  # 横向风力
        self.screen_width = 800
        self.screen_height = 600
        self._initialized = False
        self.particle_pool: List[WeatherParticle] = []
        self.max_particles = 200
        
    def initialize(self, width: int, height: int):
        """初始化天气系统"""
        self.screen_width = width
        self.screen_height = height
        self._initialized = True
        
    def set_weather(self, weather_type: str, intensity: float = 0.5):
        """设置天气类型和强度"""
        if weather_type not in [self.CLEAR, self.RAIN, self.SNOW, self.SAKURA, self.AUTUMN]:
            weather_type = self.CLEAR
        self.weather_type = weather_type
        self.intensity = min(1.0, max(0.0, intensity))
        
        # 设置不同天气的风力
        if weather_type == self.RAIN:
            self.wind_x = random.uniform(-2, 1)
        elif weather_type == self.SNOW:
            self.wind_x = random.uniform(-1, 1)
        elif weather_type == self.SAKURA:
            self.wind_x = random.uniform(0.5, 2)
        elif weather_type == self.AUTUMN:
            self.wind_x = random.uniform(1, 3)
        else:
            self.wind_x = 0
            
    def spawn_particle(self) -> Optional[WeatherParticle]:
        """生成单个粒子(从对象池)"""
        if len(self.particles) >= self.max_particles:
            return None
            
        # 从池中获取或创建新粒子
        if self.particle_pool:
            particle = self.particle_pool.pop()
        else:
            # 池为空则创建新粒子
            particle = WeatherParticle(
                x=0, y=0, vx=0, vy=0,
                size=0, alpha=255,
                lifetime=0, max_lifetime=1,
                particle_type='rain'
            )
            
        # 根据天气类型初始化粒子属性
        if self.weather_type == self.RAIN:
            particle.x = random.uniform(-50, self.screen_width + 50)
            particle.y = random.uniform(-100, -10)
            particle.vx = self.wind_x + random.uniform(-0.5, 0.5)
            particle.vy = random.uniform(8, 15)
            particle.size = random.uniform(1, 3)
            particle.alpha = random.randint(150, 220)
            particle.lifetime = 0
            particle.max_lifetime = random.uniform(3, 5)
            particle.particle_type = 'rain'
            
        elif self.weather_type == self.SNOW:
            particle.x = random.uniform(-50, self.screen_width + 50)
            particle.y = random.uniform(-50, -10)
            particle.vx = self.wind_x + random.uniform(-1, 1)
            particle.vy = random.uniform(1, 3)
            particle.size = random.uniform(2, 5)
            particle.alpha = random.randint(180, 255)
            particle.lifetime = 0
            particle.max_lifetime = random.uniform(5, 10)
            particle.particle_type = 'snow'
            
        elif self.weather_type == self.SAKURA:
            particle.x = random.uniform(-30, self.screen_width + 30)
            particle.y = random.uniform(-30, -10)
            particle.vx = self.wind_x + random.uniform(-0.5, 1)
            particle.vy = random.uniform(1, 2.5)
            particle.size = random.uniform(4, 8)
            particle.alpha = random.randint(180, 240)
            particle.lifetime = 0
            particle.max_lifetime = random.uniform(6, 12)
            particle.particle_type = 'sakura'
            
        elif self.weather_type == self.AUTUMN:
            particle.x = random.uniform(-30, self.screen_width + 30)
            particle.y = random.uniform(-30, -10)
            particle.vx = self.wind_x + random.uniform(0, 1)
            particle.vy = random.uniform(1.5, 3)
            particle.size = random.uniform(3, 6)
            particle.alpha = random.randint(160, 220)
            particle.lifetime = 0
            particle.max_lifetime = random.uniform(5, 10)
            particle.particle_type = 'leaf'
            
        self.particles.append(particle)
        return particle
        
    def update(self, dt: float):
        """更新天气粒子"""
        if not self._initialized or self.weather_type == self.CLEAR:
            # 清理现有粒子
            for p in self.particles:
                self.particle_pool.append(p)
            self.particles.clear()
            return
            
        # 生成新粒子
        spawn_rate = int(self.intensity * 10 * dt)
        for _ in range(spawn_rate):
            self.spawn_particle()
            
        # 更新现有粒子
        to_remove = []
        for particle in self.particles:
            particle.lifetime += dt
            
            if particle.lifetime > particle.max_lifetime:
                to_remove.append(particle)
                continue
                
            # 更新位置
            particle.x += particle.vx * dt * 60
            particle.y += particle.vy * dt * 60
            
            # 添加飘动效果
            if particle.particle_type in ['snow', 'sakura', 'leaf']:
                particle.x += math.sin(particle.lifetime * 2 + particle.y * 0.01) * 0.5
                
            # 渐变消失
            life_ratio = particle.lifetime / particle.max_lifetime
            if life_ratio > 0.7:
                particle.alpha = int(particle.alpha * (1 - (life_ratio - 0.7) / 0.3))
                
            # 边界检查
            if (particle.y > self.screen_height + 50 or 
                particle.x < -100 or particle.x > self.screen_width + 100):
                to_remove.append(particle)
                
        # 回收粒子到对象池
        for particle in to_remove:
            self.particles.remove(particle)
            self.particle_pool.append(particle)
            
    def draw(self, screen: pygame.Surface):
        """绘制天气粒子"""
        if not self._initialized or self.weather_type == self.CLEAR or not self.particles:
            return
            
        for particle in self.particles:
            if particle.alpha <= 0:
                continue
                
            pos = (int(particle.x), int(particle.y))
            
            if particle.particle_type == 'rain':
                # 雨滴 - 细长线条
                end_pos = (int(particle.x - particle.vx * 2), 
                          int(particle.y - particle.vy * 3))
                pygame.draw.line(screen, (180, 200, 220, particle.alpha), 
                               pos, end_pos, max(1, int(particle.size)))
                               
            elif particle.particle_type == 'snow':
                # 雪花 - 圆形
                snow_color = (240, 248, 255, particle.alpha)
                pygame.draw.circle(screen, snow_color, pos, int(particle.size))
                
            elif particle.particle_type == 'sakura':
                # 樱花花瓣 - 带旋转的椭圆模拟
                sakura_color = (255, 183, 197, particle.alpha)
                size = int(particle.size)
                rect = pygame.Rect(pos[0] - size, pos[1] - size, size * 2, size * 2)
                pygame.draw.ellipse(screen, sakura_color, rect)
                
            elif particle.particle_type == 'leaf':
                # 秋叶 - 多彩
                leaf_colors = [
                    (210, 105, 30, particle.alpha),   # 巧克力色
                    (255, 140, 0, particle.alpha),    # 深橙色
                    (220, 20, 60, particle.alpha),    # 猩红色
                    (218, 165, 32, particle.alpha),   # 金麒麟色
                ]
                leaf_color = random.choice(leaf_colors)
                size = int(particle.size)
                rect = pygame.Rect(pos[0] - size//2, pos[1] - size//2, size, size)
                pygame.draw.ellipse(screen, leaf_color, rect)
                
    def get_weather_info(self) -> dict:
        """获取当前天气信息"""
        return {
            'type': self.weather_type,
            'intensity': self.intensity,
            'wind_x': self.wind_x,
            'particle_count': len(self.particles)
        }
        
    def transition_weather(self, new_weather: str, new_intensity: float, duration: float = 2.0):
        """平滑过渡到新天气"""
        # 淡出当前粒子
        fade_steps = 10
        for _ in range(fade_steps):
            self.intensity *= 0.8
            self.update(duration / fade_steps)
            
        # 切换天气
        self.set_weather(new_weather, 0)
        
        # 淡入新天气
        for i in range(fade_steps):
            self.intensity = new_intensity * (i + 1) / fade_steps
            self.update(duration / fade_steps)


# 全局单例
_weather_instance: Optional[WeatherEffect] = None

def get_weather_effect() -> WeatherEffect:
    """获取天气效果单例"""
    global _weather_instance
    if _weather_instance is None:
        _weather_instance = WeatherEffect()
    return _weather_instance


def init_weather(width: int = 800, height: int = 600):
    """便捷初始化函数"""
    weather = get_weather_effect()
    weather.initialize(width, height)
    return weather