"""
Power Surge System Tests - 能量爆发系统测试
"""

import pytest
import sys
import os

# 确保可以导入src模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
from src.power_surge import PowerSurge, get_power_surge


@pytest.fixture(scope="module")
def pygame_init():
    """初始化pygame"""
    if not pygame.get_init():
        pygame.init()
    yield
    # 不关闭pygame,因为其他测试可能需要


class TestPowerSurge:
    """能量爆发测试套件"""
    
    def test_surge_creation(self, pygame_init):
        """测试能量爆发创建"""
        surge = PowerSurge()
        assert surge is not None
        assert not surge.active
        assert surge.duration == 5.0
        assert surge.damage_boost == 1.5
        assert not surge.activated
        return True
    
    def test_surge_activation(self, pygame_init):
        """测试激活能量爆发"""
        surge = PowerSurge()
        surge.activate(400, 300, 200)
        
        assert surge.active
        assert surge.elapsed == 0.0
        assert surge.center_x == 400
        assert surge.center_y == 300
        assert surge.radius == 200
        assert surge.activated
        assert len(surge.particles) == surge.max_particles
        return True
    
    def test_surge_update(self, pygame_init):
        """测试更新状态"""
        surge = PowerSurge()
        surge.activate(400, 300, 200)
        
        # 更新1秒
        surge.update(1.0)
        assert surge.elapsed == 1.0
        assert surge.active
        
        # 更新到结束
        surge.update(10.0)
        assert not surge.active
        return True
    
    def test_damage_multiplier(self, pygame_init):
        """测试伤害倍率计算"""
        surge = PowerSurge()
        
        # 未激活时
        assert surge.get_damage_multiplier() == 1.0
        
        # 激活时
        surge.activate(400, 300, 200)
        assert surge.get_damage_multiplier() == 1.5
        
        # 接近结束时淡出(80%时间后开始淡出)
        surge.elapsed = surge.duration * 0.9
        mult = surge.get_damage_multiplier()
        assert 0.75 <= mult <= 1.5  # 淡出过程中会降低
        
        return True
    
    def test_singleton(self, pygame_init):
        """测试单例模式"""
        s1 = get_power_surge()
        s2 = get_power_surge()
        assert s1 is s2
        return True
    
    def test_particle_movement(self, pygame_init):
        """测试粒子运动"""
        surge = PowerSurge()
        surge.activate(400, 300, 200)
        
        initial_distances = [p.distance for p in surge.particles]
        
        surge.update(0.5)
        
        for i, p in enumerate(surge.particles):
            assert p.distance >= initial_distances[i]
        
        return True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
