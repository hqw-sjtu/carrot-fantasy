"""测试天气和昼夜特效"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

SCREEN = None
try:
    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
    SCREEN = pygame.Surface((800, 600))
except Exception:
    pass  # 无显示环境时使用虚拟Surface

from extra_effects import DayNightCycleEffect, WeatherEffect, EffectManager


class TestDayNightCycleEffect:
    """测试昼夜循环特效"""
    
    def test_day_night_init(self):
        """测试昼夜循环初始化"""
        effect = DayNightCycleEffect(800, 600, cycle_duration=60.0)
        assert effect.cycle_duration == 60.0
        assert effect.current_phase == "day"
        assert effect.active == True
        
    def test_day_night_update(self):
        """测试昼夜循环更新"""
        effect = DayNightCycleEffect(800, 600, cycle_duration=60.0)
        effect.update(15.0)  # 15秒 = 1/4周期
        assert effect.current_phase in ["dawn", "day", "dusk", "night"]
        
    def test_day_night_get_colors(self):
        """测试获取天空颜色"""
        effect = DayNightCycleEffect(800, 600, cycle_duration=60.0)
        colors = effect.get_sky_colors()
        assert len(colors) == 3
        
    @pytest.mark.skipif(SCREEN is None, reason="Pygame not initialized")
    def test_day_night_draw(self):
        """测试昼夜循环绘制"""
        effect = DayNightCycleEffect(800, 600, cycle_duration=60.0)
        effect.update(0.1)
        effect.draw(SCREEN)


class TestWeatherEffect:
    """测试天气特效"""
    
    def test_weather_rain_init(self):
        """测试雨天初始化"""
        effect = WeatherEffect(800, 600, weather_type="rain")
        assert effect.weather_type == "rain"
        assert len(effect.particles) == 200
        assert effect.active == True
        
    def test_weather_snow_init(self):
        """测试雪天初始化"""
        effect = WeatherEffect(800, 600, weather_type="snow")
        assert effect.weather_type == "snow"
        assert len(effect.particles) == 150
        
    def test_weather_update(self):
        """测试天气更新"""
        effect = WeatherEffect(800, 600, weather_type="rain")
        effect.update(0.1)
        assert effect.life == 0.1
        
    def test_weather_expire(self):
        """测试天气过期"""
        effect = WeatherEffect(800, 600, weather_type="rain")
        effect.update(10.5)  # 超过max_life
        assert effect.active == False
        
    @pytest.mark.skipif(SCREEN is None, reason="Pygame not initialized")
    def test_weather_draw(self):
        """测试天气绘制"""
        effect = WeatherEffect(800, 600, weather_type="rain")
        effect.update(0.1)
        effect.draw(SCREEN)
        

class TestEffectManagerWeather:
    """测试特效管理器的天气功能"""
    
    def test_spawn_day_night_cycle(self):
        """测试生成昼夜循环"""
        manager = EffectManager()
        effect = manager.spawn_day_night_cycle(800, 600, cycle_duration=60.0)
        assert effect is not None
        assert manager.day_night_cycle is effect
        
    def test_spawn_weather_rain(self):
        """测试生成雨天"""
        manager = EffectManager()
        effect = manager.spawn_weather(800, 600, weather_type="rain")
        assert effect is not None
        assert len(manager.weather_effects) == 1
        
    def test_spawn_weather_snow(self):
        """测试生成雪天"""
        manager = EffectManager()
        effect = manager.spawn_weather(800, 600, weather_type="snow")
        assert effect is not None
        assert len(manager.weather_effects) == 1
        
    def test_weather_update_in_manager(self):
        """测试管理器更新天气"""
        manager = EffectManager()
        manager.spawn_weather(800, 600, weather_type="rain")
        manager.update(0.1)
        # 天气应该自动清理过期的
        assert len(manager.weather_effects) == 1