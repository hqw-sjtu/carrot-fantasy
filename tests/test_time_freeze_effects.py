"""
时间膨胀与屏幕冰冻特效测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
except:
    pytest.skip("Pygame not available", allow_module_level=True)

from extra_effects import TimeDilationEffect, ScreenFreezeEffect, EffectManager


class TestTimeDilationEffect:
    """时间膨胀特效测试"""
    
    def test_time_dilation_init(self):
        """测试时间膨胀特效初始化"""
        effect = TimeDilationEffect(400, 300, radius=150)
        assert effect.x == 400
        assert effect.y == 300
        assert effect.radius == 150
        assert effect.active == True
        assert effect.max_life == 2.0
        
    def test_time_dilation_update(self):
        """测试时间膨胀特效更新"""
        effect = TimeDilationEffect(400, 300)
        initial_life = effect.life
        effect.update(0.1)
        assert effect.life > initial_life
        
    def test_time_dilation_deactivate(self):
        """测试时间膨胀特效过期"""
        effect = TimeDilationEffect(400, 300, radius=50)
        effect.update(3.0)  # 超过max_life
        assert effect.active == False


class TestScreenFreezeEffect:
    """屏幕冰冻特效测试"""
    
    def test_screen_freeze_init(self):
        """测试屏幕冰冻特效初始化"""
        effect = ScreenFreezeEffect(800, 600)
        assert effect.width == 800
        assert effect.height == 600
        assert effect.active == True
        assert effect.max_life == 0.5
        
    def test_screen_freeze_update(self):
        """测试屏幕冰冻特效更新"""
        effect = ScreenFreezeEffect(800, 600)
        effect.update(0.1)
        assert effect.life == 0.1
        
    def test_screen_freeze_deactivate(self):
        """测试屏幕冰冻特效过期"""
        effect = ScreenFreezeEffect(800, 600)
        effect.update(1.0)  # 超过max_life
        assert effect.active == False


class TestEffectManagerIntegration:
    """EffectManager集成测试"""
    
    def test_spawn_time_dilation(self):
        """测试生成时间膨胀特效"""
        manager = EffectManager.get_instance()
        effect = manager.spawn_time_dilation(400, 300, radius=150)
        assert effect in manager.time_dilations
        assert isinstance(effect, TimeDilationEffect)
        
    def test_spawn_screen_freeze(self):
        """测试生成屏幕冰冻特效"""
        manager = EffectManager.get_instance()
        effect = manager.spawn_screen_freeze(800, 600)
        assert effect in manager.screen_freezes
        assert isinstance(effect, ScreenFreezeEffect)
        
    def test_update_time_freeze_effects(self):
        """测试更新时间膨胀和屏幕冰冻特效"""
        manager = EffectManager.get_instance()
        manager.time_dilations.clear()
        manager.screen_freezes.clear()
        
        manager.spawn_time_dilation(400, 300)
        manager.spawn_screen_freeze(800, 600)
        
        initial_count_time = len(manager.time_dilations)
        initial_count_freeze = len(manager.screen_freezes)
        
        # 正常更新不应删除
        manager.update(0.1)
        
        assert len(manager.time_dilations) == initial_count_time
        assert len(manager.screen_freezes) == initial_count_freeze