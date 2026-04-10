"""保卫萝卜 - 新增特效测试"""
import pytest
import sys
sys.path.insert(0, 'src')
import pygame
pygame.init()

from base_effects import ShieldEffect, PulseWarningEffect, BaseEffectManager


class TestShieldEffect:
    """护盾特效测试"""
    
    def test_shield_effect_init(self):
        """测试护盾特效初始化"""
        effect = ShieldEffect(100, 100, (100, 150, 255), 30)
        assert effect.x == 100
        assert effect.y == 100
        assert effect.color == (100, 150, 255)
        assert effect.max_life == 30
        assert effect.active is True
        
    def test_shield_effect_update(self):
        """测试护盾特效更新"""
        effect = ShieldEffect(100, 100)
        initial_life = effect.life
        effect.update(10)
        assert effect.life == initial_life + 10
        
    def test_shield_effect_deactivate(self):
        """测试护盾特效消失"""
        effect = ShieldEffect(100, 100, duration=20)
        effect.update(25)
        assert effect.active is False
        
    def test_shield_effect_rings(self):
        """测试护盾环结构"""
        effect = ShieldEffect(100, 100)
        assert len(effect.rings) == 3
        assert effect.rings[0]['radius'] == 25
        assert effect.rings[1]['radius'] == 35
        assert effect.rings[2]['radius'] == 45


class TestPulseWarningEffect:
    """脉冲警告特效测试"""
    
    def test_pulse_warning_init(self):
        """测试脉冲警告初始化"""
        effect = PulseWarningEffect(200, 200, 80, (255, 80, 80), 3)
        assert effect.x == 200
        assert effect.y == 200
        assert effect.radius == 80
        assert effect.color == (255, 80, 80)
        assert effect.pulses == 3
        
    def test_pulse_warning_update(self):
        """测试脉冲警告更新"""
        effect = PulseWarningEffect(200, 200, pulses=3)
        effect.update(25)
        assert effect.current_pulse == 1
        
    def test_pulse_warning_deactivate(self):
        """测试脉冲警告结束"""
        effect = PulseWarningEffect(200, 200, pulses=3)
        # max_life = pulses * 20 = 60
        effect.update(65)
        assert effect.active is False


class TestBaseEffectManagerNew:
    """新增特效管理器测试"""
    
    def test_add_shield_effect(self):
        """测试添加护盾特效"""
        manager = BaseEffectManager()
        manager.add_shield_effect(100, 100)
        assert len(manager.effects) == 1
        assert isinstance(manager.effects[0], ShieldEffect)
        
    def test_add_pulse_warning(self):
        """测试添加脉冲警告特效"""
        manager = BaseEffectManager()
        manager.add_pulse_warning(200, 200)
        assert len(manager.effects) == 1
        assert isinstance(manager.effects[0], PulseWarningEffect)
        
    def test_trigger_shield_effect(self):
        """测试触发护盾特效"""
        manager = BaseEffectManager()
        
        class MockTower:
            def __init__(self):
                self.x = 100
                self.y = 100
                self.name = "箭塔"
        
        tower = MockTower()
        manager.trigger_shield_effect(tower)
        assert len(manager.effects) == 1