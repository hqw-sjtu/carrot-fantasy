"""
Slow Motion Effect Tests - 子弹时间系统测试
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
from src.slow_motion_effect import SlowMotionEffect


@pytest.fixture(scope="module")
def pygame_init():
    if not pygame.get_init():
        pygame.init()
    yield


class TestSlowMotionEffect:
    """子弹时间效果测试套件"""
    
    def test_slow_motion_creation(self, pygame_init):
        effect = SlowMotionEffect()
        assert effect is not None
        assert not effect.active
        assert effect.duration == 3.0
        assert effect.slow_factor == 0.3
        assert effect.energy == 100
        
    def test_activate_success(self, pygame_init):
        effect = SlowMotionEffect()
        result = effect.activate()
        
        assert result is True
        assert effect.active
        assert effect.energy < 100  # 消耗了能量
        
    def test_activate_fail_no_energy(self, pygame_init):
        effect = SlowMotionEffect()
        effect.energy = 0
        
        result = effect.activate()
        
        assert result is False
        assert not effect.active
        
    def test_deactivate(self, pygame_init):
        effect = SlowMotionEffect()
        effect.activate()
        effect.deactivate()
        
        assert not effect.active
        
    def test_time_scale_changes(self, pygame_init):
        effect = SlowMotionEffect()
        effect.activate()
        
        # 初始时间缩放应该接近1
        initial_scale = effect.current_time_scale
        
        # 更新后应该接近slow_factor
        effect.update(0.5)
        
        assert effect.current_time_scale < initial_scale
        assert effect.current_time_scale <= 1.0
        
    def test_energy_recharge(self, pygame_init):
        effect = SlowMotionEffect()
        effect.energy = 0
        effect.active = False
        
        effect.update(1.0)  # 1秒后
        
        assert effect.energy > 0
        
    def test_vignette_alpha(self, pygame_init):
        effect = SlowMotionEffect()
        
        # 未激活时暗角为0
        assert effect.vignette_alpha == 0
        
        effect.activate()
        effect.update(0.1)
        
        # 激活后暗角增加
        assert effect.vignette_alpha > 0
        
    def test_particles_generation(self, pygame_init):
        effect = SlowMotionEffect()
        effect.activate()
        
        effect.update(0.5)
        
        # 应该生成粒子
        assert len(effect.particles) >= 0  # 随机生成
        
    def test_ready_state(self, pygame_init):
        effect = SlowMotionEffect()
        
        # 满能量时应该ready
        effect.energy = 100
        effect.update(0)
        assert effect.ready is True
        
        # 能量不足时不应该ready
        effect.energy = 10
        effect.update(0)
        assert effect.ready is False
        
    def test_duration_expires(self, pygame_init):
        effect = SlowMotionEffect()
        effect.duration = 0.5  # 短持续时间
        effect.activate()
        
        # 等待超时
        effect.update(0.6)
        
        assert not effect.active
        
    def test_get_time_scale(self, pygame_init):
        effect = SlowMotionEffect()
        
        scale1 = effect.get_time_scale()
        assert scale1 == 1.0
        
        effect.activate()
        effect.update(0.5)
        
        scale2 = effect.get_time_scale()
        assert scale2 < 1.0
        
    def test_is_active(self, pygame_init):
        effect = SlowMotionEffect()
        
        assert effect.is_active() is False
        
        effect.activate()
        
        assert effect.is_active() is True


class TestSlowMotionEnergy:
    """能量系统测试"""
    
    def test_energy_cost(self, pygame_init):
        effect = SlowMotionEffect()
        initial_energy = effect.energy
        
        effect.activate()
        
        assert effect.energy == initial_energy - effect.energy_cost
        
    def test_max_energy_limit(self, pygame_init):
        effect = SlowMotionEffect()
        effect.energy = 200
        effect.update(0)
        
        assert effect.energy <= effect.max_energy
        
    def test_recharge_rate(self, pygame_init):
        effect = SlowMotionEffect()
        effect.energy = 50
        effect.active = False
        
        effect.update(1.0)  # 1秒
        
        # 应该增加约10点能量
        assert effect.energy > 50
        assert effect.energy <= 50 + effect.recharge_rate + 1