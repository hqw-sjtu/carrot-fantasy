"""
Weather Effect Tests - 天气特效测试套件
"""

import pytest
import pygame
import sys
import os

# 初始化pygame用于测试
pygame.init()
pygame.display.set_mode((800, 600))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from weather_effect import WeatherEffect, get_weather_effect, init_weather


class TestWeatherEffect:
    """天气效果测试"""
    
    def test_weather_init(self):
        """测试天气系统初始化"""
        weather = WeatherEffect()
        assert weather.weather_type == WeatherEffect.CLEAR
        assert weather.intensity == 0
        assert weather.screen_width == 800
        assert weather.screen_height == 600
        
    def test_initialize(self):
        """测试尺寸设置"""
        weather = WeatherEffect()
        weather.initialize(1024, 768)
        assert weather.screen_width == 1024
        assert weather.screen_height == 768
        assert weather._initialized == True
        
    def test_set_weather(self):
        """测试设置天气类型"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        
        weather.set_weather(WeatherEffect.RAIN, 0.8)
        assert weather.weather_type == WeatherEffect.RAIN
        assert weather.intensity == 0.8
        assert weather.wind_x != 0  # 雨
        
        weather.set_weather(WeatherEffect.SNOW, 0.5)
        assert weather.weather_type == WeatherEffect.SNOW
        
    def test_invalid_weather_type(self):
        """测试无效天气类型"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        
        weather.set_weather("invalid_weather", 0.5)
        assert weather.weather_type == WeatherEffect.CLEAR
        
    def test_weather_constants(self):
        """测试天气类型常量"""
        assert WeatherEffect.CLEAR == "clear"
        assert WeatherEffect.RAIN == "rain"
        assert WeatherEffect.SNOW == "snow"
        assert WeatherEffect.SAKURA == "sakura"
        assert WeatherEffect.AUTUMN == "autumn"
        
    def test_get_weather_info(self):
        """测试获取天气信息"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        weather.set_weather(WeatherEffect.RAIN, 0.7)
        
        info = weather.get_weather_info()
        assert info['type'] == WeatherEffect.RAIN
        assert info['intensity'] == 0.7
        assert 'wind_x' in info
        assert 'particle_count' in info
        
    def test_update_no_weather(self):
        """测试无天气时更新"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        
        weather.update(0.016)  # 约60fps一帧
        assert len(weather.particles) == 0
        
    def test_rain_spawn(self):
        """测试雨天粒子生成"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        weather.set_weather(WeatherEffect.RAIN, 1.0)
        
        # 手动触发生成
        for _ in range(10):
            weather.spawn_particle()
            
        assert len(weather.particles) > 0
        
    def test_snow_spawn(self):
        """测试雪天粒子生成"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        weather.set_weather(WeatherEffect.SNOW, 0.8)
        
        for _ in range(10):
            weather.spawn_particle()
            
        assert len(weather.particles) > 0
        
    def test_sakura_spawn(self):
        """测试樱花天气粒子生成"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        weather.set_weather(WeatherEffect.SAKURA, 0.6)
        
        for _ in range(10):
            weather.spawn_particle()
            
        assert len(weather.particles) > 0
        
    def test_particle_lifecycle(self):
        """测试粒子生命周期"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        weather.set_weather(WeatherEffect.SNOW, 1.0)
        weather.max_particles = 50
        
        # 生成粒子
        for _ in range(30):
            weather.spawn_particle()
            
        # 模拟长时间更新让粒子消失
        for _ in range(100):
            weather.update(1.0)  # 大幅推进时间
            
        # 粒子应该消失或被回收
        assert len(weather.particle_pool) > 0 or len(weather.particles) == 0
        
    def test_intensity_bounds(self):
        """测试强度边界"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        
        weather.set_weather(WeatherEffect.RAIN, 1.5)
        assert weather.intensity == 1.0
        
        weather.set_weather(WeatherEffect.RAIN, -0.5)
        assert weather.intensity == 0.0


class TestWeatherSingleton:
    """天气单例测试"""
    
    def test_get_weather_effect(self):
        """测试获取单例"""
        weather1 = get_weather_effect()
        weather2 = get_weather_effect()
        assert weather1 is weather2
        
    def test_init_weather(self):
        """测试便捷初始化"""
        weather = init_weather(1024, 768)
        assert weather.screen_width == 1024
        assert weather.screen_height == 768


class TestWeatherDraw:
    """天气绘制测试"""
    
    def test_draw_no_crash(self):
        """测试绘制不崩溃"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        weather.set_weather(WeatherEffect.RAIN, 0.5)
        
        # 生成一些粒子
        for _ in range(5):
            weather.spawn_particle()
            
        screen = pygame.display.get_surface()
        if screen:
            weather.draw(screen)  # 不应崩溃
            
    def test_draw_clear_weather(self):
        """测试晴天不绘制"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        weather.set_weather(WeatherEffect.CLEAR, 0.5)
        
        screen = pygame.display.get_surface()
        if screen:
            weather.draw(screen)  # 晴天不绘制


class TestWeatherTransition:
    """天气过渡测试"""
    
    def test_transition_weather(self):
        """测试天气过渡"""
        weather = WeatherEffect()
        weather.initialize(800, 600)
        
        weather.set_weather(WeatherEffect.RAIN, 1.0)
        for _ in range(10):
            weather.spawn_particle()
            
        # 过渡到晴天
        weather.transition_weather(WeatherEffect.CLEAR, 0, 0.1)
        
        # 粒子应该被清理
        assert weather.weather_type == WeatherEffect.CLEAR


if __name__ == '__main__':
    pytest.main([__file__, '-v'])