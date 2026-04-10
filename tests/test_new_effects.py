"""
保卫萝卜 - 新特效系统测试
"""
import sys
sys.path.insert(0, 'src')

import pytest
from base_effects import ShieldEffect, TowerIdleParticles, get_base_effect_manager


class TestShieldEffect:
    """护盾环绕特效测试"""
    
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
        
    def test_shield_effect_deactivation(self):
        """测试护盾特效过期"""
        effect = ShieldEffect(100, 100, duration=15)
        effect.update(20)
        assert effect.active is False
        
    def test_shield_effect_draw(self):
        """测试护盾特效绘制(不崩溃)"""
        effect = ShieldEffect(100, 100)
        import pygame
        pygame.init()
        screen = pygame.Surface((200, 200))
        effect.draw(screen)  # 不应崩溃


class TestTowerIdleParticles:
    """塔空闲粒子特效测试"""
    
    def test_idle_particles_init(self):
        """测试空闲粒子初始化"""
        effect = TowerIdleParticles(100, 100, (255, 255, 200), 5)
        assert effect.x == 100
        assert effect.y == 100
        assert effect.max_life == 120
        assert len(effect.particles) == 5
        
    def test_idle_particles_update(self):
        """测试空闲粒子更新"""
        effect = TowerIdleParticles(100, 100, (255, 255, 200), 3)
        initial_y = effect.particles[0]['y']
        effect.update(10)
        assert effect.particles[0]['y'] <= initial_y  # 向上漂浮
        
    def test_idle_particles_lifecycle(self):
        """测试粒子生命周期"""
        effect = TowerIdleParticles(100, 100, (255, 255, 200), 3)
        effect.update(130)
        assert effect.active is False


class TestBaseEffectManager:
    """塔基特效管理器测试"""
    
    def test_manager_add_shield(self):
        """测试添加护盾特效"""
        manager = get_base_effect_manager()
        manager.add_shield_effect(100, 100, (100, 150, 255))
        assert len(manager.effects) >= 1
        
    def test_manager_add_idle_particles(self):
        """测试添加空闲粒子特效"""
        manager = get_base_effect_manager()
        initial_count = len(manager.effects)
        manager.add_idle_particles(100, 100)
        assert len(manager.effects) > initial_count
        
    def test_manager_update(self):
        """测试管理器更新"""
        manager = get_base_effect_manager()
        manager.add_shield_effect(100, 100)
        manager.add_idle_particles(150, 150)
        manager.update(10)
        # 验证更新不崩溃
        assert True