# -*- coding: utf-8 -*-
"""全局光影系统测试"""
import pytest
import pygame
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ambient_light_system import AmbientLightSystem, init_ambient_light, get_ambient_light


@pytest.fixture(scope='module')
def pygame_init():
    """初始化pygame"""
    pygame.init()
    pygame.display.set_mode((800, 600))
    yield
    pygame.quit()


class TestAmbientLightSystem:
    """测试全局光影系统"""
    
    def test_init(self):
        """测试初始化"""
        screen_width, screen_height = 800, 600
        system = AmbientLightSystem(screen_width, screen_height)
        
        assert system.screen_width == screen_width
        assert system.screen_height == screen_height
        assert system.vignette_enabled is True
        assert system.brightness == 1.0
        assert system.battle_mode is False
    
    def test_preset_normal(self, pygame_init):
        """测试普通预设"""
        system = AmbientLightSystem(800, 600)
        system.set_preset("normal", transition=False)
        
        assert system.current_tint == (255, 255, 255)
        assert system.brightness == 1.0
    
    def test_preset_boss(self, pygame_init):
        """测试Boss预设"""
        system = AmbientLightSystem(800, 600)
        system.set_preset("boss", transition=False)
        
        assert system.current_tint == (255, 100, 100)
        assert system.brightness == 1.1
    
    def test_battle_mode(self, pygame_init):
        """测试战斗模式"""
        system = AmbientLightSystem(800, 600)
        system.start_battle_mode()
        
        assert system.battle_mode is True
        assert system.battle_intensity == 0.0
        
        # 更新几帧
        system.update(0.1)
        assert system.battle_intensity > 0
        
        system.end_battle_mode()
        assert system.battle_mode is False
    
    def test_update_transition(self, pygame_init):
        """测试过渡更新"""
        system = AmbientLightSystem(800, 600)
        system.target_tint = (200, 200, 255)
        system.target_brightness = 1.2
        
        # 初始状态
        assert system.current_tint == (255, 255, 255)
        
        # 更新
        system.update(0.5)
        
        # 应该接近目标值
        assert system.current_tint[0] < 255
        assert system.brightness > 1.0
    
    def test_vignette_surface_created(self, pygame_init):
        """测试暗角表面创建"""
        system = AmbientLightSystem(800, 600)
        
        assert system._vignette_surface is not None
        assert system._vignette_surface.get_size() == (800, 600)
    
    def test_get_light_info(self, pygame_init):
        """测试获取光照信息"""
        system = AmbientLightSystem(800, 600)
        info = system.get_light_info()
        
        assert "tint" in info
        assert "brightness" in info
        assert "vignette_strength" in info
        assert "battle_mode" in info
        assert "battle_intensity" in info
    
    def test_singleton_functions(self, pygame_init):
        """测试单例函数"""
        # 先初始化
        init_ambient_light(800, 600)
        
        # 获取实例
        instance = get_ambient_light()
        assert instance is not None
        assert isinstance(instance, AmbientLightSystem)
    
    def test_multiple_presets(self, pygame_init):
        """测试多个预设"""
        system = AmbientLightSystem(800, 600)
        
        # 夜晚预设
        system.set_preset("night", transition=False)
        assert system.current_tint == (180, 190, 220)
        
        # 日落预设
        system.set_preset("sunset", transition=False)
        assert system.current_tint == (255, 200, 150)
        
        # 胜利预设
        system.set_preset("victory", transition=False)
        assert system.current_tint == (255, 240, 200)
    
    def test_battle_mode_transitions(self, pygame_init):
        """测试战斗模式转换"""
        system = AmbientLightSystem(800, 600)
        
        # 进入战斗
        system.start_battle_mode()
        assert system.battle_mode is True
        
        # 模拟战斗
        for _ in range(10):
            system.update(0.1)
        
        assert system.battle_intensity >= 0.4
        
        # 退出战斗
        system.end_battle_mode()
        assert system.battle_mode is False
        
        # 战斗强度应该降低
        system.update(0.5)
        assert system.battle_intensity < 0.5


class TestVignetteDrawing:
    """测试暗角绘制"""
    
    def test_draw_without_error(self, pygame_init):
        """测试绘制不出错"""
        system = AmbientLightSystem(800, 600)
        
        screen = pygame.display.get_surface()
        system.draw(screen)  # 不应该抛出异常
    
    def test_vignette_toggle(self, pygame_init):
        """测试暗角开关"""
        system = AmbientLightSystem(800, 600)
        
        assert system.vignette_enabled is True
        system.vignette_enabled = False
        assert system.vignette_enabled is False
        system.vignette_enabled = True


class TestTintApplication:
    """测试色调应用"""
    
    def test_apply_tint_no_change(self, pygame_init):
        """测试无变化时"""
        system = AmbientLightSystem(800, 600)
        system.set_preset("normal", transition=False)
        
        test_surf = pygame.Surface((100, 100))
        result = system.apply_tint(test_surf)
        
        assert result is not None
    
    def test_apply_tint_with_brightness(self, pygame_init):
        """测试亮度调整"""
        system = AmbientLightSystem(800, 600)
        system.brightness = 1.5
        system.current_tint = (255, 255, 255)
        
        test_surf = pygame.Surface((50, 50))
        test_surf.fill((128, 128, 128))
        
        result = system.apply_tint(test_surf)
        assert result is not None