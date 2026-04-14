"""
测试 - 破碎与涟漪特效系统
Test - Shatter and Ripple Effect System
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
    pytest.skip("pygame not available", allow_module_level=True)

from shatter_effect import ShatterParticle, ShatterEffect, RippleEffect, RippleManager


class TestShatterParticle:
    """测试破碎粒子"""
    
    def test_particle_creation(self):
        """测试粒子创建"""
        particle = ShatterParticle(100, 100, (100, 200, 255), 8, (50, -50), 90)
        assert particle.x == 100
        assert particle.y == 100
        assert particle.color == (100, 200, 255)
        assert particle.life == 1.0
    
    def test_particle_update(self):
        """测试粒子更新"""
        particle = ShatterParticle(100, 100, (100, 200, 255), 8, (50, -50), 90)
        result = particle.update(0.1)
        assert result is True
        assert particle.life < 1.0
        assert particle.x != 100 or particle.y != 100  # 位置已更新
    
    def test_particle_death(self):
        """测试粒子死亡"""
        particle = ShatterParticle(100, 100, (100, 200, 255), 8, (50, -50), 180)
        for _ in range(100):
            if not particle.update(0.05):
                break
        assert particle.life <= 0


class TestShatterEffect:
    """测试破碎特效管理器"""
    
    def test_create_shatter(self):
        """测试创建破碎特效"""
        effect = ShatterEffect()
        effect.create_shatter(100, 100, (100, 200, 255), 10)
        assert len(effect.particles) == 10
    
    def test_update(self):
        """测试更新"""
        effect = ShatterEffect()
        effect.create_shatter(100, 100, (255, 100, 100), 5)
        effect.update(0.1)
        assert len(effect.particles) <= 5
    
    def test_clear(self):
        """测试清除"""
        effect = ShatterEffect()
        effect.create_shatter(100, 100, (100, 255, 100), 5)
        effect.clear()
        assert len(effect.particles) == 0


class TestRippleEffect:
    """测试涟漪特效"""
    
    def test_ripple_creation(self):
        """测试涟漪创建"""
        ripple = RippleEffect(100, 100, 50, (255, 255, 255))
        assert ripple.x == 100
        assert ripple.y == 100
        assert ripple.radius == 5
    
    def test_ripple_expansion(self):
        """测试涟漪扩展"""
        ripple = RippleEffect(100, 100, 100, (255, 255, 255))
        initial_radius = ripple.radius
        ripple.update(0.1)
        assert ripple.radius > initial_radius
    
    def test_ripple_life(self):
        """测试涟漪生命周期"""
        ripple = RippleEffect(100, 100, 50, (255, 255, 255))
        for _ in range(10):
            ripple.update(0.1)
        assert ripple.life < 1.0


class TestRippleManager:
    """测试涟漪管理器"""
    
    def test_add_ripple(self):
        """测试添加涟漪"""
        manager = RippleManager()
        manager.add_ripple(100, 100, 50)
        assert len(manager.ripples) == 1
    
    def test_multiple_ripples(self):
        """测试多个涟漪"""
        manager = RippleManager()
        manager.add_ripple(100, 100, 50)
        manager.add_ripple(200, 200, 80)
        assert len(manager.ripples) == 2
    
    def test_clear_ripples(self):
        """测试清除涟漪"""
        manager = RippleManager()
        manager.add_ripple(100, 100, 50)
        manager.add_ripple(200, 200, 80)
        manager.clear()
        assert len(manager.ripples) == 0


class TestShatterShapes:
    """测试不同形状"""
    
    def test_different_shapes(self):
        """测试不同形状粒子"""
        for shape in ['triangle', 'diamond', 'shard']:
            particle = ShatterParticle(100, 100, (100, 200, 255), 8, (50, -50), 90)
            particle.shape = shape
            assert particle.shape == shape


class TestShatterIntegration:
    """集成测试"""
    
    def test_full_cycle(self):
        """测试完整生命周期"""
        effect = ShatterEffect()
        effect.create_shatter(400, 300, (255, 200, 100), 20)
        
        # 模拟多帧更新
        for _ in range(200):
            effect.update(0.016)
        
        # 粒子应该全部消失
        assert len(effect.particles) == 0
    
    def test_ripple_fade(self):
        """测试涟漪淡出"""
        manager = RippleManager()
        manager.add_ripple(400, 300, 30)
        
        # 模拟多帧
        for _ in range(100):
            manager.update(0.016)
        
        # 涟漪应该消失
        assert len(manager.ripples) == 0